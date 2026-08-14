"""
src/evaluation/run_simulation.py
---------------------------------
Objectives 3 and 4 — Full simulation with CORRECT ground-truth evaluation.

KEY DESIGN:
  Routing decision  → each method uses its own information
                       (GRU predictions / current speeds / historical avg / oracle)
  Journey simulation → ALL methods are simulated using ACTUAL future speeds
                       from the METR-LA test set (ground truth)

This ensures that if GRU correctly predicts congestion and routes around it,
the framework genuinely arrives faster than a reactive baseline that drove
into that congestion.

Run from project root:
    python src/evaluation/run_simulation.py
"""

import os, sys, time, random, heapq, math, warnings, pickle
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, ".")

# ── CONFIG ────────────────────────────────────────────────────────────────────
MODEL_DIR     = os.path.join("models", "saved")
PROCESSED_DIR = os.path.join("data", "processed")
RESULTS_DIR   = os.path.join("results", "simulation")
VIZ_DIR       = os.path.join("visualizations")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(VIZ_DIR, exist_ok=True)

N_SENSORS    = 207
N_OD_PAIRS   = 75
DELTA_VALUES = [0.05, 0.10, 0.15, 0.20]
SCENARIOS    = ["peak_hour", "off_peak", "incident"]
SEQUENCE_LEN = 12
N_FUTURE     = 6
HIDDEN       = 64
DROPOUT      = 0.2
FREE_FLOW    = 13.4   # m/s ≈ 30 mph
RANDOM_SEED  = 42


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: LOAD MODEL
# ═══════════════════════════════════════════════════════════════════════════════

def _make_5layer():
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import GRU, Dropout, Dense
    m = Sequential()
    m.add(GRU(HIDDEN, return_sequences=True, input_shape=(SEQUENCE_LEN, N_SENSORS)))
    m.add(Dropout(DROPOUT))
    m.add(GRU(HIDDEN, return_sequences=False))
    m.add(Dropout(DROPOUT))
    m.add(Dense(N_FUTURE * N_SENSORS))
    return m


def _make_3layer():
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import GRU, Dense, Input
    return Sequential([
        Input(shape=(SEQUENCE_LEN, N_SENSORS)),
        GRU(HIDDEN, return_sequences=True),
        GRU(HIDDEN, return_sequences=False),
        Dense(N_FUTURE * N_SENSORS),
    ])


def load_model():
    import tensorflow as tf
    dummy = np.zeros((1, SEQUENCE_LEN, N_SENSORS), dtype=np.float32)
    for fname, builder in [
        ("gru_improved_best.h5", _make_5layer),
        ("gru_best.h5",          _make_3layer),
    ]:
        path = os.path.join(MODEL_DIR, fname)
        if not os.path.exists(path):
            continue
        try:
            m = tf.keras.models.load_model(path, compile=False)
            m.predict(dummy, verbose=0)
            print(f"  [OK] Loaded directly: {fname}")
            return m
        except Exception:
            pass
        try:
            m = builder()
            m.predict(dummy, verbose=0)
            m.load_weights(path)
            m.predict(dummy, verbose=0)
            print(f"  [OK] Loaded weights: {fname}")
            return m
        except Exception as e:
            print(f"  [WARN] {fname}: {e}")
    raise RuntimeError("No GRU model found in models/saved/")


def load_scaler():
    for p in [os.path.join(PROCESSED_DIR, "scaler.pkl"),
              os.path.join(MODEL_DIR, "scaler.pkl")]:
        if os.path.exists(p):
            with open(p, "rb") as f:
                return pickle.load(f)
    raise FileNotFoundError("scaler.pkl not found")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: LOAD ROAD NETWORK
# ═══════════════════════════════════════════════════════════════════════════════

def load_graph():
    import networkx as nx
    net = os.path.join(PROCESSED_DIR, "la_road_network.pkl")
    esm = os.path.join(PROCESSED_DIR, "edge_sensor_mapping.pkl")
    if os.path.exists(net) and os.path.exists(esm):
        with open(net, "rb") as f:
            G = pickle.load(f)
        with open(esm, "rb") as f:
            raw = pickle.load(f)
        edge_sensor_map = {}
        for k, v in raw.items():
            if isinstance(k, (list, tuple)) and len(k) >= 2:
                edge_sensor_map[(k[0], k[1])] = v
            else:
                edge_sensor_map[k] = v
        edge_lengths = {(u, v): float(d.get("length", 500.0))
                        for u, v, d in G.edges(data=True)}
        print(f"  [OK] Graph: {G.number_of_nodes()} nodes, "
              f"{G.number_of_edges()} edges, "
              f"{len(edge_sensor_map)} sensor-mapped")
        return G, edge_sensor_map, edge_lengths
    raise FileNotFoundError("Road network not found in data/processed/")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: LOAD TEST DATA WITH GROUND TRUTH FUTURE SPEEDS
# ═══════════════════════════════════════════════════════════════════════════════

def load_test_data(scaler):
    """
    Returns:
      X_test_mph  : (T, N_SENSORS) — input window speeds in mph (current + past)
      y_test_mph  : (T, N_FUTURE, N_SENSORS) — ACTUAL future speeds in mph
      speed_hist  : (T_full, N_SENSORS) — full history for hist avg baseline
    """
    npz = os.path.join(PROCESSED_DIR, "training_data.npz")
    d = np.load(npz)

    # Ground truth future speeds — inverse scale y_test
    y_test_scaled = d["y_test"]                             # (T, N_FUTURE, N_SENSORS)
    T, NF, NS = y_test_scaled.shape
    y_test_mph = scaler.inverse_transform(
        y_test_scaled.reshape(-1, 1)
    ).reshape(T, NF, NS).astype(np.float32)
    y_test_mph = np.clip(y_test_mph, 1.0, None)

    # Current window — last step of X_test as current speed
    X_test_scaled = d["X_test"]                             # (T, SEQUENCE_LEN, N_SENSORS)
    X_last = scaler.inverse_transform(
        X_test_scaled[:, -1, :].reshape(-1, 1)
    ).reshape(T, NS).astype(np.float32)
    X_last = np.clip(X_last, 1.0, None)

    # Full input window for GRU (scaled)
    X_test_seq = X_test_scaled                              # (T, 12, N_SENSORS)

    # Historical averages from training set
    X_train_scaled = d["X_train"]                           # (Tr, 12, N_SENSORS)
    hist_mph = scaler.inverse_transform(
        X_train_scaled.reshape(-1, 1)
    ).reshape(X_train_scaled.shape).mean(axis=0).mean(axis=0)  # (N_SENSORS,)
    hist_mph = np.clip(hist_mph, 1.0, None)

    print(f"  [OK] Test windows: {T}  |  Ground truth future: {y_test_mph.shape}")
    return X_test_seq, X_last, y_test_mph, hist_mph


# ═══════════════════════════════════════════════════════════════════════════════
# GRU PREDICTION
# ═══════════════════════════════════════════════════════════════════════════════

def gru_predict_mph(model, scaler, X_window_scaled):
    """
    X_window_scaled: (SEQUENCE_LEN, N_SENSORS) — scaled input window
    Returns: (N_FUTURE, N_SENSORS) — predicted speeds in mph
    """
    X = X_window_scaled.reshape(1, SEQUENCE_LEN, N_SENSORS)  # (1, 12, 207)
    raw = model.predict(X, verbose=0)                         # (1, N_FUTURE*207)
    pred_mph = scaler.inverse_transform(
        raw.reshape(-1, 1)
    ).reshape(N_FUTURE, N_SENSORS)
    return np.clip(pred_mph, 1.0, None)


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVEL TIME FUNCTIONS FOR ROUTING DECISIONS
# ═══════════════════════════════════════════════════════════════════════════════

def speeds_to_edge_tt(speeds_mph, edge_sensor_map, edge_lengths):
    """
    speeds_mph: either (N_SENSORS,) for scalar or (N_FUTURE, N_SENSORS) for array
    Returns: dict {(u,v): travel_time_or_array_of_times}
    """
    tt = {}
    for e, s in edge_sensor_map.items():
        s = int(s[0]) if isinstance(s, (list, tuple)) else int(s)
        if s >= N_SENSORS:
            continue
        length = edge_lengths.get(e, 500.0)
        if speeds_mph.ndim == 1:
            tt[e] = length / (speeds_mph[s] * 0.44704)
        else:
            tt[e] = length / (speeds_mph[:, s] * 0.44704)   # (N_FUTURE,)
    return tt


def free_flow_tt(edge_lengths):
    return {e: l / FREE_FLOW for e, l in edge_lengths.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTING: TD-A*
# ═══════════════════════════════════════════════════════════════════════════════

def heuristic(G, n, goal):
    try:
        d1, d2 = G.nodes[n], G.nodes[goal]
        R = 6_371_000
        p1, p2 = math.radians(d1["y"]), math.radians(d2["y"])
        dp = math.radians(d2["y"] - d1["y"])
        dl = math.radians(d2["x"] - d1["x"])
        a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2*R*math.asin(math.sqrt(a)) / FREE_FLOW
    except Exception:
        return 0.0


def get_tt(tt_dict, ff, u, v, elapsed=0.0):
    e = (u, v)
    val = tt_dict.get(e, ff.get(e, 300.0))
    if hasattr(val, "__len__"):
        slot = min(int(elapsed // 300), len(val)-1)
        return max(float(val[slot]), 1.0)
    return max(float(val), 1.0)


def astar_route(G, origin, dest, tt_dict, ff):
    """Returns path (list of nodes) found by A*."""
    t0 = time.perf_counter()
    g_sc = {origin: 0.0}
    prev = {origin: None}
    heap = [(heuristic(G, origin, dest), 0.0, origin)]
    while heap:
        _, g, u = heapq.heappop(heap)
        if g > g_sc.get(u, math.inf) + 1e-9:
            continue
        if u == dest:
            path, node = [], dest
            while node is not None:
                path.append(node); node = prev[node]
            path.reverse()
            lat = (time.perf_counter() - t0) * 1000
            return path, lat
        for v in G.successors(u):
            ng = g + get_tt(tt_dict, ff, u, v, g)
            if ng < g_sc.get(v, math.inf):
                g_sc[v] = ng; prev[v] = u
                heapq.heappush(heap, (ng + heuristic(G, v, dest), ng, v))
    return [origin], (time.perf_counter() - t0) * 1000


# ═══════════════════════════════════════════════════════════════════════════════
# JOURNEY SIMULATION WITH GROUND TRUTH SPEEDS
# This is the key function that makes results meaningful.
# All routing methods are evaluated using ACTUAL future speeds.
# ═══════════════════════════════════════════════════════════════════════════════

def simulate_path(path, actual_mph, edge_sensor_map, edge_lengths):
    """
    Simulate traversal of a pre-computed path using ACTUAL future speeds.

    path       : list of node IDs (from routing algorithm)
    actual_mph : (N_FUTURE, N_SENSORS) — actual observed future speeds
    Returns    : actual journey time in seconds
    """
    elapsed = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        slot = min(int(elapsed // 300), N_FUTURE - 1)
        sensor = edge_sensor_map.get((u, v))
        if sensor is not None:
            s_idx = int(sensor[0]) if isinstance(sensor, (list, tuple)) else int(sensor)
            if s_idx < N_SENSORS:
                spd_mph = max(float(actual_mph[slot, s_idx]), 1.0)
            else:
                spd_mph = FREE_FLOW * 2.237
        else:
            spd_mph = FREE_FLOW * 2.237
        spd_mps = spd_mph * 0.44704
        elapsed += edge_lengths.get((u, v), 500.0) / spd_mps
    return elapsed


# ═══════════════════════════════════════════════════════════════════════════════
# ADAPTIVE REPLANNING CONTROLLER (for Framework + Objective 3)
# ═══════════════════════════════════════════════════════════════════════════════

def simulate_with_replanning(G, origin, dest, model, scaler,
                              X_test_seq, t_idx, actual_mph, edge_sensor_map,
                              edge_lengths, ff, delta):
    X_seq_t = X_test_seq[t_idx]
    """
    Framework journey simulation with adaptive replanning.

    - Routes initially using GRU predictions.
    - After each edge, checks if updated GRU prediction diverges from
      current expected remaining time by more than delta.
    - If yes, recomputes route using updated predictions.
    - Journey time computed using actual_mph (ground truth) throughout.
    """
    # Initial route using GRU predictions
    pred_mph = gru_predict_mph(model, scaler, X_seq_t)
    pred_tt  = speeds_to_edge_tt(pred_mph, edge_sensor_map, edge_lengths)

    path, lat = astar_route(G, origin, dest, pred_tt, ff)
    lats = [lat]
    elapsed = 0.0
    current = origin
    n_rep = 0

    while current != dest:
        if len(path) < 2:
            break

        nxt = path[1]
        slot = min(int(elapsed // 300), N_FUTURE - 1)
        sensor = edge_sensor_map.get((current, nxt))
        if sensor is not None:
            s_idx = int(sensor[0]) if isinstance(sensor, (list, tuple)) else int(sensor)
            if s_idx < N_SENSORS:
                spd_mph = max(float(actual_mph[slot, s_idx]), 1.0)
            else:
                spd_mph = FREE_FLOW * 2.237
        else:
            spd_mph = FREE_FLOW * 2.237
        spd_mps = spd_mph * 0.44704
        elapsed += edge_lengths.get((current, nxt), 500.0) / spd_mps
        current = nxt
        path.pop(0)

        if current == dest:
            break

        # Estimate remaining time under current plan
        _, T_check_lat = astar_route(G, current, dest, pred_tt, ff)
        T_old = sum(
            get_tt(pred_tt, ff, path[i], path[i+1], elapsed)
            for i in range(len(path)-1)
        ) if len(path) > 1 else 0.0

        # Refresh GRU prediction (in practice would advance window;
        # here we re-use same window to simulate a stable horizon)
        slots_passed = min(int(elapsed // 300), len(X_test_seq) - t_idx - 1)
        X_seq_new = X_test_seq[t_idx + slots_passed]
        pred_mph_new = gru_predict_mph(model, scaler, X_seq_new)
        pred_tt_new  = speeds_to_edge_tt(pred_mph_new, edge_sensor_map, edge_lengths)

        _, T_new_lat = astar_route(G, current, dest, pred_tt_new, ff)
        T_new = sum(
            get_tt(pred_tt_new, ff, path[i], path[i+1], elapsed)
            for i in range(len(path)-1)
        ) if len(path) > 1 else 0.0

        if T_old > 0 and abs(T_new - T_old) / T_old > delta:
            new_path, replan_lat = astar_route(
                G, current, dest, pred_tt_new, ff)
            lats.append(replan_lat)
            n_rep += 1
            pred_tt = pred_tt_new
            path = new_path

    return elapsed, n_rep, float(np.mean(lats))


# ═══════════════════════════════════════════════════════════════════════════════
# OD PAIR GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def make_od_pairs(G):
    import networkx as nx
    rng = random.Random(RANDOM_SEED)
    nodes = list(G.nodes())
    pairs = []
    attempts = 0
    while len(pairs) < N_OD_PAIRS and attempts < N_OD_PAIRS * 30:
        o, d = rng.choice(nodes), rng.choice(nodes)
        attempts += 1
        if o == d:
            continue
        try:
            if nx.shortest_path_length(G, o, d) >= 3:
                pairs.append((o, d))
        except Exception:
            pass
    print(f"  [OK] Generated {len(pairs)} OD pairs")
    return pairs


def pick_test_indices(y_test_mph, scenario, n=5):
    """
    Select time indices from test set representing each scenario.
    peak_hour:  windows where mean actual future speed is lowest 25th pct
    off_peak:   windows where mean actual future speed is highest 25th pct
    incident:   random windows where we synthetically inject a speed drop
    """
    mean_speed = y_test_mph.mean(axis=(1, 2))   # (T,) mean over steps and sensors
    if scenario == "peak_hour":
        cands = np.where(mean_speed <= np.percentile(mean_speed, 25))[0]
    elif scenario == "off_peak":
        cands = np.where(mean_speed >= np.percentile(mean_speed, 75))[0]
    else:
        cands = np.arange(len(mean_speed))

    rng = np.random.default_rng(RANDOM_SEED)
    return rng.choice(cands, size=min(n, len(cands)), replace=False).tolist()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXPERIMENT LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def run_experiments(model, scaler, G, esm, el,
                    X_test_seq, X_last, y_test_mph, hist_mph):
    total = N_OD_PAIRS * len(SCENARIOS) * len(DELTA_VALUES)
    print(f"\n  {N_OD_PAIRS} OD pairs × {len(SCENARIOS)} scenarios × "
          f"{len(DELTA_VALUES)} delta values = {total} runs\n")

    ff = free_flow_tt(el)
    pairs = make_od_pairs(G)
    hist_tt = speeds_to_edge_tt(hist_mph, esm, el)

    rng  = np.random.default_rng(RANDOM_SEED)
    rows = []
    count = 0

    for scenario in SCENARIOS:
        test_indices = pick_test_indices(y_test_mph, scenario)

        for origin, dest in pairs:
            t_idx = int(rng.choice(test_indices))

            # Ground truth future speeds for this window
            actual = y_test_mph[t_idx]                           # (N_FUTURE, 207)

            # Inject incident for incident scenario
            if scenario == "incident":
                actual = actual.copy()
                n_aff = max(1, int(N_SENSORS * 0.15))
                aff = rng.choice(N_SENSORS, n_aff, replace=False)
                # Speed drop midway through the journey
                actual[N_FUTURE//2:, aff] *= 0.4

            # Current speeds (last observed) for reactive baselines
            curr_mph = X_last[t_idx]                             # (207,)
            curr_tt  = speeds_to_edge_tt(curr_mph, esm, el)

            # Oracle travel times (actual future - perfect knowledge)
            oracle_tt = speeds_to_edge_tt(actual, esm, el)

            # GRU predictions
            t_gru = time.perf_counter()
            pred_mph = gru_predict_mph(model, scaler, X_test_seq[t_idx])
            gru_ms   = (time.perf_counter() - t_gru) * 1000
            pred_tt  = speeds_to_edge_tt(pred_mph, esm, el)

            # ── ROUTING DECISIONS (each method chooses its own path) ──────
            t_r = time.perf_counter()
            b1_path, b1_lat = astar_route(G, origin, dest, curr_tt,  ff)  # B1 Dijkstra
            b2_path, b2_lat = astar_route(G, origin, dest, hist_tt,  ff)  # B2 Static
            b3_path, b3_lat = astar_route(G, origin, dest, curr_tt,  ff)  # B3 Reactive
            b4_path, b4_lat = astar_route(G, origin, dest, oracle_tt, ff) # B4 Oracle

            # ── JOURNEY SIMULATION WITH ACTUAL SPEEDS ────────────────────
            # All paths traversed under ground truth — this is the fair comparison
            b1_tt = simulate_path(b1_path, actual, esm, el)
            b2_tt = simulate_path(b2_path, actual, esm, el)
            b3_tt = simulate_path(b3_path, actual, esm, el)
            b4_tt = simulate_path(b4_path, actual, esm, el)

            # ── FRAMEWORK (GRU-predicted routing + actual speed simulation) ──
            for delta in DELTA_VALUES:
                count += 1
                if count % 100 == 0:
                    print(f"  Progress: {count}/{total} "
                          f"({count*100//total}%)", flush=True)
                try:
                    fw_tt, n_rep, fw_lat = simulate_with_replanning(
                        G, origin, dest, model, scaler,
                        X_test_seq, t_idx, actual, esm, el, ff, delta)

                    def red(base):
                        if base > 0 and fw_tt < math.inf and fw_tt > 0:
                            return (base - fw_tt) / base * 100
                        return 0.0

                    rows.append({
                        "scenario":       scenario,
                        "delta":          delta,
                        "gru_ms":         gru_ms,
                        "b1_tt_s":        b1_tt,
                        "b2_tt_s":        b2_tt,
                        "b3_tt_s":        b3_tt,
                        "b4_tt_s":        b4_tt,
                        "fw_tt_s":        fw_tt,
                        "fw_lat_ms":      fw_lat,
                        "n_replannings":  n_rep,
                        "red_vs_b1":      red(b1_tt),
                        "red_vs_b2":      red(b2_tt),
                        "red_vs_b3":      red(b3_tt),
                        "red_vs_b4":      red(b4_tt),
                    })
                except Exception as e:
                    print(f"  [WARN] ({origin},{dest}) δ={delta}: {e}")

    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def analyse(df):
    print("\n" + "="*65)
    print("OBJECTIVE 4 — FRAMEWORK vs BASELINES")
    print("="*65)
    for col, label in [
        ("red_vs_b1", "vs Dijkstra/Current (B1)"),
        ("red_vs_b2", "vs Static A* (B2)       "),
        ("red_vs_b3", "vs Reactive A* (B3)     "),
        ("red_vs_b4", "vs Oracle A* (B4)       "),
    ]:
        m, s = df[col].mean(), df[col].std()
        med  = df[col].median()
        print(f"  {label}  mean: {m:+.2f}%  SD: {s:.2f}%  median: {med:.2f}%")

    print(f"\n  Avg TD-A* latency:       {df['fw_lat_ms'].mean():.3f} ms")
    print(f"  Avg GRU inference:       {df['gru_ms'].mean():.1f} ms")
    print(f"  Avg replannings/journey: {df['n_replannings'].mean():.2f}")

    print("\n" + "="*65)
    print("OBJECTIVE 3 — THRESHOLD (delta) SENSITIVITY")
    print("="*65)
    g = df.groupby("delta")[
        ["red_vs_b1", "n_replannings", "fw_lat_ms"]
    ].mean().round(3)
    g.columns = [
        "Mean Reduction vs B1 (%)", "Avg Replannings", "Avg Latency (ms)"]
    print(g.to_string())

    try:
        from scipy import stats
        groups = [df[df["delta"] == d]["red_vs_b1"].values
                  for d in DELTA_VALUES]
        if all(len(g) > 1 and g.std() > 1e-9 for g in groups):
            F, p = stats.f_oneway(*groups)
            print(f"\n  ANOVA: F={F:.3f}  p={p:.3f}")
            if p > 0.05:
                best = df.groupby("delta")["red_vs_b1"].mean().idxmax()
                print(f"  → No significant effect (p>0.05). "
                      f"Recommended delta = {best} "
                      f"(best reduction, fewest replannings)")
            else:
                best = df.groupby("delta")["red_vs_b1"].mean().idxmax()
                print(f"  → Significant effect (p={p:.3f}). Best delta = {best}")
        else:
            print("  ANOVA skipped — insufficient variance in groups.")
    except ImportError:
        print("  Install scipy for ANOVA: pip install scipy")

    print("\n" + "="*65)
    print("BREAKDOWN BY SCENARIO")
    print("="*65)
    scn = df.groupby("scenario")[
        ["red_vs_b1", "red_vs_b4", "n_replannings"]
    ].mean().round(2)
    scn.columns = ["Reduction vs B1 (%)", "Reduction vs Oracle (%)", "Replannings"]
    print(scn.to_string())

    # Statistical significance
    print("\n" + "="*65)
    print("STATISTICAL SIGNIFICANCE (paired t-test vs B1)")
    print("="*65)
    try:
        from scipy import stats as st
        for scenario in SCENARIOS:
            sub = df[df["scenario"] == scenario]
            if len(sub) < 2:
                continue
            t_stat, p_val = st.ttest_1samp(sub["red_vs_b1"], 0)
            sig = "Yes" if p_val < 0.05 else "No"
            print(f"  {scenario:<12}  "
                  f"mean={sub['red_vs_b1'].mean():.2f}%  "
                  f"t={t_stat:.2f}  p={p_val:.4f}  sig={sig}")
    except Exception as e:
        print(f"  t-test skipped: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# VISUALISATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def visualise(df):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    NAVY, TEAL, GOLD, RED = "#1E2761", "#0D9488", "#E8A838", "#C0392B"

    # ── Chart 1: Travel time reduction by scenario ────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 5))
    scens = df["scenario"].unique()
    baselines = [
        ("red_vs_b1", "Dijkstra/Current", NAVY),
        ("red_vs_b2", "Static A*",        TEAL),
        ("red_vs_b3", "Reactive A*",       GOLD),
        ("red_vs_b4", "Oracle A*",         RED),
    ]
    x = np.arange(len(scens)); w = 0.18
    for i, (col, lbl, col_c) in enumerate(baselines):
        vals = [df[df["scenario"]==s][col].mean() for s in scens]
        errs = [df[df["scenario"]==s][col].std() for s in scens]
        ax.bar(x+i*w, vals, w, label=lbl, color=col_c, alpha=0.85)
        ax.errorbar(x+i*w, vals, yerr=errs, fmt='none',
                    color='black', capsize=3, linewidth=1)
    ax.set_xticks(x+w*1.5)
    ax.set_xticklabels([s.replace("_", " ").title() for s in scens])
    ax.set_ylabel("Travel Time Reduction (%)"); ax.legend()
    ax.set_title(
        "Objective 4 — Framework Travel Time Reduction vs Baselines by Scenario",
        fontweight="bold")
    ax.axhline(15, color="black", lw=1, ls="--",
               label="15% minimum target", alpha=0.5)
    ax.grid(axis="y", alpha=0.3); ax.set_facecolor("#F4F7FF")
    plt.tight_layout()
    p = os.path.join(VIZ_DIR, "obj4_travel_time_reduction.png")
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[OK] {p}")

    # ── Chart 2: Delta sensitivity ────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Objective 3 — Threshold (δ) Sensitivity Analysis",
                 fontweight="bold", fontsize=13)
    g = df.groupby("delta")
    d_labels = [str(d) for d in DELTA_VALUES]

    ax = axes[0]
    means = [g.get_group(d)["red_vs_b1"].mean() for d in DELTA_VALUES]
    stds  = [g.get_group(d)["red_vs_b1"].std()  for d in DELTA_VALUES]
    ax.bar(d_labels, means, yerr=stds, color=NAVY, alpha=0.8,
           error_kw={"capsize": 5})
    ax.set_xlabel("Threshold δ"); ax.set_ylabel("Mean Reduction vs B1 (%)")
    ax.set_title("Route Quality by δ"); ax.grid(axis="y", alpha=0.3)
    ax.set_facecolor("#F4F7FF")

    ax = axes[1]
    reps = [g.get_group(d)["n_replannings"].mean() for d in DELTA_VALUES]
    ax.bar(d_labels, reps, color=TEAL, alpha=0.8)
    ax.set_xlabel("Threshold δ"); ax.set_ylabel("Avg Replannings per Journey")
    ax.set_title("Update Frequency by δ"); ax.grid(axis="y", alpha=0.3)
    ax.set_facecolor("#F4F7FF")
    plt.tight_layout()
    p = os.path.join(VIZ_DIR, "obj3_delta_sensitivity.png")
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[OK] {p}")

    # ── Chart 3: Latency distribution ─────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(df["fw_lat_ms"], bins=30, color=NAVY, alpha=0.8, edgecolor="white")
    ml = df["fw_lat_ms"].mean()
    ax.axvline(ml, color=GOLD, lw=2, label=f"Mean: {ml:.3f} ms")
    ax.axvline(1000, color=RED, lw=1.5, ls="--", label="1,000 ms target")
    ax.set_xlabel("Routing Latency (ms)"); ax.set_ylabel("Frequency")
    ax.set_title("Objective 4 — TD-A* Routing Latency Distribution",
                 fontweight="bold")
    ax.legend(); ax.grid(alpha=0.3); ax.set_facecolor("#F4F7FF")
    plt.tight_layout()
    p = os.path.join(VIZ_DIR, "obj4_latency_distribution.png")
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[OK] {p}")

    # ── Chart 4: GRU predicted vs actual speeds (sample) ─────────────────────
    # (requires access to a sample window — shows prediction quality)
    print("  [INFO] Charts 1-3 saved. Run cross_validate.py for prediction plots.")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("="*65)
    print("OBJECTIVES 3 & 4 — FULL SIMULATION (CORRECTED)")
    print("Ground truth evaluation: all paths simulated with actual speeds")
    print("="*65)

    print("\n[Phase 1] Loading GRU model...")
    model = load_model()
    scaler = load_scaler()

    print("\n[Phase 2] Loading road network...")
    G, esm, el = load_graph()

    print("\n[Phase 3] Loading test data with ground truth future speeds...")
    X_test_seq, X_last, y_test_mph, hist_mph = load_test_data(scaler)

    print("\n[Phase 4] Running experiments...")
    df = run_experiments(model, scaler, G, esm, el,
                         X_test_seq, X_last, y_test_mph, hist_mph)

    raw = os.path.join(RESULTS_DIR, "simulation_results.csv")
    df.to_csv(raw, index=False)
    print(f"\n[OK] Raw results → {raw}  ({len(df)} records)")

    analyse(df)

    print("\n[Phase 5] Saving visualisations...")
    visualise(df)

    summ = df.groupby(["scenario", "delta"])[[
        "fw_tt_s", "b1_tt_s",
        "red_vs_b1", "red_vs_b2", "red_vs_b4",
        "fw_lat_ms", "n_replannings", "gru_ms"
    ]].agg(["mean", "std"]).round(3)
    sp = os.path.join(RESULTS_DIR, "summary_statistics.csv")
    summ.to_csv(sp)
    print(f"[OK] Summary → {sp}")

    print("\n" + "="*65)
    print("DONE")
    print(f"  Results:        {RESULTS_DIR}/")
    print(f"  Visualisations: {VIZ_DIR}/")
    print("="*65)


if __name__ == "__main__":
    main()