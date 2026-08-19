"""Build the 15-minute Objectives 3 & 4 progress PPT (widescreen, KyU navy)."""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import nsmap
from pptx.util import Emu, Inches, Pt
from lxml import etree

NAVY = RGBColor(0x1E, 0x27, 0x61)
GOLD = RGBColor(0xE8, 0xA8, 0x38)
TEAL = RGBColor(0x0D, 0x94, 0x88)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ICE = RGBColor(0xCA, 0xDC, 0xFC)
MUTED = RGBColor(0xA0, 0xB0, 0xD0)
CARD = RGBColor(0x2A, 0x35, 0x7A)
RED = RGBColor(0xC0, 0x39, 0x2B)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "Freshia_Njoki_Obj34_Findings_Presentation.pptx"
FIG = ROOT / "results" / "simulation" / "figures"


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


def footer(slide, n, total=12):
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


def txt(slide, l, t, w, h, text, size=18, color=WHITE, bold=False, font="Calibri", align=PP_ALIGN.LEFT):
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


def card(slide, l, t, w, h, fill=CARD):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
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
txt(s, 0.6, 0.45, 12, 0.35, "KIRINYAGA UNIVERSITY  ·  MSc COMPUTER SCIENCE", 14, ICE)
txt(
    s,
    0.6,
    1.15,
    12,
    1.6,
    "GRU-Based Predictive Route Optimisation\nfor Emergency Vehicle Navigation",
    32,
    WHITE,
    True,
    "Cambria",
)
sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(2.95), Inches(3.0), Inches(0.06))
sh.fill.solid()
sh.fill.fore_color.rgb = GOLD
sh.line.fill.background()
txt(s, 0.6, 3.2, 12, 0.4, "Research Progress Presentation  —  Objectives 3 & 4 findings", 18, ICE)
txt(
    s,
    0.6,
    4.0,
    12,
    0.8,
    "Freshia Njoki Macharia  |  PA206/S/25427/24\nSupervisors: Dr Gilbert Langat  ·  Dr Stephen Mageto",
    16,
    MUTED,
)
txt(s, 0.6, 5.3, 12, 0.4, "Defended results  ·  900 ground-truth journeys  ·  METR-LA detector graph", 14, GOLD)
footer(s, 1)
notes(
    s,
    "0:00–0:30. Thank the panel. Say this talk reports Objectives 3 and 4 only, using the improved evaluation on branch cursor/improve-ev-routing-framework-c48b. One sentence on what the artefact is: GRU speeds + time-dependent A* + a remaining-time threshold, as dispatcher support. Do not mention 78%, 123 seconds, or 0.17%.",
)

# ----- 2 recap -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.45, "Recap — what was already shown (Obj. 1 & 2)", 26, WHITE, True, "Cambria")
items = [
    ("Gap", "No emergency loop joined a learned speed model, time-dependent search, and a tested remaining-time trigger."),
    ("Artefact", "Two-layer GRU (64 units, dropout 0.2) + TD-A* + δ-controller. Dispatcher keeps final authority."),
    ("Prediction", "METR-LA MAE 3.48 mph (27 epochs). Separate PEMS-BAY GRU MAE 2.38 mph. Not one joint model."),
    ("Graph", "Routing uses 207 detector nodes and 1,515 fully instrumented edges — not the old 397-node OSM map."),
]
for i, (h, body) in enumerate(items):
    y = 0.9 + i * 1.35
    card(s, 0.5, y, 12.3, 1.22)
    txt(s, 0.75, y + 0.12, 11.8, 0.35, h, 16, GOLD, True)
    txt(s, 0.75, y + 0.48, 11.8, 0.6, body, 16, WHITE)
footer(s, 2)
notes(
    s,
    "0:30–1:30. Correct the previous presentation: MAE is 3.48 not 3.42; 34,272 frames not 34,254; StandardScaler on train only, not MinMax; routing graph is the sensor graph, not 397 OSM nodes. PEMS-BAY is a second GRU, not a second 900-run.",
)

# ----- 3 setup -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.45, "What was measured — 900 matched journeys", 26, WHITE, True, "Cambria")
stats = [
    ("75", "origin–destination\npairs (seed 42)"),
    ("3", "scenarios: peak,\noff-peak, incident"),
    ("4", "δ values:\n5, 10, 15, 20%"),
    ("900", "ground-truth\nwalks of every method"),
]
for i, (n, lab) in enumerate(stats):
    card(s, 0.45 + i * 3.2, 0.95, 3.0, 2.15)
    txt(s, 0.45 + i * 3.2, 1.1, 3.0, 0.7, n, 36, GOLD, True, "Cambria", PP_ALIGN.CENTER)
    txt(s, 0.55 + i * 3.2, 1.9, 2.8, 0.95, lab, 14, WHITE, False, "Calibri", PP_ALIGN.CENTER)
txt(s, 0.5, 3.3, 12, 0.35, "Four baselines (same clock, same realised speeds)", 16, ICE, True)
bases = [
    ("B1  Dijkstra", "Current snapshot\n— dispatch practice"),
    ("B2  Static A*", "Historical mean\n— average day"),
    ("B3  Reactive A*", "Replan after jam\nis already visible"),
    ("B4  Oracle", "Perfect future speeds\n— unreachable ceiling"),
]
for i, (h, b) in enumerate(bases):
    card(s, 0.45 + i * 3.2, 3.75, 3.0, 1.7)
    txt(s, 0.55 + i * 3.2, 3.9, 2.8, 0.45, h, 15, GOLD, True)
    txt(s, 0.55 + i * 3.2, 4.4, 2.8, 0.85, b, 13, WHITE)
footer(s, 3)
notes(
    s,
    "1:30–2:30. Stress pairing: the same ambulance, same departure, five brains choosing the path, marked on actual future speeds. Incident = 40% slowdown on the planned corridor so the vehicle actually meets the jam. Peak = slowest quarter of windows; off-peak = fastest quarter.",
)

# ----- 4 obj3 question -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.45, "Objective 3 — which remaining-time trigger?", 26, WHITE, True, "Cambria")
card(s, 0.5, 0.95, 12.3, 1.5)
txt(
    s,
    0.75,
    1.1,
    11.8,
    1.15,
    "RQ3: What δ balances route reliability against extra dispatcher alerts?\nA new path is offered if remaining time from the current position grows by more than δ, or a new path is better by δ.",
    16,
    WHITE,
)
card(s, 0.5, 2.7, 6.0, 3.5)
txt(s, 0.75, 2.9, 5.5, 0.4, "δ  —  policy  (not a p-value)", 16, GOLD, True)
txt(
    s,
    0.75,
    3.4,
    5.5,
    2.5,
    "δ = 0.05 means: speak if the rest of the trip looks 5% worse.\n\nTested {0.05, 0.10, 0.15, 0.20}.\n\nThis is a dispatcher setting.",
    16,
    WHITE,
)
card(s, 6.8, 2.7, 6.0, 3.5)
txt(s, 7.05, 2.9, 5.5, 0.4, "α / p  —  statistics", 16, GOLD, True)
txt(
    s,
    7.05,
    3.4,
    5.5,
    2.5,
    "α = .05 means: call a mean reduction real only if a zero effect would produce it fewer than five times in a hundred.\n\nAPA writes p = .0002 (no leading zero) because p cannot exceed 1.",
    16,
    WHITE,
)
footer(s, 4)
notes(
    s,
    "2:30–3:30. This is the slide that stops the two 0.05s being mixed. Remaining time is from where the vehicle is now — that is why replans exist in the new run. If T_old was the original full trip from the station, the controller stayed silent.",
)

# ----- 5 obj3 figure -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.22, 12, 0.4, "Objective 3 — travel time did not move with δ", 24, WHITE, True, "Cambria")
add_picture_safe(s, FIG / "fig3_delta_sensitivity.png", 0.35, 0.7, w=8.3)
card(s, 8.8, 0.9, 4.1, 5.4)
txt(s, 9.0, 1.1, 3.7, 0.4, "Read the figure", 16, GOLD, True)
txt(
    s,
    9.0,
    1.55,
    3.7,
    4.5,
    "Left: % vs Dijkstra is flat across 5–20%.\nIncident ≈ 16% at every δ.\nPeak ≈ 1%. Off-peak ≈ 0%.\n\nRight: replans fall slightly as δ rises.\nIncidents ≈ 1 replan per trip.\n\nANOVA: F ≈ 0.001, p = 1.00.\nThe four policies tied on travel time.",
    14,
    WHITE,
)
footer(s, 5)
notes(
    s,
    "3:30–5:00. Point at the orange incident line: it is high and flat. F near zero is not a failed study — a 40% corridor drop is larger than 20% remaining-time growth, so every policy fired. That is why we do not pick δ by travel time.",
)

# ----- 6 recommend 0.20 -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.45, "Recommended default: δ = 0.20", 26, WHITE, True, "Cambria")
rows = [
    ("δ", "Mean vs Dijkstra", "Replans / journey", "TD-A* latency"),
    ("0.05", "+5.726%", "0.45", "0.37 ms"),
    ("0.10", "+5.748%", "0.44", "0.37 ms"),
    ("0.15", "+5.726%", "0.43", "0.37 ms"),
    ("0.20", "+5.767%", "0.39", "0.37 ms"),
]
for r, row in enumerate(rows):
    y = 0.95 + r * 0.7
    bgc = GOLD if r == 4 else (RGBColor(0x24, 0x2E, 0x6E) if r else CARD)
    fg = NAVY if r == 4 else WHITE
    for c, val in enumerate(row):
        card(s, 0.5 + c * 3.15, y, 3.05, 0.62, bgc)
        txt(s, 0.5 + c * 3.15, y + 0.12, 3.05, 0.4, val, 14, fg, True, "Calibri", PP_ALIGN.CENTER)
card(s, 0.5, 4.55, 12.3, 1.85)
txt(
    s,
    0.75,
    4.75,
    11.8,
    1.45,
    "Decision-support reading: keep the least chatty policy that still catches incidents.\n0.10 was the planned guess in Chapter 3. After measurement, 0.20 is the operational default.",
    16,
    WHITE,
)
footer(s, 6)
notes(
    s,
    "5:00–6:00. Highlight the last row. Slightly fewer alerts, same travel time. Do not say 0.10 is still recommended. Combined wait is not this 0.37 ms — that is routing only; GRU is ~39 ms.",
)

# ----- 7 obj4 times -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.22, 12, 0.4, "Objective 4 — journey time (seconds)", 24, WHITE, True, "Cambria")
add_picture_safe(s, FIG / "fig1_travel_time_comparison.png", 0.3, 0.7, w=8.1)
card(s, 8.55, 0.85, 4.4, 5.5)
txt(s, 8.75, 1.05, 4.0, 0.35, "Incident cell", 16, GOLD, True)
txt(
    s,
    8.75,
    1.5,
    4.0,
    4.5,
    "Dijkstra  ≈  728 s\nFramework  ≈  599 s\nReactive A*  ≈  604 s\nOracle  ≈  581 s\n\nPeak: 506 s vs 513 s\nOff-peak: both ≈ 403 s\n\nThe framework does not beat the oracle. That is required if B4 is honest.",
    15,
    WHITE,
)
footer(s, 7)
notes(
    s,
    "6:00–7:30. This replaces 123 s versus 588 s, which was a scaling bug. Tell them: when the planned road is jammed, 728 seconds falls to about 599. Off-peak bars sit on top of each other — empty roads do not need a fortune-teller.",
)

# ----- 8 percent -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.22, 12, 0.4, "Objective 4 — reduction versus Dijkstra", 24, WHITE, True, "Cambria")
add_picture_safe(s, FIG / "fig2_reduction_by_scenario.png", 0.25, 0.7, w=8.4)
card(s, 8.75, 0.85, 4.2, 5.5)
txt(s, 8.95, 1.0, 3.85, 0.35, "Headline numbers", 16, GOLD, True)
txt(
    s,
    8.95,
    1.45,
    3.85,
    4.6,
    "Incident  +16.19%\n  t = 26.43,  p < .001\n  ~1.03 replans\n\nPeak  +1.03%\n  t = 3.81,  p = .0002\n\nOff-peak  +0.01%\n  p = .90  (not significant)\n\nOverall  +5.74%\nvs static A*  +7.39%\nvs reactive A*  +0.61%\nvs oracle  −1.69%",
    14,
    WHITE,
)
footer(s, 8)
notes(
    s,
    "7:30–9:00. The 16% bar is the result that matches the purpose: emergency time reduction when traffic actually breaks. +5.74% overall is a mixture — do not promise 16% on every trip. Versus reactive A* the extra is small: once the jam is visible, a 30-minute forecast adds little. That is honest. Green 15% line is a plot decoration, not a WHO target.",
)

# ----- 9 latency -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.22, 12, 0.4, "Computational feasibility — well under 1 second", 24, WHITE, True, "Cambria")
add_picture_safe(s, FIG / "fig4_computational_performance.png", 0.3, 0.7, w=8.3)
card(s, 8.75, 0.9, 4.2, 5.4)
txt(s, 8.95, 1.1, 3.85, 0.35, "What the dispatcher waits", 16, GOLD, True)
txt(
    s,
    8.95,
    1.6,
    3.85,
    4.4,
    "TD-A*  0.37 ms\nGRU  39.3 ms\nCombined  ≈ 40 ms\n\nBudget  1,000 ms\n≈ 25× headroom\n\nDo not quote 0.315 ms\nor 69.1 ms — those were\nthe old OSM / old GRU run.\n\nRouting is not the bottleneck.\nThe predictor is, and it still fits.",
    15,
    WHITE,
)
footer(s, 9)
notes(
    s,
    "9:00–10:00. Combined 40 milliseconds is the DSS claim. 0.315 milliseconds was TD-A* on the old 397-node map and was never the full system wait. If asked about 3,175×, that used 0.315 against 1,000; the honest factor is about 25 times (1000/40).",
)

# ----- 10 interpret -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.45, "What the results mean", 26, WHITE, True, "Cambria")
blocks = [
    ("Incident +16%", "The planned road is crawling. The system offers another corridor. About one suggestion per journey — not a siren."),
    ("Peak +1%", "Almost every detector is already slow. Looking 15–30 minutes ahead helps only a little. Still statistically detectable."),
    ("Off-peak ≈ 0%", "Empty roads: a predictor and a paper map should agree. This is a successful negative control, not a failed model."),
    ("Literature", "16% sits near Abuaisha et al. (2025) 12–18% (fixed transit, different problem). Werner et al. (2022) is the closest router and does not replace the GRU + δ loop."),
]
for i, (h, b) in enumerate(blocks):
    y = 0.9 + i * 1.4
    card(s, 0.5, y, 12.3, 1.25)
    txt(s, 0.75, y + 0.12, 11.8, 0.32, h, 16, GOLD, True)
    txt(s, 0.75, y + 0.48, 11.8, 0.65, b, 15, WHITE)
footer(s, 10)
notes(
    s,
    "10:00–11:30. This is the 4.6 discussion in spoken form. Do not defend 18.6% coverage or zero replans. Those belonged to the unused OSM map and the old remaining-time bug. If asked about Nairobi: method can transfer; these percentages cannot until local sensors exist.",
)

# ----- 11 limits -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.45, "Limits — and what we are not claiming", 26, WHITE, True, "Cambria")
left = [
    "METR-LA / PEMS-BAY are US freeways, not matatu traffic.",
    "900-run routing is Los Angeles detectors only (100% coverage).",
    "PEMS-BAY was a second-city GRU check, not a second routing city.",
    "A 10–30% sparse-sensor Nairobi analogue has not been run.",
]
right = [
    "Do not convert +16% into CBD minutes against the WHO 8-minute target.",
    "Do not quote 3.42 mph, 17 epochs, 123 s, +0.17%, or 0 replans.",
    "Do not say the journal article still uses the OSM 18.6% graph.",
    "Further work: Bay routing graph; downsample 100% → 10–30%; field trial.",
]
card(s, 0.45, 0.95, 6.1, 5.2)
txt(s, 0.7, 1.15, 5.7, 0.4, "True limits", 16, GOLD, True)
txt(s, 0.7, 1.65, 5.7, 4.2, "\n\n".join("•  " + x for x in left), 15, WHITE)
card(s, 6.8, 0.95, 6.1, 5.2)
txt(s, 7.05, 1.15, 5.7, 0.4, "Do not say", 16, GOLD, True)
txt(s, 7.05, 1.65, 5.7, 4.2, "\n\n".join("•  " + x for x in right), 15, WHITE)
footer(s, 11)
notes(
    s,
    "11:30–13:00. This is the 5.5 correction: we do not reduce the old 18.6% map further. Sparse Nairobi work starts from the 100% detector graph and downsamples it. Journal article v0.3 already uses 3.48, 16.19%, 207 nodes, δ = 0.20 — do not paste OSM 18.6% into the paper as the result graph.",
)

# ----- 12 close -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.35, 12, 0.5, "Take-home for Objectives 3 and 4", 26, WHITE, True, "Cambria")
take = [
    ("1", "When a crash sits on the planned road, predictive remaining-time routing cut Dijkstra time by 16%."),
    ("2", "δ in 5–20% did not change travel time. Recommend δ = 0.20 to limit extra alerts."),
    ("3", "The dispatcher waits about 40 ms. The constraint is not compute; it is local sensor data."),
]
for i, (n, t) in enumerate(take):
    y = 1.15 + i * 1.35
    card(s, 0.5, y, 12.3, 1.2)
    txt(s, 0.75, y + 0.3, 0.7, 0.55, n, 28, GOLD, True, "Cambria")
    txt(s, 1.6, y + 0.28, 10.8, 0.7, t, 18, WHITE)
txt(s, 0.5, 5.4, 12, 0.5, "Thank you  ·  Questions", 22, ICE, True, "Cambria", PP_ALIGN.CENTER)
txt(
    s,
    0.5,
    6.0,
    12,
    0.4,
    "Results: github.com/Freshia-Njoki/Emergency_Routing  ·  branch cursor/improve-ev-routing-framework-c48b",
    13,
    MUTED,
    False,
    "Calibri",
    PP_ALIGN.CENTER,
)
footer(s, 12)
notes(
    s,
    "13:00–15:00 including questions. Repeat the three lines if asked to summarise. If asked which branch: cursor/improve-ev-routing-framework-c48b — not main. If asked to pull: git fetch && git checkout that branch && git pull, then PYTHONUTF8=1 and run_improved_pipeline.sh, or skip retrain and python -m src.evaluation.run_simulation --graph sensor if models already exist.",
)

prs.save(str(OUT))
print("Wrote", OUT, "slides", len(prs.slides))
