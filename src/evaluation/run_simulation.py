"""
src/evaluation/run_simulation.py
---------------------------------
Objectives 3 and 4 — Full simulation evaluation.

Objective 3: Optimal replanning threshold delta in {5%, 10%, 15%, 20%}
Objective 4: Framework vs Dijkstra, Static A*, Reactive A*, Oracle A*

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
FREE_FLOW    = 13.4   # m/s (~30 mph)
RANDOM_SEED  = 42


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: LOAD MODEL
# Two possible architectures depending on which .h5 file loads successfully.
# gru_improved_best.h5 → 5 layers (GRU + Dropout + GRU + Dropout + Dense)
# gru_best.h5          → 3 layers (GRU + GRU + Dense)
# Both expect input shape (1, SEQUENCE_LEN, N_SENSORS) = (1, 12, 207)
# ═══════════════════════════════════════════════════════════════════════════════

def _make_5layer():
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import GRU, Dropout, Dense, Input
    m = Sequential([
        Input(shape=(SEQUENCE_LEN, N_SENSORS)),
        GRU(HIDDEN, return_sequences=True),
        Dropout(DROPOUT),
        GRU(HIDDEN, return_sequences=False),
        Dropout(DROPOUT),
        Dense(N_FUTURE * N_SENSORS),
    ])
    return m


def _make_3layer():
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import GRU, Dense, Input
    m = Sequential([
        Input(shape=(SEQUENCE_LEN, N_SENSORS)),
        GRU(HIDDEN, return_sequences=True),
        GRU(HIDDEN, return_sequences=False),
        Dense(N_FUTURE * N_SENSORS),
    ])
    return m


def load_model():
    import tensorflow as tf
    dummy = np.zeros((1, SEQUENCE_LEN, N_SENSORS), dtype=np.float32)

    candidates = [
        ("gru_improved_best.h5", _make_5layer),
        ("gru_best.h5",          _make_3layer),
    ]

    for fname, builder in candidates:
        path = os.path.join(MODEL_DIR, fname)
        if not os.path.exists(path):
            continue

        # Try 1: direct keras load
        try:
            m = tf.keras.models.load_model(path, compile=False)
            m.predict(dummy, verbose=0)   # confirm it runs
            print(f"  [OK] Loaded: {fname}")
            return m
        except Exception:
            pass

        # Try 2: rebuild architecture then load weights
        try:
            m = builder()
            m.predict(dummy, verbose=0)   # build weights
            m.load_weights(path)
            m.predict(dummy, verbose=0)   # confirm weights work
            print(f"  [OK] Loaded weights into fresh model: {fname}")
            return m
        except Exception as e:
            print(f"  [WARN] {fname}: {e}")

    raise RuntimeError(
        "Could not load any GRU model from models/saved/.\n"
        "Expected: gru_improved_best.h5 or gru_best.h5"
    )


def load_scaler():
    for p in [os.path.join(PROCESSED_DIR, "scaler.pkl"),
              os.path.join(MODEL_DIR,     "scaler.pkl")]:
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
            raw_esm = pickle.load(f)

        # Normalise keys to (u, v) tuples
        edge_sensor_map = {}
        for k, v in raw_esm.items():
            if isinstance(k, (list, tuple)) and len(k) >= 2:
                edge_sensor_map[(k[0], k[1])] = v
            else:
                edge_sensor_map[k] = v

        edge_lengths = {
            (u, v): float(d.get("length", 500.0))
            for u, v, d in G.edges(data=True)
        }
        print(f"  [OK] Real graph: {G.number_of_nodes()} nodes, "
              f"{G.number_of_edges()} edges, "
              f"{len(edge_sensor_map)} sensor-mapped edges")
        return G, edge_sensor_map, edge_lengths

    # Synthetic fallback
    print("  [INFO] Building synthetic graph")
    N = N_SENSORS
    cols = 23
    G = nx.DiGraph()
    rng = np.random.default_rng(RANDOM_SEED)
    lats = rng.uniform(33.7, 34.4, N)
    lons = rng.uniform(-118.7, -117.8, N)
    for i in range(N):
        G.add_node(i, y=float(lats[i]), x=float(lons[i]))
    esm, el = {}, {}
    for i in range(N):
        r, c = i // cols, i % cols
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            j = (r+dr)*cols + (c+dc)
            if 0 <= j < N and 0 <= c+dc < cols:
                G.add_edge(i, j, length=1000.0)
                esm[(i, j)] = i
                el[(i, j)] = 1000.0
    print(f"  [OK] Synthetic graph: {G.number_of_nodes()} nodes")
    return G, esm, el


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: LOAD SPEED DATA
# ═══════════════════════════════════════════════════════════════════════════════

def load_speed_data():
    npz = os.path.join(PROCESSED_DIR, "training_data.npz")
    d = np.load(npz)
    speed = np.vstack([d["X_train"][:,0,:], d["X_val"][:,0,:], d["X_test"][:,0,:]])
    print(f"  [OK] Speed data: {speed.shape}  (time steps x sensors)")
    return speed.astype(np.float32)


# ═══════════════════════════════════════════════════════════════════════════════
# TRAVEL TIME FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def predict_travel_times(model, scaler, speed_window, edge_sensor_map, edge_lengths):
    """
    speed_window : np.ndarray (N_SENSORS, SEQUENCE_LEN) in mph
    Model input  : (1, SEQUENCE_LEN, N_SENSORS) = (1, 12, 207)
    Returns      : dict {(u,v): np.ndarray shape (N_FUTURE,)} in seconds
    """
    n = speed_window.shape[0]

    # Scale: transpose to (SEQUENCE_LEN, N_SENSORS), flatten, scale, reshape
    X = speed_window.T.reshape(-1, 1)             # (12*207, 1)
    X = scaler.transform(X).reshape(1, SEQUENCE_LEN, n)  # (1, 12, 207)

    raw = model.predict(X, verbose=0)             # (1, N_FUTURE * N_SENSORS)

    pred_mph = scaler.inverse_transform(
        raw.reshape(-1, 1)
    ).reshape(N_FUTURE, n)                        # (N_FUTURE, 207)
    pred_mph = np.clip(pred_mph, 1.0, None)
    pred_mps = pred_mph * 0.44704                 # (N_FUTURE, 207)

    tt_fn = {}
    for e, s in edge_sensor_map.items():
        if isinstance(s, (int, np.integer)) and int(s) < n:
            length = edge_lengths.get(e, 500.0)
            tt_fn[e] = length / pred_mps[:, int(s)]  # (N_FUTURE,)
    return tt_fn


def current_tt(speed_window, edge_sensor_map, edge_lengths):
    mph = np.clip(speed_window[:, -1], 1.0, None)
    mps = mph * 0.44704
    return {e: edge_lengths.get(e, 500.0) / mps[int(s)]
            for e, s in edge_sensor_map.items()
            if isinstance(s, (int, np.integer)) and int(s) < len(mps)}


def hist_avg_tt(speed_data, edge_sensor_map, edge_lengths):
    avg = np.clip(np.nanmean(speed_data, axis=0), 1.0, None) * 0.44704
    return {e: edge_lengths.get(e, 500.0) / avg[int(s)]
            for e, s in edge_sensor_map.items()
            if isinstance(s, (int, np.integer)) and int(s) < len(avg)}


def free_flow_tt(edge_lengths):
    return {e: l / FREE_FLOW for e, l in edge_lengths.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTING
# ═══════════════════════════════════════════════════════════════════════════════

def _heuristic(G, n, goal):
    try:
        d1, d2 = G.nodes[n], G.nodes[goal]
        R = 6_371_000
        p1 = math.radians(d1["y"]); p2 = math.radians(d2["y"])
        dp = math.radians(d2["y"]-d1["y"]); dl = math.radians(d2["x"]-d1["x"])
        a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2*R*math.asin(math.sqrt(a)) / FREE_FLOW
    except Exception:
        return 0.0


def _get_tt(tt_fn, ff, u, v, elapsed):
    e = (u, v)
    if e in tt_fn:
        val = tt_fn[e]
        if hasattr(val, "__len__"):
            slot = min(int(elapsed // 300), len(val)-1)
            return max(float(val[slot]), 1.0)
        return max(float(val), 1.0)
    return max(ff.get(e, 300.0), 1.0)


def run_astar(G, origin, dest, tt_fn, ff):
    t0 = time.perf_counter()
    g_sc = {origin: 0.0}
    prev = {origin: None}
    heap = [(_heuristic(G, origin, dest), 0.0, origin)]
    while heap:
        f, g, u = heapq.heappop(heap)
        if g > g_sc.get(u, math.inf) + 1e-9:
            continue
        if u == dest:
            path, node = [], dest
            while node is not None:
                path.append(node); node = prev[node]
            path.reverse()
            return path, g, (time.perf_counter()-t0)*1000
        for v in G.successors(u):
            ng = g + _get_tt(tt_fn, ff, u, v, g)
            if ng < g_sc.get(v, math.inf):
                g_sc[v] = ng; prev[v] = u
                heapq.heappush(heap, (ng + _heuristic(G, v, dest), ng, v))
    return [origin], math.inf, (time.perf_counter()-t0)*1000


# ═══════════════════════════════════════════════════════════════════════════════
# JOURNEY SIMULATION (Objective 3 — threshold controller)
# ═══════════════════════════════════════════════════════════════════════════════

def simulate(G, origin, dest, tt_series, ff, delta):
    elapsed = 0.0
    current = origin
    slot = 0

    path, T_old, lat = run_astar(G, current, dest, tt_series[0], ff)
    lats = [lat]
    n_rep = 0

    while current != dest:
        if len(path) < 2:
            break
        nxt = path[1]
        tt = _get_tt(tt_series[min(slot, len(tt_series)-1)], ff, current, nxt, elapsed)
        elapsed += tt
        slot = min(int(elapsed // 300), len(tt_series)-1)
        current = nxt
        path.pop(0)

        if current == dest:
            break

        fn = tt_series[slot]
        _, T_new, check_lat = run_astar(G, current, dest, fn, ff)

        if T_old > 0 and abs(T_new - T_old) / T_old > delta:
            _, T_old, rl = run_astar(G, current, dest, fn, ff)
            lats.append(rl)
            n_rep += 1

    return elapsed, n_rep, float(np.mean(lats))


# ═══════════════════════════════════════════════════════════════════════════════
# OD PAIRS & SCENARIOS
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


def pick_slots(speed_data, scenario, n=5):
    mean = speed_data.mean(axis=1)
    if scenario == "peak_hour":
        cands = np.where(mean <= np.percentile(mean, 25))[0]
    elif scenario == "off_peak":
        cands = np.where(mean >= np.percentile(mean, 75))[0]
    else:
        cands = np.arange(SEQUENCE_LEN, len(mean)-N_FUTURE-10)
    rng = np.random.default_rng(RANDOM_SEED)
    return rng.choice(cands, size=min(n, len(cands)), replace=False).tolist()


def add_incident(window):
    rng = np.random.default_rng()
    n_aff = max(1, int(window.shape[0] * 0.15))
    aff = rng.choice(window.shape[0], n_aff, replace=False)
    out = window.copy()
    out[aff, SEQUENCE_LEN//2:] *= 0.6
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXPERIMENT LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def run_experiments(model, scaler, G, esm, el, speed_data):
    total = N_OD_PAIRS * len(SCENARIOS) * len(DELTA_VALUES)
    print(f"\n  {N_OD_PAIRS} OD pairs × {len(SCENARIOS)} scenarios × "
          f"{len(DELTA_VALUES)} delta values = {total} runs\n")

    h_avg = hist_avg_tt(speed_data, esm, el)
    ff    = free_flow_tt(el)
    pairs = make_od_pairs(G)
    rng   = np.random.default_rng(RANDOM_SEED)
    rows  = []
    count = 0

    for scenario in SCENARIOS:
        slots = pick_slots(speed_data, scenario)

        for origin, dest in pairs:
            slot  = int(rng.choice(slots))
            start = max(0, slot - SEQUENCE_LEN)
            win   = speed_data[start:slot, :].T          # (207, 12)
            if win.shape[1] < SEQUENCE_LEN:
                win = np.pad(win, ((0,0),(SEQUENCE_LEN-win.shape[1],0)), mode="edge")
            if scenario == "incident":
                win = add_incident(win)

            # ── GRU prediction ──────────────────────────────────────────────
            t0 = time.perf_counter()
            pred = predict_travel_times(model, scaler, win, esm, el)
            gru_ms = (time.perf_counter() - t0) * 1000

            curr = current_tt(win, esm, el)

            # ── Baselines ────────────────────────────────────────────────────
            _, b1, b1l = run_astar(G, origin, dest, curr,  ff)   # Dijkstra equiv
            _, b2, b2l = run_astar(G, origin, dest, h_avg, ff)   # Static A*
            _, b3, b3l = run_astar(G, origin, dest, curr,  ff)   # Reactive A*
            _, b4, b4l = run_astar(G, origin, dest, pred,  ff)   # Oracle A*

            tt_series = [pred] * (N_FUTURE + 2)

            for delta in DELTA_VALUES:
                count += 1
                if count % 100 == 0:
                    print(f"  Progress: {count}/{total} "
                          f"({count*100//total}%)", flush=True)
                try:
                    fw_tt, n_rep, fw_lat = simulate(
                        G, origin, dest, tt_series, ff, delta)

                    def red(base):
                        if base > 0 and fw_tt < math.inf:
                            return (base - fw_tt) / base * 100
                        return 0.0

                    rows.append({
                        "scenario":        scenario,
                        "delta":           delta,
                        "gru_ms":          gru_ms,
                        "b1_tt":           b1,
                        "b2_tt":           b2,
                        "b3_tt":           b3,
                        "b4_tt":           b4,
                        "fw_tt":           fw_tt,
                        "fw_lat_ms":       fw_lat,
                        "n_replannings":   n_rep,
                        "red_vs_b1":       red(b1),
                        "red_vs_b2":       red(b2),
                        "red_vs_b3":       red(b3),
                        "red_vs_b4":       red(b4),
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
        ("red_vs_b1", "vs Dijkstra (B1)   "),
        ("red_vs_b2", "vs Static A* (B2)  "),
        ("red_vs_b3", "vs Reactive A* (B3)"),
        ("red_vs_b4", "vs Oracle A* (B4)  "),
    ]:
        m, s = df[col].mean(), df[col].std()
        print(f"  {label}  mean reduction: {m:+.2f}% ± {s:.2f}%")

    print(f"\n  Avg TD-A* latency:      {df['fw_lat_ms'].mean():.3f} ms")
    print(f"  Avg GRU inference:      {df['gru_ms'].mean():.1f} ms")
    print(f"  Avg replannings/journey:{df['n_replannings'].mean():.2f}")

    print("\n" + "="*65)
    print("OBJECTIVE 3 — THRESHOLD (delta) SENSITIVITY")
    print("="*65)
    g = df.groupby("delta")[["red_vs_b1","n_replannings","fw_lat_ms"]].mean().round(3)
    g.columns = ["Mean Reduction vs Dijkstra (%)", "Avg Replannings", "Avg Latency (ms)"]
    print(g.to_string())

    try:
        from scipy import stats
        groups = [df[df["delta"]==d]["red_vs_b1"].values for d in DELTA_VALUES]
        F, p = stats.f_oneway(*groups)
        print(f"\n  ANOVA: F={F:.3f}  p={p:.3f}")
        if p > 0.05:
            print("  → No significant difference across delta values (p>0.05).")
            best = df.groupby("delta")["red_vs_b1"].mean().idxmax()
            print(f"  → Recommended delta = {best} "
                  f"(best mean reduction, fewest unnecessary replannings)")
        else:
            best = df.groupby("delta")["red_vs_b1"].mean().idxmax()
            print(f"  → Significant difference found. Best delta = {best}")
    except ImportError:
        print("  Run: pip install scipy  for ANOVA")

    print("\n" + "="*65)
    print("BREAKDOWN BY SCENARIO")
    print("="*65)
    print(df.groupby("scenario")[["red_vs_b1","n_replannings"]].mean().round(2).to_string())


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
    cols  = [("red_vs_b1","Dijkstra",NAVY),
             ("red_vs_b2","Static A*",TEAL),
             ("red_vs_b3","Reactive A*",GOLD),
             ("red_vs_b4","Oracle A*",RED)]
    x = np.arange(len(scens)); w = 0.18
    for i,(c,l,col) in enumerate(cols):
        vals = [df[df["scenario"]==s][c].mean() for s in scens]
        ax.bar(x+i*w, vals, w, label=l, color=col, alpha=0.85)
    ax.set_xticks(x+w*1.5)
    ax.set_xticklabels([s.replace("_"," ").title() for s in scens])
    ax.set_ylabel("Travel Time Reduction (%)"); ax.legend()
    ax.set_title("Objective 4 — Framework vs Baselines by Scenario", fontweight="bold")
    ax.grid(axis="y", alpha=0.3); ax.set_facecolor("#F4F7FF")
    plt.tight_layout()
    p = os.path.join(VIZ_DIR, "obj4_travel_time_reduction.png")
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[OK] {p}")

    # ── Chart 2: Delta sensitivity (Objective 3) ──────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Objective 3 — Threshold (δ) Sensitivity Analysis",
                 fontweight="bold", fontsize=13)
    g = df.groupby("delta")
    d_labels = [str(d) for d in DELTA_VALUES]

    ax = axes[0]
    means = g["red_vs_b1"].mean().reindex(DELTA_VALUES)
    stds  = g["red_vs_b1"].std().reindex(DELTA_VALUES)
    ax.bar(d_labels, means.values, yerr=stds.values, color=NAVY, alpha=0.8,
           error_kw={"capsize":5})
    ax.set_xlabel("Threshold δ"); ax.set_ylabel("Mean Reduction vs Dijkstra (%)")
    ax.set_title("Route Quality by δ"); ax.grid(axis="y", alpha=0.3)
    ax.set_facecolor("#F4F7FF")

    ax = axes[1]
    reps = g["n_replannings"].mean().reindex(DELTA_VALUES)
    ax.bar(d_labels, reps.values, color=TEAL, alpha=0.8)
    ax.set_xlabel("Threshold δ"); ax.set_ylabel("Avg Replannings per Journey")
    ax.set_title("Update Frequency by δ"); ax.grid(axis="y", alpha=0.3)
    ax.set_facecolor("#F4F7FF")
    plt.tight_layout()
    p = os.path.join(VIZ_DIR, "obj3_delta_sensitivity.png")
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[OK] {p}")

    # ── Chart 3: Latency distribution ────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(df["fw_lat_ms"], bins=30, color=NAVY, alpha=0.8, edgecolor="white")
    mean_lat = df["fw_lat_ms"].mean()
    ax.axvline(mean_lat, color=GOLD, lw=2, label=f"Mean: {mean_lat:.3f} ms")
    ax.axvline(1000, color=RED, lw=1.5, ls="--", label="1,000 ms target")
    ax.set_xlabel("Routing Latency (ms)"); ax.set_ylabel("Frequency")
    ax.set_title("Objective 4 — TD-A* Latency Distribution", fontweight="bold")
    ax.legend(); ax.grid(alpha=0.3); ax.set_facecolor("#F4F7FF")
    plt.tight_layout()
    p = os.path.join(VIZ_DIR, "obj4_latency_distribution.png")
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    print(f"[OK] {p}")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("="*65)
    print("OBJECTIVES 3 & 4 — FULL SIMULATION")
    print("="*65)

    print("\n[Phase 1] Loading GRU model...")
    model = load_model()
    scaler = load_scaler()

    print("\n[Phase 2] Loading road network...")
    G, esm, el = load_graph()

    print("\n[Phase 3] Loading speed data...")
    speed = load_speed_data()
    speed = speed[:, :N_SENSORS]

    print("\n[Phase 4] Running experiments...")
    df = run_experiments(model, scaler, G, esm, el, speed)

    raw = os.path.join(RESULTS_DIR, "simulation_results.csv")
    df.to_csv(raw, index=False)
    print(f"\n[OK] Raw results → {raw}  ({len(df)} records)")

    analyse(df)

    print("\n[Phase 5] Saving visualisations...")
    visualise(df)

    summ = df.groupby(["scenario","delta"])[[
        "fw_tt","b1_tt","red_vs_b1","red_vs_b2",
        "fw_lat_ms","n_replannings","gru_ms"
    ]].agg(["mean","std"]).round(3)
    sp = os.path.join(RESULTS_DIR, "summary_statistics.csv")
    summ.to_csv(sp)
    print(f"[OK] Summary → {sp}")

    print("\n" + "="*65)
    print("DONE — check results/simulation/ and visualizations/")
    print("="*65)


if __name__ == "__main__":
    main()