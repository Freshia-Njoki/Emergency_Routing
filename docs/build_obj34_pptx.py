"""Build the 15-minute findings seminar PPT (widescreen, KyU navy).

Overwrites docs/Freshia_Njoki_Obj34_Findings_Presentation.pptx.
Speaker notes are a live reading script (View → Notes / Presenter View).
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
    slide.notes_slide.notes_text_frame.text = text.strip()


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
    "What I will show: a dispatcher-support loop — forecast speeds, time-dependent route, remaining-time update.\n"
    "Evidence: 900 matched journeys on the METR-LA detector graph.",
    15, GOLD,
)
footer(s, 1)
notes(
    s,
    """SLIDE 1  ·  0:00–0:20  ·  read this

Chair, supervisors, examiners — thank you. I am Freshia Njoki Macharia.

This seminar reports a decision-support framework for emergency-vehicle routing. It forecasts traffic speeds for the next thirty minutes, computes a time-dependent path, and offers a new path only when remaining travel time has truly worsened.

I evaluated that loop on nine hundred matched journeys. The dispatcher keeps final authority.

I will go: problem, design, then the results — prediction, the threshold, journey time, and latency.""",
)


# ----- 2 problem -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.45, "The problem", 26, WHITE, True, "Cambria")
card(s, 0.5, 0.9, 12.3, 1.7)
txt(
    s, 0.75, 1.1, 11.8, 1.35,
    "A route that is shortest at dispatch is optimal only for the speeds seen at that moment. "
    "If a corridor slows fifteen to thirty minutes later, the vehicle is already committed. "
    "That is the failure this study treats.",
    17, WHITE,
)
items = [
    ("What dispatch does today", "A current-map shortest path — Dijkstra, or the same idea in A* — using speeds available at departure."),
    ("What the literature leaves open", "Strong predictors and strong time-dependent routers are usually published apart. An emergency loop that joins a learned forecast, time-dependent search, and a tested remaining-time trigger, inside one second, is missing."),
    ("Where the numbers come from", "Public freeway detector archives (METR-LA for routing; PEMS-BAY for a second-city prediction check). Replicable measurement. Local mixed traffic is the next deployment step, not this table."),
]
for i, (h, body) in enumerate(items):
    y = 2.8 + i * 1.35
    card(s, 0.5, y, 12.3, 1.22)
    txt(s, 0.75, y + 0.12, 11.8, 0.32, h, 16, GOLD, True)
    txt(s, 0.75, y + 0.46, 11.8, 0.65, body, 15, WHITE)
footer(s, 2)
notes(
    s,
    """SLIDE 2  ·  0:20–1:15  ·  read this

The operational problem is simple. At dispatch we compute a shortest path from the speeds on the map right now. That path is optimal only for those speeds. If a queue forms on the planned road fifteen or thirty minutes later, the vehicle is already on it.

That is how most computer-aided dispatch still works: Dijkstra, or A*, on a current snapshot.

The literature has excellent traffic predictors, and it has time-dependent shortest-path algorithms. They usually sit in different papers. What was missing is one emergency loop: learn the next half hour of speeds, route on those changing costs, and only interrupt the dispatcher when remaining time has really jumped — all inside one second.

I measured that loop on public loop-detector archives so another researcher can repeat it. METR-LA is the routing city. PEMS-BAY checks whether the same predictor still works in a second city.""",
)


# ----- 3 purpose -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.4, "Purpose and objectives", 26, WHITE, True, "Cambria")
card(s, 0.5, 0.8, 12.3, 1.35)
txt(s, 0.75, 0.92, 11.8, 0.28, "Purpose", 14, GOLD, True)
txt(
    s, 0.75, 1.25, 11.8, 0.7,
    "To design and evaluate a dispatcher-support framework that cuts realised emergency-vehicle "
    "travel time by joining GRU speed forecasts, time-dependent A*, and a remaining-time threshold.",
    16, WHITE,
)
rqs = [
    ("Obj. 1", "Map the gaps among emergency routing, traffic prediction, and time-dependent pathfinding."),
    ("Obj. 2", "Build the three-part system: GRU predictor, time-dependent A*, remaining-time controller."),
    ("Obj. 3", "Find which remaining-time threshold δ to use — 5%, 10%, 15%, or 20%."),
    ("Obj. 4", "Measure realised travel time and latency against four baselines, inside one second."),
]
for i, (h, b) in enumerate(rqs):
    y = 2.35 + i * 0.7
    card(s, 0.5, y, 12.3, 0.62)
    txt(s, 0.7, y + 0.14, 1.3, 0.35, h, 15, GOLD, True)
    txt(s, 2.1, y + 0.14, 10.4, 0.38, b, 15, WHITE)
footer(s, 3)
notes(
    s,
    """SLIDE 3  ·  1:15–1:55  ·  read this

The purpose of the study was to design and evaluate that loop as dispatcher support — not as an autonomous vehicle.

Four objectives. One: show the gap. Two: build the three parts. Three: choose the remaining-time threshold, called delta. Four: measure travel time and wait against four baselines.

Delta is a policy. If remaining time from where the vehicle is now grows by more than delta, we offer a new path. Alpha of point-zero-five is the statistical significance level. They share the digits zero-point-zero-five. They are not the same thing.

This talk spends most of the remaining time on Objectives 3 and 4, because that is the new evidence.""",
)


# ----- 4 framework -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.45, "How the loop works", 26, WHITE, True, "Cambria")
steps = [
    ("1", "Observe", "Last 60 minutes of detector speeds — 12 frames, five minutes each."),
    ("2", "Forecast", "Two-layer GRU, 64 units, dropout 0.2. Next 30 minutes — 6 frames."),
    ("3", "Cost", "Predicted miles per hour become travel time on each detector-to-detector edge."),
    ("4", "Route", "Time-dependent A* from origin to destination using those changing costs."),
    ("5", "Update", "If remaining time from the current position grows by more than δ, offer a new path."),
    ("6", "Decide", "The dispatcher accepts or rejects. The vehicle is not self-driving."),
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
    """SLIDE 4  ·  1:55–2:45  ·  read this

Walk the six boxes left to right, then down.

Box 1. We look at the last hour of detector speeds.

Box 2. A two-layer GRU forecasts the next half hour.

Box 3. Those speeds become the time to cross each road.

Box 4. Time-dependent A-star picks a path. Edge cost depends on when the vehicle would enter that road, not only on now.

Box 5. As the vehicle moves, remaining time is from here, not from the station. If that remaining time grows by more than delta, we offer a new path. The observation window slides forward every five minutes, so a jam that appears mid-trip can be seen.

Box 6. A person accepts or rejects. This is decision support.""",
)


# ----- 5 methods -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.4, "What was measured, and how the numbers stay honest", 24, WHITE, True, "Cambria")
card(s, 0.45, 0.8, 6.1, 5.55)
txt(s, 0.7, 0.98, 5.6, 0.35, "Design of the 900 journeys", 16, GOLD, True)
bullets(
    s, 0.7, 1.45, 5.6, 4.6,
    [
        "METR-LA: 207 detectors, 34,272 five-minute speed frames. This is the routing graph: 207 nodes, 1,515 edges, a speed on every edge.",
        "PEMS-BAY: 325 detectors. A second GRU only. Not a second routing city.",
        "75 origin–destination pairs × 3 traffic regimes × 4 values of δ = 900 journeys.",
        "Regimes: peak (slowest quarter of test windows), off-peak (fastest quarter), incident (40% slowdown on the planned corridor).",
        "Four baselines: B1 current Dijkstra; B2 historical A*; B3 reactive A* (one replan when the jam is visible); B4 oracle (actual future speeds).",
    ],
    size=13, space_after=8,
)
card(s, 6.8, 0.8, 6.1, 5.55)
txt(s, 7.05, 0.98, 5.6, 0.35, "What I did so the comparison is fair", 16, GOLD, True)
bullets(
    s, 7.05, 1.45, 5.6, 4.6,
    [
        "Split time 70 / 15 / 15 before windowing. Scaler fitted on training rows only — no leakage from later weeks.",
        "The forecast chooses the path. Journey time is then walked on actual future speeds. We do not score a method on its own predictions.",
        "Same origin, destination, and clock for every method. That is what N will mean on the result figures.",
        "Incidents sit on Dijkstra’s planned corridor, so the vehicle actually meets the disruption.",
        "I used the fully instrumented detector graph, not a sparse street map with guessed speeds. Percentages describe that graph.",
    ],
    size=13, space_after=8,
)
footer(s, 5)
notes(
    s,
    """SLIDE 5  ·  2:45–4:00  ·  read this

Two datasets, two models. A GRU cannot take two hundred and seven sensors and three hundred and twenty-five sensors in one tensor. Routing uses only Los Angeles, so the graph and the speeds belong to the same city.

The routing graph is the detector adjacency: two hundred and seven nodes, one thousand five hundred and fifteen directed edges, a measured speed on every edge. I chose that graph on purpose. A downtown street extract would have left most roads without a sensor. I did not want travel times invented on unmapped edges.

Nine hundred journeys: seventy-five origin–destination pairs, times three traffic regimes, times four delta values. Origin–destination means a start detector and an end detector. They were sampled to be reachable.

Three regimes. Peak: the slowest quarter of test windows. Off-peak: the fastest quarter — a negative control; a forecast and a current map should agree. Incident: after twenty percent of the planned Dijkstra time, speeds on that corridor drop to forty percent. The vehicle meets the jam.

Four baselines. B1 is dispatch practice — Dijkstra on now. B2 is a typical day. B3 is allowed one replan from the latest snapshot when the jam becomes visible, with no thirty-minute forecast. B4 is an oracle with actual future speeds. We must not beat B4. If we did, the experiment would be broken.

Honesty of the clock: every method is then driven on the real future speeds. Predicted costs pick the path; they do not mark the path.""",
)


# ----- 6 prediction -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.22, 12, 0.4, "Objective 2 — did the GRU forecast usable speeds?", 24, WHITE, True, "Cambria")
stats = [
    ("3.48 mph", "METR-LA test MAE\nRMSE 6.04 mph  ·  27 epochs"),
    ("2.38 mph", "PEMS-BAY test MAE\nseparate model  ·  79 epochs"),
    ("60 → 30 min", "Input 12 steps  ·  output 6 steps\nmatched to a typical response"),
]
for i, (n, lab) in enumerate(stats):
    card(s, 0.45 + i * 4.2, 0.8, 4.0, 1.85)
    txt(s, 0.55 + i * 4.2, 0.95, 3.8, 0.7, n, 26, GOLD, True, "Cambria", PP_ALIGN.CENTER)
    txt(s, 0.55 + i * 4.2, 1.7, 3.8, 0.75, lab, 13, WHITE, False, "Calibri", PP_ALIGN.CENTER)
card(s, 0.45, 2.9, 12.4, 3.45)
txt(s, 0.7, 3.1, 12.0, 0.35, "How to read these errors", 16, GOLD, True)
bullets(
    s, 0.7, 3.55, 11.9, 2.55,
    [
        "MAE is mean absolute error: on average, the forecast is 3.48 miles per hour off on held-out Los Angeles detectors.",
        "On freeways that is small enough to rank a quiet corridor against a slowing one. It is not a replacement for the dispatcher.",
        "The Bay model is a second-city check of the same architecture. Lower MAE there reflects smoother Bay Area speeds, not a failed Los Angeles model.",
        "A heavier graph network can beat this MAE. I kept a two-layer GRU so the whole loop still answers inside one second. The routing tables use the 27-epoch Los Angeles checkpoint.",
    ],
    size=15, space_after=8,
)
footer(s, 6)
notes(
    s,
    """SLIDE 6  ·  4:00–5:00  ·  read this

Objective 2. Can a light GRU forecast the next half hour well enough to rank roads?

On Los Angeles, test mean absolute error is 3.48 miles per hour. Root mean square error is 6.04. Training stopped at 27 epochs. On the Bay Area, a separate model, 2.38 miles per hour after 79 epochs.

Mean absolute error means: ignore sign, average the miss. Three and a half miles per hour on a freeway is enough to tell a still-moving corridor from one that is about to clog. It is not centimetre-accurate positioning.

The Bay error is lower because those freeways are smoother. That is not Los Angeles “failing.” I never routed Bay speeds on Los Angeles edges.

I did not bake off a graph neural net in this study. Those models can win on raw MAE. They also cost more at every five-minute refresh. The dispatch constraint was a combined wait well under one second. The GRU is the predictor that fitted that budget.""",
)


# ----- 7 obj 3 figure -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.18, 12, 0.38, "Objective 3 — which remaining-time threshold?", 22, WHITE, True, "Cambria")
txt(
    s, 0.5, 0.52, 12.3, 0.28,
    "Figure: travel-time reduction versus Dijkstra, and replans per journey, at each δ.  N = 225 journeys per δ  (75 pairs × 3 regimes).",
    13, ICE,
)
add_picture_safe(s, FIG / "fig3_delta_sensitivity.png", 0.25, 0.85, w=8.15)
card(s, 8.55, 0.85, 4.4, 5.55)
txt(s, 8.75, 1.0, 4.05, 0.32, "What the figure shows", 15, GOLD, True)
txt(
    s, 8.75, 1.4, 4.05, 4.75,
    "δ = 0.05 means: offer a new path if remaining time from here grows by 5%.\n\n"
    "Four policies: 5%, 10%, 15%, 20%.\n\n"
    "The reduction line is flat. ANOVA F ≈ 0.001, p = 1.00 — the four means are interchangeable.\n\n"
    "Incidents still replan about once at every δ. A 40% corridor drop exceeds a 20% remaining-time rise.\n\n"
    "I therefore recommend δ = 0.20: same travel time, slightly fewer extra alerts.\n\n"
    "0.10 was the planned mid-range candidate before measurement. It is not the measured default.",
    13, WHITE,
)
footer(s, 7)
notes(
    s,
    """SLIDE 7  ·  5:00–6:20  ·  point at the figure, then read

This figure is Objective 3. Left side: how much travel time we save versus Dijkstra, at each delta. Right side: how often we replan.

N equals 225 on each delta. That is seventy-five origin–destination pairs, times the three traffic regimes. We are pooling peak, off-peak, and incident here. The next slides split the regimes.

Look at the reduction line. It does not move. Five percent, ten, fifteen, twenty — about five and three-quarter percent overall versus Dijkstra in every case. The ANOVA F is about 0.001, p equals 1.00. That does not mean the study failed. It means the four policies produce the same travel time.

Why? In the incident regime, corridor speed falls by forty percent. Remaining time jumps by more than twenty percent. So even the strictest policy, delta 0.20, still fires. About one replan per incident journey at every setting.

When travel time is the same, decision support prefers the quieter alert. That is delta 0.20. Replans overall fall slightly from 0.45 to 0.39.

Chapter 3 put 0.10 in the middle of a five-to-twenty percent band as the value to test. After measurement, 0.20 is the default. Delta is not alpha. Alpha stays point-zero-five for the t-tests.""",
)


# ----- 8 obj 4 seconds figure -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.18, 12, 0.38, "Objective 4 — realised journey time in seconds", 22, WHITE, True, "Cambria")
txt(
    s, 0.5, 0.52, 12.3, 0.28,
    "Figure: mean travel time (seconds). Same 75 pairs and clock for every method. Incident, peak, and off-peak are separate groups.",
    13, ICE,
)
add_picture_safe(s, FIG / "fig1_travel_time_comparison.png", 0.2, 0.85, w=8.15)
card(s, 8.5, 0.85, 4.45, 5.55)
txt(s, 8.7, 1.0, 4.1, 0.32, "Read the bars", 15, GOLD, True)
txt(
    s, 8.7, 1.4, 4.1, 4.75,
    "Incident — the operational result\n"
    "  Dijkstra          728 s\n"
    "  Framework         599 s\n"
    "  Reactive A*       604 s\n"
    "  Oracle            581 s\n\n"
    "Peak — small, real gap\n"
    "  Framework         506 s\n"
    "  Dijkstra          513 s\n\n"
    "Off-peak — negative control\n"
    "  Both about        403 s\n\n"
    "The framework stays slower than the oracle. That is what an honest ceiling looks like.",
    13, WHITE,
)
footer(s, 8)
notes(
    s,
    """SLIDE 8  ·  6:20–7:40  ·  point at the three clusters

Objective 4. These bars are mean journey time in seconds — clock time from origin to destination after we drive every method on the real future speeds.

Start with incident, the tall cluster. Dijkstra, the current-map path, averages 728 seconds. The framework averages 599 seconds. That is about two minutes and ten seconds saved on that test graph when the planned road is disrupted. Reactive A-star, which replans once the jam is already on the snapshot, is 604 seconds — close to us. The oracle, with perfect future knowledge, is 581. We sit a little behind the oracle, as we must.

Why is reactive close in incidents? Once the slowdown is visible in current speeds, a thirty-minute forecast adds little. The value of the GRU is anticipatory: it can divert before the vehicle is fully committed. That is the keen reading of this figure. We are not claiming to dominate a reactive router after the jam is obvious.

Peak. Both methods are around 510 seconds. Widespread congestion leaves few quiet alternatives, so looking ahead helps only modestly: 506 versus 513.

Off-peak. Every serious method sits near 403 seconds. Empty roads are the negative control. A forecast and a current map should agree. They do. That is success, not a dead model.""",
)


# ----- 9 obj 4 percent figure -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.18, 12, 0.38, "Objective 4 — percentage versus Dijkstra", 22, WHITE, True, "Cambria")
txt(
    s, 0.5, 0.52, 12.3, 0.28,
    "Figure: mean % reduction versus Dijkstra.  N = 300 per regime  (75 pairs × 4 values of δ).  Positive = faster than current-map dispatch.",
    13, ICE,
)
add_picture_safe(s, FIG / "fig2_reduction_by_scenario.png", 0.2, 0.85, w=8.2)
card(s, 8.55, 0.85, 4.4, 5.55)
txt(s, 8.75, 1.0, 4.05, 0.32, "What N and % mean", 15, GOLD, True)
txt(
    s, 8.75, 1.4, 4.05, 4.75,
    "N = 300 is 75 pairs pooled across the four δ values. Table 4.5 already showed δ does not change time, so pooling is valid.\n\n"
    "Incident  +16.19%\n  t = 26.43,  p < .001\n  about 1.03 replans\n\n"
    "Peak  +1.03%\n  t = 3.81,  p = .0002\n\n"
    "Off-peak  +0.01%\n  p = .90  — not significant\n\n"
    "Overall versus Dijkstra  +5.74%\n"
    "versus historical A*  +7.39%\n"
    "versus reactive A*  +0.61%\n"
    "versus oracle  −1.69%\n\n"
    "The 16% figure is the incident regime. It is not a promise for every trip.",
    12, WHITE,
)
footer(s, 9)
notes(
    s,
    """SLIDE 9  ·  7:40–9:10  ·  this is the headline figure — go slowly

This figure is the same experiment as the seconds, now as a percentage against Dijkstra.

N equals 300 in each regime. That is seventy-five pairs, times four delta values. We can pool delta because Objective 3 showed travel time does not depend on which of the four policies we pick. N is not seventy-five here, and it is not nine hundred. Nine hundred is the whole study. Three hundred is one regime.

Percentage reduction: how much shorter the framework journey is than Dijkstra’s, on the same origin, destination, and clock. Positive means we were faster.

Incident: plus 16.19 percent. t is 26.43, p less than .001. About one replan per journey. That is the result that matches the purpose: when the planned corridor breaks, looking thirty minutes ahead and triggering on remaining time cuts realised delay.

Peak: plus 1.03 percent. Statistically detectable, p equals .0002. Operationally small. The network is busy in every direction.

Off-peak: plus 0.01 percent, p equals .90. Not significant. The negative control held.

Overall plus 5.74 percent is a mixture of those three worlds. If you quote one number from this talk, quote 16 percent under incidents, not 5.74 percent as if it applied to every ambulance.

Versus historical A-star we are 7.39 percent faster — an average day is not enough. Versus reactive A-star, 0.61 percent. I report that small gap on purpose. Versus the oracle we are 1.69 percent slower. The ceiling is intact.""",
)


# ----- 10 latency figure -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.18, 12, 0.38, "Objective 4 — does the loop fit a dispatch second?", 22, WHITE, True, "Cambria")
txt(
    s, 0.5, 0.52, 12.3, 0.28,
    "Figure: time-dependent A* search time and GRU inference time. Combined wait is the sum. Target is 1,000 milliseconds.",
    13, ICE,
)
add_picture_safe(s, FIG / "fig4_computational_performance.png", 0.2, 0.85, w=8.2)
card(s, 8.55, 0.85, 4.4, 5.55)
txt(s, 8.75, 1.0, 4.05, 0.32, "Dispatcher wait", 15, GOLD, True)
txt(
    s, 8.75, 1.45, 4.05, 4.6,
    "Time-dependent A*    0.37 ms\n"
    "GRU inference         39.3 ms\n"
    "Combined              ≈ 40 ms\n\n"
    "Dispatch cap          1,000 ms\n\n"
    "Search is not the bottleneck. The predictor is. The loop still returns in far less than one second.\n\n"
    "At 207 nodes, no heavy graph preprocessing was required, so edge times can refresh every five minutes.",
    14, WHITE,
)
footer(s, 10)
notes(
    s,
    """SLIDE 10  ·  9:10–10:00  ·  point at the two bars

Latency. The operational cap was one thousand milliseconds — one second — so a recommendation can be issued inside a dispatch click.

Time-dependent A-star averages 0.37 milliseconds. The GRU averages 39.3 milliseconds. Combined, about 40 milliseconds. That combined figure is the system wait. Do not quote 0.37 as if the dispatcher only waits for search.

The predictor is the slower part, and the loop still fits comfortably inside one second.

I did not pre-build a continental contraction hierarchy. At two hundred and seven nodes it was unnecessary. That is useful: edge weights can be rewritten every five minutes when a new forecast arrives.""",
)


# ----- 11 limits + what was already done -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.28, 12, 0.4, "Limits, and what this design already did about them", 22, WHITE, True, "Cambria")
card(s, 0.45, 0.8, 6.1, 5.55)
txt(s, 0.7, 0.98, 5.6, 0.4, "What these tables do not measure", 16, GOLD, True)
bullets(
    s, 0.7, 1.5, 5.6, 4.5,
    [
        "METR-LA and PEMS-BAY are United States freeway detectors. They are not Nairobi mixed traffic.",
        "The 900 journeys used 100% detector coverage. The percentages describe that graph.",
        "PEMS-BAY was a second GRU, not a second 900-run routing city.",
        "A 10–30% coverage run, as a sparse-sensor analogue, was not executed.",
        "One vehicle. Multi-unit interference was not modelled.",
    ],
    size=14, space_after=9,
)
card(s, 6.8, 0.8, 6.1, 5.55)
txt(s, 7.05, 0.98, 5.6, 0.4, "What I already did to contain those risks", 16, GOLD, True)
bullets(
    s, 7.05, 1.5, 5.6, 4.5,
    [
        "Did not invent speeds on unmapped streets: routed only on fully instrumented detector links.",
        "Did not leak the future into training: chronological split; scaler on train only.",
        "Did not mark paths with predicted time: scored every method on actual future speeds.",
        "Did not compare only with weak dispatch: included reactive A* and an oracle.",
        "Did not assume delta: swept 5–20% and let travel time decide. Next: downsample this same 100% graph to 10–30% and repeat the 900-run.",
    ],
    size=14, space_after=9,
)
footer(s, 11)
notes(
    s,
    """SLIDE 11  ·  10:00–11:20  ·  read steadily — this is the honesty slide

These percentages describe Los Angeles freeway detectors with a sensor on every edge. Transfer to a mixed-traffic city needs local sensors. That is a real limit, not a hidden error. Here is what I already did about it.

I did not route on a sparse street map and fill missing roads with guessed free-flow. I used the detector graph so every edge had a measured speed. The honest next step is to downsample that same graph to ten or thirty percent coverage and repeat the nine hundred journeys — not to pretend this 16 percent is already a sparse-city number.

I stopped the future leaking into the past: time-ordered split, scaler fitted on training only.

I stopped a method looking good because it was scored on its own forecast: everyone is walked on actual future speeds.

I stopped a weak baseline making 16 percent look larger than it is: reactive A-star and an oracle are in the table. The small gap to reactive, and the small gap behind the oracle, are part of the result.

PEMS-BAY shows the architecture still predicts in a second city. It does not yet show routing there. That is further work, with a Bay routing graph.

Single vehicle. Fleet interference is out of scope.

If there is a next study, it starts from this 100 percent detector graph and thins the sensors.""",
)


# ----- 12 close -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.12)
txt(s, 0.5, 0.32, 12, 0.5, "What to take from the 900 journeys", 24, WHITE, True, "Cambria")
take = [
    ("1", "When the planned corridor is disrupted, mean time falls from 728 s to 599 s versus current-map Dijkstra — 16.19%, about one replan."),
    ("2", "Travel time does not depend on which δ in 5–20% we pick. The operational default is 0.20: same time, quieter alerts."),
    ("3", "The loop answers in about 40 milliseconds. The binding constraint for deployment is local sensor coverage, not compute."),
]
for i, (n, t) in enumerate(take):
    y = 1.05 + i * 1.35
    card(s, 0.5, y, 12.3, 1.2)
    txt(s, 0.75, y + 0.3, 0.7, 0.55, n, 28, GOLD, True, "Cambria")
    txt(s, 1.6, y + 0.22, 10.8, 0.8, t, 16, WHITE)
txt(s, 0.5, 5.3, 12.3, 0.4, "Thank you. I welcome your questions.", 20, ICE, True, "Cambria", PP_ALIGN.CENTER)
txt(
    s, 0.5, 5.85, 12.3, 0.45,
    "Freshia Njoki Macharia  ·  PA206/S/25427/24  ·  Kirinyaga University",
    14, MUTED, False, "Calibri", PP_ALIGN.CENTER,
)
footer(s, 12)
notes(
    s,
    """SLIDE 12  ·  11:20–12:00  ·  then stop and wait for questions

Three sentences.

One. Under incident conditions the framework cut current-map Dijkstra time by 16.19 percent — about 599 seconds versus 728 — with about one replan.

Two. Delta from 5 to 20 percent did not change travel time. I recommend 0.20.

Three. Combined wait is about 40 milliseconds. Compute is not the barrier. Sensors are.

Thank you. I welcome your questions.

--- If a question comes, answer in one of these frames ---

N: 900 is the whole study. 225 is one delta across three regimes. 300 is one regime across four deltas.

Why not Nairobi numbers: I needed a public, fully instrumented archive so the 900-run can be repeated. The method transfers; these percentages do not, until local detectors exist.

Why so close to reactive A*: once the jam is on the snapshot, a 30-minute forecast adds little. The gain is before that.

Why p = 1.00 on delta: the four policies are interchangeable on time, not “the experiment found nothing.”

Why off-peak is zero: that was the control. Empty roads should not need a forecast.

Oracle: we are 1.69% slower. Required.

Code: GitHub repository Emergency_Routing; tables match results/full_report.txt.""",
)

prs.save(str(OUT))
print("Wrote", OUT, "slides", len(prs.slides))
