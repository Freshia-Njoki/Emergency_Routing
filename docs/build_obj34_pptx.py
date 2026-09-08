"""Build the 15-minute findings seminar PPT with speaker notes.

Output:
  docs/Presentation_GRU_Emergency_Routing_Findings.pptx

Run: python docs/build_obj34_pptx.py
Open Presenter View for speaker notes.
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
OUT = ROOT / "docs" / "Presentation_GRU_Emergency_Routing_Findings.pptx"
FIG = ROOT / "results" / "simulation" / "figures"
FIG_LAT = ROOT / "docs" / "article_figures" / "figure6_latency.png"
TOTAL = 13


def set_bg(slide, rgb=NAVY):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb


def bar(slide, top=0, height=0.08, color=GOLD):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(top), Inches(13.333), Inches(height)
    )
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()


def page_num(slide, n, total=TOTAL):
    t = slide.shapes.add_textbox(Inches(12.35), Inches(7.15), Inches(0.8), Inches(0.25))
    p = t.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    r = p.add_run()
    r.text = f"{n} / {total}"
    r.font.size = Pt(10)
    r.font.color.rgb = MUTED
    r.font.name = "Calibri"


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


def multiline(slide, l, t, w, h, text, size=14, color=WHITE, bold=False, line_space=1.15):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    lines = text.strip().split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(4)
        p.line_spacing = line_space
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = "Calibri"
    return box


def bullets(slide, l, t, w, h, items, size=14, color=WHITE, space_after=6):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
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
        return False
    kwargs = {}
    if w:
        kwargs["width"] = Inches(w)
    if h:
        kwargs["height"] = Inches(h)
    slide.shapes.add_picture(str(path), Inches(l), Inches(t), **kwargs)
    return True


def slide_header(slide, n, title, intro=None):
    bar(slide, 0, 0.08)
    txt(slide, 0.5, 0.22, 12.2, 0.45, title, 24, WHITE, True, "Cambria")
    if intro:
        txt(slide, 0.5, 0.62, 12.3, 0.35, intro, 13, ICE)
    page_num(slide, n)


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

# ----- 1 Title -----
s = prs.slides.add_slide(blank)
set_bg(s)
bar(s, 0, 0.08)
txt(s, 0.6, 0.45, 12, 0.35, "KIRINYAGA UNIVERSITY  ·  MSc COMPUTER SCIENCE", 14, ICE)
txt(
    s, 0.6, 1.0, 12, 1.6,
    "GRU-Based Predictive Route Optimisation\nfor Emergency Vehicle Navigation",
    32, WHITE, True, "Cambria",
)
sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(2.75), Inches(3.0), Inches(0.06))
sh.fill.solid()
sh.fill.fore_color.rgb = GOLD
sh.line.fill.background()
txt(s, 0.6, 3.05, 12, 0.35, "Freshia Njoki Macharia  ·  PA206/S/25427/24", 18, WHITE)
txt(s, 0.6, 3.5, 12, 0.35, "Supervisors: Dr Gilbert Langat  ·  Dr Stephen Mageto", 15, MUTED)
txt(
    s, 0.6, 4.2, 12, 0.55,
    "Design and evaluation reported in a companion journal article.",
    14, GOLD,
)
page_num(s, 1)
notes(
    s,
    """Chair, supervisors, examiners — thank you. I am Freshia Njoki Macharia.

This seminar reports a dispatcher-support system for emergency routing. It forecasts traffic speeds for the next 30 minutes, computes a time-dependent path, and offers a new path only when remaining travel time has truly worsened. The dispatcher keeps final authority.

Before I go to the results, I should mention that the design and evaluation of this framework is reported in my first journal article — Design and Evaluation of a GRU-Based Predictive Routing Framework for Emergency Vehicles. I am grateful for the opportunity to present the defended findings here, especially Objectives 3 and 4.

Evidence: 900 matched journeys on the METR-LA detector graph. Most of this talk focuses on the threshold test and journey-time results.""",
)

# ----- 2 Problem -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(s, 2, "Statement of the problem")
card(s, 0.5, 0.95, 12.3, 1.55)
txt(
    s, 0.75, 1.15, 11.8, 1.2,
    "A route that is shortest at dispatch is optimal only for the speeds seen at that moment. "
    "If a corridor slows 15–30 minutes later, the vehicle is already committed. "
    "That is the failure this study treats.",
    16, WHITE,
)
items = [
    ("Present dispatch practice", "A current-map shortest path — Dijkstra, or A* — using speeds available at departure."),
    ("Research gap", "Strong predictors and strong time-dependent routers are usually published apart. "
     "An emergency loop that joins a learned forecast, time-dependent search, and a tested remaining-time trigger, inside one second, is missing."),
    ("Data and test setting", "Public freeway detector archives (METR-LA; PEMS-BAY). Local mixed traffic is the next deployment step."),
]
for i, (h, body) in enumerate(items):
    y = 2.65 + i * 1.35
    card(s, 0.5, y, 12.3, 1.22)
    txt(s, 0.75, y + 0.12, 11.8, 0.3, h, 15, GOLD, True)
    txt(s, 0.75, y + 0.44, 11.8, 0.65, body, 14, WHITE)
notes(
    s,
    """The problem is straightforward. At dispatch we compute a shortest path from the speeds on the map right now. That path is optimal only for those speeds. If a corridor slows 15–30 minutes later, the vehicle is already committed.

That is how most computer-aided dispatch still works: Dijkstra, or A*, on a current snapshot.

The literature has strong predictors and strong time-dependent routers, but they are usually published separately. What was missing is one emergency loop — forecast, time-dependent search, and a tested remaining-time trigger — all inside one second.

I measured on public loop-detector archives so the run can be repeated. METR-LA is the routing city. PEMS-BAY checks the same predictor in a second city only.""",
)

# ----- 3 Objectives -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(s, 3, "Study purpose and research objectives")
card(s, 0.5, 0.95, 12.3, 1.25)
txt(s, 0.75, 1.05, 11.8, 0.25, "Purpose", 14, GOLD, True)
txt(
    s, 0.75, 1.32, 11.8, 0.75,
    "To design and evaluate a dispatcher-support framework that cuts realised emergency-vehicle "
    "travel time by joining GRU speed forecasts, time-dependent A*, and a remaining-time threshold.",
    15, WHITE,
)
rqs = [
    ("Obj. 1", "Map the gaps among emergency routing, traffic prediction, and time-dependent pathfinding."),
    ("Obj. 2", "Build the three-part system: GRU predictor, time-dependent A*, remaining-time controller."),
    ("Obj. 3", "Which remaining-time threshold δ ∈ {5%, 10%, 15%, 20%} balances travel time against extra alerts."),
    ("Obj. 4", "Whether the loop cuts realised travel time versus four baselines while answering inside one second."),
]
for i, (h, b) in enumerate(rqs):
    y = 2.35 + i * 0.72
    card(s, 0.5, y, 12.3, 0.64)
    txt(s, 0.7, y + 0.15, 1.35, 0.35, h, 14, GOLD, True)
    txt(s, 2.15, y + 0.15, 10.4, 0.38, b, 14, WHITE)
txt(s, 0.5, 5.35, 12.3, 0.35, "Objectives 1–2 produce the artefact. Objectives 3–4 are the evaluation evidence.", 13, ICE)
notes(
    s,
    """The purpose was to design and evaluate that loop as dispatcher support — not as an autonomous vehicle.

Four objectives. One maps the gap. Two builds the three parts. Three chooses the remaining-time threshold, delta. Four measures journey time and system response time against four baselines.

This talk focuses on Objectives 3 and 4.

Delta is a policy: if remaining time from where the vehicle is now grows by more than delta, we offer a new path. Alpha = 0.05 is the significance level for the t-tests. They share digits. They are not the same thing.""",
)

# ----- 4 Framework -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(
    s, 4, "Integrated routing framework",
    "Figure 1. End-to-end loop: observe, forecast, route, update — dispatcher retains authority.",
)
steps = [
    ("1", "Observe", "Last 60 minutes of detector speeds — 12 frames, five minutes each."),
    ("2", "Forecast", "Two-layer GRU, 64 units, dropout 0.2. Next 30 minutes — 6 frames."),
    ("3", "Cost", "Predicted mph become travel time on each detector-to-detector edge."),
    ("4", "Route", "Time-dependent A* from origin to destination using those changing costs."),
    ("5", "Update", "If remaining time from the current position grows by more than δ, offer a new path."),
    ("6", "Decide", "The dispatcher accepts or rejects. The vehicle is not self-driving."),
]
for i, (n, h, b) in enumerate(steps):
    col, row = i % 3, i // 3
    x, y = 0.45 + col * 4.2, 1.05 + row * 2.55
    card(s, x, y, 4.0, 2.35)
    txt(s, x + 0.2, y + 0.2, 3.6, 0.45, n, 28, GOLD, True, "Cambria")
    txt(s, x + 0.2, y + 0.75, 3.6, 0.4, h, 17, ICE, True)
    txt(s, x + 0.2, y + 1.25, 3.6, 0.85, b, 13, WHITE)
notes(
    s,
    """Walk the six steps in order.

One — observe the last 60 minutes of detector speeds.
Two — a two-layer GRU forecasts the next 30 minutes.
Three — predicted speeds become edge travel times.
Four — time-dependent A* picks a path. Edge cost depends on when the vehicle would enter that road, not only on now.
Five — if remaining time from the current position grows by more than delta, offer a new path.
Six — a person accepts or rejects. This is decision support, not a self-driving ambulance.""",
)

# ----- 5 Design -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(
    s, 5, "Research design and fair comparison",
    "This slide presents how the 900 journeys were built and why the comparison is fair.",
)
card(s, 0.45, 1.05, 6.1, 5.35)
txt(s, 0.7, 1.2, 5.6, 0.32, "Simulation design (N = 900)", 15, GOLD, True)
bullets(
    s, 0.7, 1.6, 5.6, 4.6,
    [
        "Routing city: METR-LA — 207 detectors, 1,515 links, speed on every link (100% instrumented).",
        "Second dataset: PEMS-BAY — 325 detectors; second GRU only, not a second routing city.",
        "Total: 75 origin–destination pairs × 3 traffic scenarios × 4 δ values = 900 journeys.",
        "Scenarios: peak hour (slowest 25%), off-peak (fastest 25%, control), incident (corridor cut to 40% after 20% of B1 time).",
        "Baselines: B1 current Dijkstra · B2 historical static A* · B3 reactive A* (one replan) · B4 oracle (actual future speeds).",
    ],
    size=12, space_after=7,
)
card(s, 6.8, 1.05, 6.1, 5.35)
txt(s, 7.05, 1.2, 5.6, 0.32, "Steps taken for a fair test", 15, GOLD, True)
bullets(
    s, 7.05, 1.6, 5.6, 4.6,
    [
        "Time split 70 / 15 / 15; scaler fitted on training data only.",
        "Each method chooses its path; clock time is measured on actual future speeds.",
        "Same origin, destination, and start time for every method on every run.",
        "Incidents placed on Dijkstra's planned corridor so the vehicle meets the disruption.",
        "Results apply to this fully instrumented detector graph — not a sparse map with guessed speeds.",
    ],
    size=12, space_after=7,
)
notes(
    s,
    """This slide presents the experiment behind every result that follows.

Think of it as 900 fair races on the same Los Angeles freeway detector map. Every method starts at the same place, ends at the same place, and leaves at the same clock time.

Routing uses METR-LA only: 207 nodes and 1,515 links, all with real detector speeds. PEMS-BAY checks that the same GRU architecture works in a second city, but those Bay speeds were never used to route in Los Angeles.

900 = 75 origin–destination pairs × 3 traffic scenarios × 4 threshold settings.

Peak hour uses the slowest quarter of test windows. Off-peak uses the fastest quarter — our control. Incident slows the planned corridor to 40% of normal speed partway through the trip.

Four baselines are included. B1 is what dispatch often does today. B4 is the oracle with perfect future knowledge. We must not beat B4; if we did, the test would be wrong.

The forecast picks the route, but journey time is always scored on what actually happened on the road — not on the model's own prediction.""",
)

# ----- 6 Obj 2 brief -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(
    s, 6, "Objective 2: GRU forecast accuracy",
    "This slide presents whether the speed forecast is accurate enough to support routing — in brief, it is.",
)
stats = [
    ("3.48 mph", "METR-LA test MAE\nRMSE 6.04 mph · 27 epochs"),
    ("2.38 mph", "PEMS-BAY test MAE\nRMSE 4.49 mph · separate model · 79 epochs"),
    ("60 → 30 min", "Input 12 steps · output 6 steps\nForecast window"),
]
for i, (n, lab) in enumerate(stats):
    card(s, 0.45 + i * 4.2, 1.05, 4.0, 1.75)
    txt(s, 0.55 + i * 4.2, 1.2, 3.8, 0.65, n, 26, GOLD, True, "Cambria", PP_ALIGN.CENTER)
    txt(s, 0.55 + i * 4.2, 1.9, 3.8, 0.7, lab, 12, WHITE, False, "Calibri", PP_ALIGN.CENTER)
card(s, 0.45, 3.0, 12.4, 2.35)
bullets(
    s, 0.7, 3.2, 11.9, 2.0,
    [
        "METR-LA (routing city): test MAE 3.48 mph, RMSE 6.04 mph — enough to rank a quiet link against a slowing one.",
        "PEMS-BAY (check only): test MAE 2.38 mph, separate model — smoother freeway speeds, not a failed Los Angeles model.",
        "A heavier model could lower MAE further; this GRU was kept so the full loop still responds in ≈40 ms.",
    ],
    size=14, space_after=8,
)
txt(
    s, 0.5, 5.55, 12.3, 0.35,
    "The 60→30 box is model input/output (1 h observed → 30 min forecast), not journey-time saved.",
    12, ICE,
)
notes(
    s,
    """This slide presents Objective 2 briefly, because Objectives 3 and 4 need a forecast that is good enough — not perfect.

On held-out Los Angeles data, the GRU is wrong by about 3.48 mph on average. On freeways that is enough to tell a corridor that is still moving from one that is about to clog.

The 60→30 box is not time saved on a trip. It means: read 1 hour of past speeds, predict the next 30 minutes — six 5-minute steps — and feed those speeds into the router.

PEMS-BAY at 2.38 mph is a second-city check only. I kept this light GRU so inference stays near 39 ms and the whole system near 40 ms. Now we test the threshold and journey time.""",
)

# ----- 7 Obj 3 -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(
    s, 7, "Objective 3: Effect of threshold δ on travel time and replans",
    "This slide presents which remaining-time threshold δ to use: 5%, 10%, 15%, or 20%.",
)
txt(
    s, 0.5, 1.0, 12.3, 0.45,
    "N = 225 per δ = 75 origin–destination pairs × 3 traffic scenarios (peak, off-peak, incident). Scenarios are pooled here to test δ itself.",
    12, ICE,
)
add_picture_safe(s, FIG / "fig3_delta_sensitivity.png", 0.25, 1.45, w=7.5)
# Table 3
card(s, 8.0, 1.45, 4.85, 2.35)
txt(s, 8.15, 1.55, 4.55, 0.28, "Table 3. Threshold sensitivity", 13, GOLD, True)
rows = [
    ("δ", "vs Dijkstra", "Replans"),
    ("0.05", "+5.726%", "0.45"),
    ("0.10", "+5.748%", "0.44"),
    ("0.15", "+5.726%", "0.43"),
    ("0.20", "+5.767%", "0.39"),
]
for ri, row in enumerate(rows):
    y = 1.95 + ri * 0.32
    c0, c1, c2 = row
    bold = ri == 0 or c0 == "0.20"
    txt(s, 8.2, y, 0.7, 0.28, c0, 12, GOLD if bold else WHITE, bold)
    txt(s, 9.0, y, 1.5, 0.28, c1, 12, GOLD if c0 == "0.20" else WHITE, c0 == "0.20")
    txt(s, 10.55, y, 1.1, 0.28, c2, 12, GOLD if c0 == "0.20" else WHITE, c0 == "0.20")
txt(s, 8.15, 3.35, 4.55, 0.25, "Operational default: δ = 0.20", 12, GOLD, True)
multiline(
    s, 0.5, 5.55, 12.3, 1.35,
    "Figure 3. Travel-time reduction relative to current-map Dijkstra (left) and mean replans per journey (right) by δ. "
    "N = 225 per δ. ANOVA: F ≈ 0.001, p = 1.00. Recommended operational default: δ = 0.20.",
    11, ICE,
)
notes(
    s,
    """This slide presents Objective 3: which remaining-time threshold to recommend.

What is δ? If remaining travel time from where the vehicle is now grows by more than δ, the system offers a new path. The dispatcher still decides.

What is N here? For each δ value we ran 75 origin–destination pairs across 3 traffic scenarios — peak, off-peak, and incident. That is 75 × 3 = 225 journeys per δ. On this slide those scenarios are pooled because we ask one question: does δ change the outcome?

Look at the table. Mean reduction versus Dijkstra is about 5.7% at every δ — from 5.726% to 5.767%. Replans fall from 0.45 to 0.39 as δ rises.

What is ANOVA in this study? ANOVA asks: do these four threshold settings produce different travel times? We are not testing whether the framework beats Dijkstra here. We are testing whether 5% is better than 10%, 15%, or 20%.

What is F? F is how different the four groups are compared with random noise. F ≈ 0.001 is extremely close to zero — the four groups look almost identical.

What is p? p is the probability we would see this pattern if there were no real difference between thresholds. p = 1.00 means there is no evidence that any δ gives a different travel time. That is a valid result, not a failed experiment.

So why δ = 0.20? When travel time is the same, decision support should minimise unnecessary alerts. δ = 0.20 gives the same 5.7% saving with the fewest replans — 0.39 versus 0.45 at δ = 0.05.

Incidents still replan about once even at 20% because the corridor was cut to 40% speed. 0.10 was the pre-measurement mid-range candidate, not the operational default.""",
)

# ----- 8 Obj 4 seconds -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(
    s, 8, "Objective 4: Mean journey time by traffic scenario",
    "This slide presents mean realised journey time in seconds for each method and traffic scenario.",
)
add_picture_safe(s, FIG / "fig1_travel_time_comparison.png", 0.2, 1.05, w=8.0)
card(s, 8.4, 1.05, 4.55, 5.35)
txt(s, 8.6, 1.18, 4.15, 0.3, "Summary of main results", 14, GOLD, True)
multiline(
    s, 8.6, 1.55, 4.15, 4.6,
    "INCIDENT — principal case\n"
    "Dijkstra B1     727.5 s\n"
    "Static A* B2    723.2 s\n"
    "Reactive A* B3  603.7 s\n"
    "Framework       598.9 s\n"
    "Oracle B4       580.5 s\n\n"
    "PEAK HOUR\n"
    "Framework 506.3 s · Dijkstra 513.1 s\n\n"
    "OFF-PEAK (control)\n"
    "All methods ≈ 403 s\n\n"
    "Framework stays below the oracle (−1.69% overall). Valid upper bound.",
    12, WHITE,
)
multiline(
    s, 0.5, 6.35, 12.3, 0.55,
    "Figure 4. Mean realised travel time (seconds) on actual future speeds. N = 300 per traffic scenario (75 pairs × 4 δ values).",
    11, ICE,
)
notes(
    s,
    """This slide presents Objective 4 in seconds — clock time from start detector to end detector, after every method is driven on actual future speeds.

N on this slide: each scenario uses 300 journeys — 75 pairs × 4 δ values. We can pool δ because Objective 3 showed δ does not change travel time.

Start with incident — the main operational case. Dijkstra on the current map: 727.5 s. The framework: 598.9 s — about 129 s saved. Reactive A*: 603.7 s, close to us. Oracle: 580.5 s.

We stay below the oracle on purpose. The oracle knows the true future speeds. No real dispatcher can beat that. If our framework were faster than the oracle, the evaluation would be wrong. Sitting at 598.9 s versus 580.5 s shows a valid upper bound.

Peak hour: 506.3 s versus 513.1 s — a small but real gap when the network is congested everywhere.

Off-peak: all methods near 403 s. Empty roads are the control — no large gain is expected. That is success.""",
)

# ----- 9 Obj 4 percent -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(
    s, 9, "Objective 4: Percentage reduction versus baseline B1",
    "This slide presents the same journeys as percentages relative to current-map Dijkstra (B1).",
)
txt(s, 0.5, 1.0, 12.3, 0.3, "N = 300 per traffic scenario = 75 pairs × 4 δ values (δ pooled).", 12, ICE)
add_picture_safe(s, FIG / "fig2_reduction_by_scenario.png", 0.2, 1.35, w=8.0)
card(s, 8.4, 1.35, 4.55, 4.2)
txt(s, 8.6, 1.48, 4.15, 0.28, "Statistical summary", 14, GOLD, True)
stats_rows = [
    ("Scenario", "vs B1", "Significance"),
    ("Incident", "+16.19%", "t = 26.43, p < .001"),
    ("Peak hour", "+1.03%", "t = 3.81, p = .0002"),
    ("Off-peak", "+0.01%", "p = .90 (n.s.)"),
]
for ri, row in enumerate(stats_rows):
    y = 1.9 + ri * 0.45
    txt(s, 8.65, y, 1.5, 0.35, row[0], 12, GOLD if ri == 0 or row[0] == "Incident" else WHITE, ri == 0 or row[0] == "Incident")
    txt(s, 10.2, y, 1.0, 0.35, row[1], 12, GOLD if row[0] == "Incident" else WHITE, row[0] == "Incident")
    txt(s, 11.25, y, 1.5, 0.35, row[2], 11, WHITE)
multiline(
    s, 8.6, 4.0, 4.15, 1.5,
    "Overall:\n+5.74% vs B1\n+7.39% vs historical A*\n+0.61% vs reactive A*\n−1.69% vs oracle",
    11, ICE,
)
multiline(
    s, 0.5, 6.0, 12.3, 0.55,
    "Figure 5. Percentage reduction in mean travel time relative to B1 by traffic scenario. Positive = shorter journey. Quote +16.19% for incidents, not +5.74% alone.",
    11, ICE,
)
notes(
    s,
    """This slide presents the headline statistics as percentages against baseline B1 — current-map Dijkstra.

N = 300 means 75 origin–destination pairs, each tested at 4 δ values, within one traffic scenario. 900 is the whole study; 300 is one scenario.

Incident: +16.19%, t = 26.43, p < .001 — highly significant. About 1.03 replans per journey. This is the number to quote when you ask where the framework helps most.

Peak hour: +1.03%, t = 3.81, p = .0002 — statistically detectable, operationally modest.

Off-peak: +0.01%, p = .90 — not significant. The control worked.

Overall +5.74% mixes all three scenarios — do not present it as every ambulance saves 16%.

Versus historical A*: +7.39%. Versus reactive A*: +0.61% — once the jam is visible on the map, a 30-minute forecast adds little. Versus oracle: −1.69% — we must remain below perfect foresight.""",
)

# ----- 10 Latency -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(
    s, 10, "Objective 4: System response time",
    "This slide presents system response time — not driving time — against a one-second operational limit.",
)
lat_path = FIG_LAT if FIG_LAT.exists() else FIG / "fig4_computational_performance.png"
add_picture_safe(s, lat_path, 0.2, 1.05, w=8.0)
card(s, 8.4, 1.05, 4.55, 3.5)
txt(s, 8.6, 1.18, 4.15, 0.3, "Measured response time", 14, GOLD, True)
multiline(
    s, 8.6, 1.55, 4.15, 2.8,
    "Time-dependent A*     0.37 ms\n"
    "GRU inference          39.3 ms\n"
    "Combined system response  ≈ 40 ms\n\n"
    "One-second response limit  1,000 ms\n\n"
    "The predictor, not the router, is the main time cost.",
    13, WHITE,
)
multiline(
    s, 0.5, 5.0, 12.3, 1.2,
    "Figure 6. System response time of the prediction and routing modules against a one-second operational limit (1,000 ms). "
    "Combined response time is GRU inference plus time-dependent A* search. The 1,000 ms limit is the maximum allowed time to return a route recommendation after a dispatcher request.",
    11, ICE,
)
notes(
    s,
    """This slide presents compute time, not journey time.

The one-second response limit (1,000 ms) is the maximum time allowed to return a route recommendation after a dispatcher request.

Time-dependent A*: 0.37 ms. GRU inference: 39.3 ms. Combined: ≈40 ms — about 4% of the limit.

Do not quote 0.37 ms alone; the dispatcher waits for the combined ≈40 ms. The predictor is the slower part, but both modules are far below one second in every traffic scenario.

At 207 nodes, no heavy graph preprocessing was required, so edge weights can refresh every 5 minutes when a new forecast arrives.""",
)

# ----- 11 Limits -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(s, 11, "Study limitations and mitigations")
card(s, 0.45, 1.05, 6.1, 5.35)
txt(s, 0.7, 1.2, 5.6, 0.32, "Study limits", 15, GOLD, True)
bullets(
    s, 0.7, 1.6, 5.6, 4.5,
    [
        "METR-LA and PEMS-BAY are United States freeway detectors — not Nairobi mixed traffic.",
        "The 900 journeys used 100% detector coverage. Percentages describe that graph.",
        "A 10–30% coverage run as a sparse-sensor analogue was not executed.",
        "One vehicle. Multi-unit interference was not modelled.",
    ],
    size=13, space_after=8,
)
card(s, 6.8, 1.05, 6.1, 5.35)
txt(s, 7.05, 1.2, 5.6, 0.32, "Steps taken to reduce bias", 15, GOLD, True)
bullets(
    s, 7.05, 1.6, 5.6, 4.5,
    [
        "Routed only on fully instrumented detector links — no guessed speeds on unmapped streets.",
        "Chronological split; scaler on training only — no future leakage.",
        "Scored every method on actual future speeds, not on its own predictions.",
        "Included reactive A* and an oracle — not only weak dispatch.",
        "Swept δ from 5–20% and let travel time decide the operational default.",
    ],
    size=13, space_after=8,
)
notes(
    s,
    """These percentages describe Los Angeles freeway detectors with a sensor on every edge. They are not Nairobi mixed-traffic numbers. Transfer needs local sensors.

What I already did: no invented speeds on unmapped streets; no leakage into training; no scoring on own predictions; strong baselines included.

The honest next step is to thin this same 100% graph to 10–30% coverage and repeat the 900-run.

Single vehicle. Fleet interference is out of scope.""",
)

# ----- 12 Summary -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(s, 12, "Summary of principal findings")
take = [
    ("1", "Under incidents, mean time falls from 727.5 s to 598.9 s versus current-map Dijkstra — 16.19%, about one replan."),
    ("2", "Travel time does not depend on δ in 5–20%. Operational default: δ = 0.20 — same time, quieter alerts."),
    ("3", "Combined system response ≈ 40 ms. The main deployment constraint is sensor coverage, not compute."),
]
for i, (n, t) in enumerate(take):
    y = 1.15 + i * 1.35
    card(s, 0.5, y, 12.3, 1.2)
    txt(s, 0.75, y + 0.3, 0.7, 0.55, n, 28, GOLD, True, "Cambria")
    txt(s, 1.6, y + 0.22, 10.8, 0.8, t, 15, WHITE)
txt(s, 0.5, 5.2, 12.3, 0.4, "Thank you. I welcome your questions.", 20, ICE, True, "Cambria", PP_ALIGN.CENTER)
notes(
    s,
    """Three sentences.

One — under incident conditions, mean time falls from 727.5 s to 598.9 s versus current-map Dijkstra — 16.19%, about one replan.

Two — travel time does not depend on δ from 5% to 20%. I recommend δ = 0.20.

Three — combined system response is about 40 ms. The main deployment constraint is sensor coverage, not compute.

Thank you. I welcome your questions.""",
)

# ----- 13 Conclusions -----
s = prs.slides.add_slide(blank)
set_bg(s)
slide_header(s, 13, "Conclusions and recommendations")
card(s, 0.45, 1.05, 6.1, 5.35)
txt(s, 0.7, 1.2, 5.6, 0.32, "Conclusions by objective", 15, GOLD, True)
bullets(
    s, 0.7, 1.6, 5.6, 4.5,
    [
        "Obj 1 — Gap confirmed: prediction and time-dependent search need one emergency loop with a tested δ trigger inside 1 s.",
        "Obj 2 — Three components integrate on the 207-node graph; GRU MAE 3.48 mph (METR-LA), 2.38 mph (PEMS-BAY); combined response ≈ 40 ms.",
        "Obj 3 — Travel time equivalent across δ ∈ {5, 10, 15, 20}% (F ≈ 0.001, p = 1.00). Operational default: δ = 0.20.",
        "Obj 4 — Reduction vs B1 is scenario-specific: +16.19% incident, +1.03% peak, +0.01% off-peak; −1.69% vs oracle.",
    ],
    size=12, space_after=7,
)
card(s, 6.8, 1.05, 6.1, 5.35)
txt(s, 7.05, 1.2, 5.6, 0.32, "Recommendations", 15, GOLD, True)
bullets(
    s, 7.05, 1.6, 5.6, 4.5,
    [
        "Deploy where loop detectors already exist; at ≈40 ms against 1,000 ms, compute is not the constraint — sensor coverage is.",
        "Build METR-LA-compatible speed archives for local deployment before quoting these percentages in mixed traffic.",
        "Next studies: sparse-sensor downsampling (10–30%), multi-vehicle coordination, live feeds, field validation with dispatch operators.",
    ],
    size=12, space_after=8,
)
txt(
    s, 0.5, 6.45, 12.3, 0.35,
    "Full design and evaluation: companion journal article.",
    12, MUTED, False, "Calibri", PP_ALIGN.CENTER,
)
notes(
    s,
    """Each objective was met. The gap was confirmed and closed with a working loop. The threshold test showed δ does not change travel time; δ = 0.20 is the measured default. Journey-time gains are strongest under incident conditions — 16.19% versus current-map Dijkstra.

Recommendations: deploy where sensors exist; build local archives before claiming Nairobi numbers; repeat the 900-run on thinned sensor coverage.

The full design, baselines, and evaluation are documented in the companion journal article. Thank you.""",
)

prs.save(str(OUT))
print(f"Wrote {OUT} ({len(prs.slides)} slides)")
