"""Build the 15-minute research seminar PPT (widescreen, KyU navy).

Overwrites docs/Freshia_Njoki_Obj34_Findings_Presentation.pptx in place.
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

NAVY = RGBColor(0x1E, 0x27, 0x61)
GOLD = RGBColor(0xE8, 0xA8, 0x38)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ICE = RGBColor(0xCA, 0xDC, 0xFC)
MUTED = RGBColor(0xA0, 0xB0, 0xD0)
CARD = RGBColor(0x2A, 0x35, 0x7A)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "Freshia_Njoki_Obj34_Findings_Presentation.pptx"
FIG = ROOT / "results" / "simulation" / "figures"
TOTAL = 12


def set_bg(slide, rgb=NAVY):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb


def bar(slide, top=0, height=0.12, color=GOLD):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(top), Inches(13.333), Inches(height)
    )
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    return sh


def footer(slide, n, total=TOTAL):
    bar(slide, top=7.38, height=0.12, color=GOLD)
    t = slide.shapes.add_textbox(Inches(0.4), Inches(7.18), Inches(10.5), Inches(0.22))
    p = t.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = "Kirinyaga University  ·  MSc Computer Science  ·  Freshia Njoki Macharia"
    run.font.size = Pt(10)
    run.font.color.rgb = MUTED
    run.font.name = "Calibri"
    t2 = slide.shapes.add_textbox(Inches(11.6), Inches(7.18), Inches(1.4), Inches(0.22))
    p2 = t2.text_frame.paragraphs[0]
    p2.alignment = PP_ALIGN.RIGHT
    r2 = p2.add_run()
    r2.text = f"{n} / {total}"
    r2.font.size = Pt(10)
    r2.font.color.rgb = MUTED
    r2.font.name = "Calibri"


def txt(slide, l, t, w, h, text, size=18, color=WHITE, bold=False, font="Calibri",
        align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    return box


def bullets(slide, l, t, w, h, items, size=16, color=WHITE, space_after=8):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = "•  " + item
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.name = "Calibri"
    return box


def card(slide, l, t, w, h, fill=CARD):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h)
    )
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def add_picture_safe(slide, path, l, t, w=None, h=None):
    path = Path(path)
    if not path.exists():
        return
    kwargs = {}
    if w:
        kwargs["width"] = Inches(w)
    if h:
        kwargs["height"] = Inches(h)
    slide.shapes.add_picture(str(path), Inches(l), Inches(t), **kwargs)


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]


# ----- 1 title -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.6, 0.45, 12, 0.35, "KIRINYAGA UNIVERSITY  ·  SCHOOL OF PURE AND APPLIED SCIENCES", 14, ICE)
txt(
    s, 0.6, 1.05, 12, 1.7,
    "GRU-Based Predictive Route Optimisation\nfor Emergency Vehicle Navigation",
    32, WHITE, True, "Cambria",
)
sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(2.85), Inches(3.0), Inches(0.06))
sh.fill.solid()
sh.fill.fore_color.rgb = GOLD
sh.line.fill.background()
txt(s, 0.6, 3.1, 12, 0.4, "Master of Science in Computer Science  ·  Research seminar (15 minutes)", 18, ICE)
txt(
    s, 0.6, 3.7, 12, 1.1,
    "Freshia Njoki Macharia  |  PA206/S/25427/24\n"
    "Supervisors: Dr Gilbert Langat  ·  Dr Stephen Mageto",
    16, MUTED,
)
txt(
    s, 0.6, 5.15, 12, 0.7,
    "Artefact: two-layer GRU speed forecasts + time-dependent A* + remaining-time controller\n"
    "Evaluation: 900 ground-truth journeys on the METR-LA detector graph",
    15, GOLD,
)
footer(s, 1)
notes(
    s,
    "0:00–0:30. Thank the chair, supervisors, and examiners. One sentence: this seminar reports a "
    "decision-support framework that forecasts short-horizon traffic speeds and uses those forecasts "
    "to route an emergency vehicle before congestion is met. The dispatcher keeps authority. "
    "Then preview the arc: problem → purpose and objectives → method → prediction → routing results "
    "→ limits. Stay inside 15 minutes.",
)


# ----- 2 problem -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.45, "Problem statement", 26, WHITE, True, "Cambria")
card(s, 0.5, 0.9, 12.3, 1.55)
txt(
    s, 0.75, 1.05, 11.8, 1.25,
    "Emergency vehicles lose time in congestion when dispatch uses a current-map shortest path. "
    "That path is optimal only for the speeds observed at departure. It does not anticipate a jam "
    "forming 15–30 minutes ahead on the planned corridor.",
    16, WHITE,
)
items = [
    ("Practice", "Dijkstra (or equivalent) on the snapshot available at dispatch."),
    ("Literature", "Strong speed predictors and strong time-dependent routers usually sit in separate papers. Few emergency loops join a learned forecast, time-dependent search, and a tested remaining-time trigger under one second."),
    ("Motivation", "Kenyan EMS delay and sparse roadside sensing motivate the work. This study is a proof of concept on United States freeway detectors; it is not a Nairobi field trial."),
]
for i, (h, body) in enumerate(items):
    y = 2.65 + i * 1.35
    card(s, 0.5, y, 12.3, 1.22)
    txt(s, 0.75, y + 0.12, 11.8, 0.32, h, 16, GOLD, True)
    txt(s, 0.75, y + 0.46, 11.8, 0.65, body, 15, WHITE)
footer(s, 2)
notes(
    s,
    "0:30–1:45. State the problem in operational language. Do not open with architecture. "
    "If asked about Nairobi: the purpose is motivated by local EMS delay; the measured percentages "
    "come from Los Angeles detectors. Method can transfer; numbers cannot until local sensors exist.",
)


# ----- 3 purpose / RQs / objectives -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.4, "Purpose, questions, and objectives", 26, WHITE, True, "Cambria")
card(s, 0.5, 0.8, 12.3, 1.25)
txt(s, 0.75, 0.92, 11.8, 0.28, "Purpose", 14, GOLD, True)
txt(
    s, 0.75, 1.22, 11.8, 0.7,
    "To reduce emergency-vehicle travel time under congestion by combining short-horizon GRU speed "
    "forecasts with time-dependent A* and a remaining-time replanning threshold, as dispatcher support.",
    15, WHITE,
)
rqs = [
    ("RQ1", "What gaps remain among EV routing, traffic prediction, and time-dependent pathfinding?"),
    ("RQ2", "How accurately can a lightweight GRU forecast 15–30 minute speeds on loop-detector traces?"),
    ("RQ3", "Which remaining-time threshold δ balances route quality against extra dispatcher alerts?"),
    ("RQ4", "Does the integrated loop cut realised travel time versus baselines while staying under 1 s?"),
]
for i, (h, b) in enumerate(rqs):
    y = 2.2 + i * 0.55
    txt(s, 0.55, y, 1.1, 0.45, h, 14, GOLD, True)
    txt(s, 1.7, y, 11.0, 0.5, b, 14, WHITE)
txt(
    s, 0.5, 4.45, 12.3, 0.3,
    "Objectives  —  Obj. 1 design the GRU  ·  Obj. 2 train and validate  ·  Obj. 3 integrate TD-A* and test δ  ·  Obj. 4 evaluate travel time and latency",
    13, ICE,
)
card(s, 0.5, 4.9, 12.3, 1.5)
txt(s, 0.75, 5.05, 11.8, 0.28, "Scope of this seminar", 14, GOLD, True)
txt(
    s, 0.75, 5.4, 11.8, 0.8,
    "Objectives 1–2 are summarised (architecture, MAE, two datasets). Objectives 3–4 are reported in full: "
    "δ sweep, 900 matched journeys, four baselines, and computational feasibility.",
    15, WHITE,
)
footer(s, 3)
notes(
    s,
    "1:45–3:15. Read the purpose once. Then: four questions map onto four objectives. "
    "RQ3’s δ is a dispatcher setting, not a p-value. RQ4’s 1-second cap is the operational constraint. "
    "Tell them you will spend most of the remaining time on Objectives 3 and 4 because that is new evidence.",
)


# ----- 4 framework -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.45, "Proposed framework", 26, WHITE, True, "Cambria")
steps = [
    ("1", "Observe", "12 steps of detector speeds (60 minutes)."),
    ("2", "Forecast", "Two-layer GRU, 64 units, dropout 0.2 → 6 steps (30 minutes)."),
    ("3", "Cost", "Predicted mph converted to edge travel times on the detector graph."),
    ("4", "Route", "Time-dependent A* from origin to destination."),
    ("5", "Control", "Offer a new path if remaining time grows by more than δ."),
    ("6", "Authority", "Dispatcher accepts or rejects. The vehicle is not autonomous."),
]
for i, (n, h, b) in enumerate(steps):
    col, row = i % 3, i // 3
    x, y = 0.45 + col * 4.2, 0.95 + row * 2.55
    card(s, x, y, 4.0, 2.35)
    txt(s, x + 0.2, y + 0.2, 3.6, 0.45, n, 28, GOLD, True, "Cambria")
    txt(s, x + 0.2, y + 0.75, 3.6, 0.4, h, 18, ICE, True)
    txt(s, x + 0.2, y + 1.25, 3.6, 0.85, b, 14, WHITE)
footer(s, 4)
notes(
    s,
    "3:15–4:15. Walk 1→6 left to right, then down. Emphasise remaining time from the vehicle’s current "
    "position, not the original station-to-scene total. Two GRUs exist (METR-LA and PEMS-BAY); only the "
    "Los Angeles model feeds routing. This is decision support, not an automated ambulance.",
)


# ----- 5 methods -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.4, "Data, graph, and experimental design", 26, WHITE, True, "Cambria")
left = [
    "METR-LA: 207 loop detectors, 34,272 five-minute frames (Li et al., 2018).",
    "PEMS-BAY: 325 detectors, January–May 2017 (five months). Separate GRU; prediction only.",
    "StandardScaler fitted on the training split only (no leakage from val/test).",
    "Routing graph: METR-LA detector adjacency — 207 nodes, 1,515 edges, every edge instrumented.",
]
right = [
    "75 origin–destination pairs (seed 42) × 3 scenarios × 4 δ values = 900 journeys.",
    "Scenarios: peak (slowest quartile), off-peak (fastest quartile), incident (40% slowdown on the planned corridor).",
    "Every method is walked on actual future speeds. Pairing is identical origin, destination, and clock.",
    "B1 Dijkstra (current snapshot)  ·  B2 static A* (historical mean)  ·  B3 reactive A*  ·  B4 oracle.",
]
card(s, 0.45, 0.85, 6.1, 5.5)
txt(s, 0.7, 1.05, 5.6, 0.35, "Data and network", 16, GOLD, True)
bullets(s, 0.7, 1.55, 5.6, 4.5, left, size=15, space_after=14)
card(s, 6.8, 0.85, 6.1, 5.5)
txt(s, 7.05, 1.05, 5.6, 0.35, "900-run design", 16, GOLD, True)
bullets(s, 7.05, 1.55, 5.6, 4.5, right, size=15, space_after=14)
footer(s, 5)
notes(
    s,
    "4:15–5:30. Two datasets, two models — not one joint 207+325 tensor. Routing uses only METR-LA. "
    "The graph is the detector adjacency with 100% coverage, not an OpenStreetMap downtown extract. "
    "Incident means the vehicle actually meets a slowed corridor. B4 is an unreachable ceiling so the "
    "framework must not beat it. B3 replans after the jam is already visible.",
)


# ----- 6 prediction -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.22, 12, 0.4, "Objectives 1 and 2 — prediction", 26, WHITE, True, "Cambria")
stats = [
    ("3.48 mph", "METR-LA test MAE\nRMSE 6.04 mph  ·  27 epochs"),
    ("2.38 mph", "PEMS-BAY test MAE\nseparate model  ·  79 epochs"),
    ("158 k", "Trainable parameters\n2 × 64 GRU, dropout 0.2"),
]
for i, (n, lab) in enumerate(stats):
    card(s, 0.45 + i * 4.2, 0.8, 4.0, 1.85)
    txt(s, 0.55 + i * 4.2, 0.95, 3.8, 0.7, n, 28, GOLD, True, "Cambria", PP_ALIGN.CENTER)
    txt(s, 0.55 + i * 4.2, 1.7, 3.8, 0.75, lab, 13, WHITE, False, "Calibri", PP_ALIGN.CENTER)
card(s, 0.45, 2.9, 12.4, 3.45)
txt(s, 0.7, 3.1, 12.0, 0.35, "What this means for routing", 16, GOLD, True)
bullets(
    s, 0.7, 3.55, 11.9, 2.55,
    [
        "A 3.48 mph error on freeway speeds is small enough to rank corridors, not to replace a dispatcher.",
        "PEMS-BAY confirms the architecture in a second city. It is not a second 900-run routing city.",
        "Input window 60 minutes; forecast horizon 30 minutes — matched to a typical urban emergency trip.",
        "The defended METR-LA checkpoint is the 27-epoch model (MAE 3.48 mph) used for the 900 journeys.",
    ],
    size=15, space_after=10,
)
footer(s, 6)
notes(
    s,
    "5:30–6:30. Quote 3.48 and 2.38. Chronological 70/15/15 split. Train-only scaler. "
    "If asked why not a graph neural net: latency budget and a proof-of-concept two-layer GRU; "
    "literature already shows GNNs can win on MAE. You traded a little accuracy for a 40 ms loop.",
)


# ----- 7 obj 3 -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.22, 12, 0.4, "Objective 3 — remaining-time threshold δ", 24, WHITE, True, "Cambria")
add_picture_safe(s, FIG / "fig3_delta_sensitivity.png", 0.3, 0.7, w=8.2)
card(s, 8.65, 0.7, 4.25, 5.7)
txt(s, 8.85, 0.85, 3.9, 0.35, "Finding", 16, GOLD, True)
txt(
    s, 8.85, 1.3, 3.9, 4.85,
    "δ = 0.05 means: offer a new path if remaining time from the current position grows by 5%.\n\n"
    "Tested {0.05, 0.10, 0.15, 0.20}.\n\n"
    "Travel time did not move (ANOVA F ≈ 0.001, p = 1.00).\n\n"
    "Incident reduction stayed ≈ 16% at every δ, with about one replan per journey.\n\n"
    "Recommended default: δ = 0.20 — same travel time, slightly fewer alerts.\n\n"
    "0.10 was the Chapter 3 starting guess, not the measured default.\n\n"
    "δ is a policy. α = .05 is a significance level. They are not the same 0.05.",
    13, WHITE,
)
footer(s, 7)
notes(
    s,
    "6:30–8:00. Point at the flat incident line. A 40% corridor drop exceeds a 20% remaining-time "
    "trigger, so every policy still fires in incidents. That is why travel time tied and you pick "
    "the least chatty setting. APA: p = .0002, no leading zero. Do not call F ≈ 0 a failed study.",
)


# ----- 8 obj 4 times -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.22, 12, 0.4, "Objective 4 — realised journey time", 24, WHITE, True, "Cambria")
add_picture_safe(s, FIG / "fig1_travel_time_comparison.png", 0.25, 0.7, w=8.2)
card(s, 8.55, 0.7, 4.4, 5.7)
txt(s, 8.75, 0.85, 4.0, 0.35, "Mean travel time (s)", 16, GOLD, True)
txt(
    s, 8.75, 1.3, 4.0, 4.9,
    "Incident\n  Dijkstra  ≈  728 s\n  Framework  ≈  599 s\n  Reactive A*  ≈  604 s\n  Oracle  ≈  581 s\n\n"
    "Peak\n  Framework  ≈  506 s\n  Dijkstra  ≈  513 s\n\n"
    "Off-peak\n  Both  ≈  403 s\n\n"
    "The framework does not beat the oracle. That is required if B4 is an honest ceiling.",
    14, WHITE,
)
footer(s, 8)
notes(
    s,
    "8:00–9:15. When the planned road is jammed, 728 seconds falls to about 599. Off-peak bars sit "
    "together: empty roads do not need a 30-minute forecast. Peak is a small gap. Reactive A* is close "
    "in incidents once the jam is visible — the extra value of the forecast is anticipatory, not magic.",
)


# ----- 9 obj 4 percent -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.22, 12, 0.4, "Objective 4 — reduction versus Dijkstra", 24, WHITE, True, "Cambria")
add_picture_safe(s, FIG / "fig2_reduction_by_scenario.png", 0.25, 0.7, w=8.3)
card(s, 8.7, 0.7, 4.2, 5.7)
txt(s, 8.9, 0.85, 3.85, 0.35, "Paired results (N = 300)", 16, GOLD, True)
txt(
    s, 8.9, 1.3, 3.85, 4.9,
    "Incident  +16.19%\n  t = 26.43,  p < .001\n  ~1.03 replans / journey\n\n"
    "Peak  +1.03%\n  t = 3.81,  p = .0002\n\n"
    "Off-peak  +0.01%\n  p = .90  (not significant)\n\n"
    "Overall  +5.74%\nvs static A*  +7.39%\nvs reactive A*  +0.61%\nvs oracle  −1.69%\n\n"
    "Overall is a mixture. Do not promise 16% on every trip.",
    13, WHITE,
)
footer(s, 9)
notes(
    s,
    "9:15–10:45. The 16% bar is the result that matches the purpose: time reduction when traffic actually "
    "breaks. Peak +1% is statistically detectable but operationally small. Off-peak ≈ 0% is a successful "
    "negative control. Versus reactive A* the extra is small: once the jam is visible, a 30-minute "
    "forecast adds little. That is an honest finding. If asked about literature: 16% sits near "
    "Abuaisha et al. (2025) 12–18% on a different (fixed-route) problem; Werner et al. (2022) is the "
    "closest router and does not use this GRU + δ loop.",
)


# ----- 10 latency -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.22, 12, 0.4, "Computational feasibility", 24, WHITE, True, "Cambria")
add_picture_safe(s, FIG / "fig4_computational_performance.png", 0.25, 0.7, w=8.3)
card(s, 8.7, 0.7, 4.25, 5.7)
txt(s, 8.9, 0.9, 3.9, 0.35, "Dispatcher wait", 16, GOLD, True)
txt(
    s, 8.9, 1.4, 3.9, 4.7,
    "TD-A* search   0.37 ms\nGRU inference   39.3 ms\nCombined        ≈ 40 ms\n\n"
    "Operational cap  1,000 ms\nHeadroom         ≈ 25×\n\n"
    "Routing is not the bottleneck. The predictor is, and the loop still fits comfortably inside one second.\n\n"
    "No preprocessing of the graph is required at this urban scale, so edge weights can refresh every five minutes.",
    15, WHITE,
)
footer(s, 10)
notes(
    s,
    "10:45–11:30. Combined ≈ 40 milliseconds is the system claim. Quote both pieces if asked: "
    "0.37 ms is search only. Werner et al. showed that time-dependent A* can be fast on very large "
    "maps with preprocessing; at 207 nodes that preprocessing was unnecessary.",
)


# ----- 11 limitations (academic; no bug list) -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.45, "Limitations and further research", 26, WHITE, True, "Cambria")
card(s, 0.45, 0.85, 6.1, 5.5)
txt(s, 0.7, 1.05, 5.6, 0.35, "Limits of the present evidence", 16, GOLD, True)
bullets(
    s, 0.7, 1.55, 5.6, 4.5,
    [
        "METR-LA and PEMS-BAY are United States freeway traces. They do not reproduce Nairobi mixed traffic.",
        "The 900 journeys used 100% detector coverage (207 nodes, 1,515 edges). Reported percentages describe that graph.",
        "PEMS-BAY confirmed prediction in a second city (MAE 2.38 mph) but was not given a routing 900-run.",
        "A sparse-sensor analogue (10–30% coverage) was not executed.",
        "Single-vehicle simulation: multi-ambulance interference was not modelled.",
    ],
    size=14, space_after=10,
)
card(s, 6.8, 0.85, 6.1, 5.5)
txt(s, 7.05, 1.05, 5.6, 0.35, "Suggested further work", 16, GOLD, True)
bullets(
    s, 7.05, 1.55, 5.6, 4.5,
    [
        "Downsample the present 100% detector graph to 10–30% coverage and repeat the 900-run, as a Nairobi-density analogue.",
        "Build a PEMS-BAY routing graph and repeat Objectives 3 and 4.",
        "Field trial with local sensors. The dispatcher remains in authority.",
        "Multi-vehicle and live incident feeds lie beyond this proof of concept.",
        "No conversion of +16% into Nairobi CBD minutes against an eight-minute target is claimed.",
    ],
    size=14, space_after=10,
)
footer(s, 11)
notes(
    s,
    "11:30–13:00. This is the examiners’ honesty slide. State what was measured and what was not. "
    "The next sparse-sensor study starts from the 100% detector graph and downsamples it. "
    "Do not discuss shrinking an unused downtown map. If asked whether Nairobi now meets an "
    "eight-minute target: no. Motivation is not measurement.",
)


# ----- 12 close -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.32, 12, 0.5, "Conclusions", 26, WHITE, True, "Cambria")
take = [
    ("1", "Under incident conditions the framework cut Dijkstra travel time by 16.19% (about 599 s versus 728 s), with about one replan per journey."),
    ("2", "Travel time did not differ among δ = 0.05–0.20. The operational default is δ = 0.20: the same quality, fewer extra alerts."),
    ("3", "Combined GRU and routing latency is about 40 ms, well inside the 1,000 ms dispatch cap. The binding constraint is local sensor data, not compute."),
]
for i, (n, t) in enumerate(take):
    y = 1.0 + i * 1.35
    card(s, 0.5, y, 12.3, 1.2)
    txt(s, 0.75, y + 0.3, 0.7, 0.55, n, 28, GOLD, True, "Cambria")
    txt(s, 1.6, y + 0.25, 10.8, 0.75, t, 16, WHITE)
txt(s, 0.5, 5.25, 12.3, 0.45, "Thank you  ·  Questions", 22, ICE, True, "Cambria", PP_ALIGN.CENTER)
txt(
    s, 0.5, 5.8, 12.3, 0.55,
    "Freshia Njoki Macharia  ·  PA206/S/25427/24  ·  Kirinyaga University",
    14, MUTED, False, "Calibri", PP_ALIGN.CENTER,
)
footer(s, 12)
notes(
    s,
    "13:00–15:00 including questions. Repeat the three numbered lines if asked to summarise. "
    "If asked for the code: the evaluation lives in the project repository; the defended tables "
    "match results/full_report.txt on the improved-evaluation branch. If asked why two datasets: "
    "prediction generalisation versus routing on one consistent graph. If asked about δ = 0.10: "
    "that was the planned guess; measurement selected 0.20.",
)

prs.save(str(OUT))
print("Wrote", OUT, "slides", len(prs.slides))
