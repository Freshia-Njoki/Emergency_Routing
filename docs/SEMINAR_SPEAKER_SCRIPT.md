# 15-minute seminar — read this in Presenter View

Open `docs/Freshia_Njoki_Obj34_Findings_Presentation.pptx`.  
**Slide Show → Presenter View** (or **View → Notes**).  
The notes on each slide are the same script as below. Speak them. Do not improvise numbers.

Clock: **finish the twelve slides by 12:00**. Leave **3 minutes** for questions.

---

## Slide 1 · 0:00–0:20 · Title

Chair, supervisors, examiners — thank you. I am Freshia Njoki Macharia.

This seminar reports a decision-support framework for emergency-vehicle routing. It forecasts traffic speeds for the next thirty minutes, computes a time-dependent path, and offers a new path only when remaining travel time has truly worsened.

I evaluated that loop on nine hundred matched journeys. The dispatcher keeps final authority.

I will go: problem, design, then the results — prediction, the threshold, journey time, and latency.

---

## Slide 2 · 0:20–1:15 · The problem

The operational problem is simple. At dispatch we compute a shortest path from the speeds on the map right now. That path is optimal only for those speeds. If a queue forms on the planned road fifteen or thirty minutes later, the vehicle is already on it.

That is how most computer-aided dispatch still works: Dijkstra, or A*, on a current snapshot.

The literature has excellent traffic predictors, and it has time-dependent shortest-path algorithms. They usually sit in different papers. What was missing is one emergency loop: learn the next half hour of speeds, route on those changing costs, and only interrupt the dispatcher when remaining time has really jumped — all inside one second.

I measured that loop on public loop-detector archives so another researcher can repeat it. METR-LA is the routing city. PEMS-BAY checks whether the same predictor still works in a second city.

---

## Slide 3 · 1:15–1:55 · Purpose and objectives

The purpose of the study was to design and evaluate that loop as dispatcher support — not as an autonomous vehicle.

Four objectives. One: show the gap. Two: build the three parts. Three: choose the remaining-time threshold, called delta. Four: measure travel time and wait against four baselines.

Delta is a policy. If remaining time from where the vehicle is now grows by more than delta, we offer a new path. Alpha of point-zero-five is the statistical significance level. They share the digits zero-point-zero-five. They are not the same thing.

This talk spends most of the remaining time on Objectives 3 and 4, because that is the new evidence.

---

## Slide 4 · 1:55–2:45 · How the loop works

Walk the six boxes left to right, then down.

Box 1. We look at the last hour of detector speeds.

Box 2. A two-layer GRU forecasts the next half hour.

Box 3. Those speeds become the time to cross each road.

Box 4. Time-dependent A-star picks a path. Edge cost depends on when the vehicle would enter that road, not only on now.

Box 5. As the vehicle moves, remaining time is from here, not from the station. If that remaining time grows by more than delta, we offer a new path. The observation window slides forward every five minutes, so a jam that appears mid-trip can be seen.

Box 6. A person accepts or rejects. This is decision support.

---

## Slide 5 · 2:45–4:00 · Design + fairness

Two datasets, two models. A GRU cannot take two hundred and seven sensors and three hundred and twenty-five sensors in one tensor. Routing uses only Los Angeles, so the graph and the speeds belong to the same city.

The routing graph is the detector adjacency: two hundred and seven nodes, one thousand five hundred and fifteen directed edges, a measured speed on every edge. I chose that graph on purpose. A downtown street extract would have left most roads without a sensor. I did not want travel times invented on unmapped edges.

Nine hundred journeys: seventy-five origin–destination pairs, times three traffic regimes, times four delta values. Origin–destination means a start detector and an end detector. They were sampled to be reachable.

Three regimes. Peak: the slowest quarter of test windows. Off-peak: the fastest quarter — a negative control; a forecast and a current map should agree. Incident: after twenty percent of the planned Dijkstra time, speeds on that corridor drop to forty percent. The vehicle meets the jam.

Four baselines. B1 is dispatch practice — Dijkstra on now. B2 is a typical day. B3 is allowed one replan from the latest snapshot when the jam becomes visible, with no thirty-minute forecast. B4 is an oracle with actual future speeds. We must not beat B4. If we did, the experiment would be broken.

Honesty of the clock: every method is then driven on the real future speeds. Predicted costs pick the path; they do not mark the path.

---

## Slide 6 · 4:00–5:00 · GRU errors

Objective 2. Can a light GRU forecast the next half hour well enough to rank roads?

On Los Angeles, test mean absolute error is 3.48 miles per hour. Root mean square error is 6.04. Training stopped at 27 epochs. On the Bay Area, a separate model, 2.38 miles per hour after 79 epochs.

Mean absolute error means: ignore sign, average the miss. Three and a half miles per hour on a freeway is enough to tell a still-moving corridor from one that is about to clog. It is not centimetre-accurate positioning.

The Bay error is lower because those freeways are smoother. That is not Los Angeles “failing.” I never routed Bay speeds on Los Angeles edges.

I did not bake off a graph neural net in this study. Those models can win on raw MAE. They also cost more at every five-minute refresh. The dispatch constraint was a combined wait well under one second. The GRU is the predictor that fitted that budget.

---

## Slide 7 · 5:00–6:20 · Figure — delta (point at the chart)

This figure is Objective 3. Left side: how much travel time we save versus Dijkstra, at each delta. Right side: how often we replan.

N equals 225 on each delta. That is seventy-five origin–destination pairs, times the three traffic regimes. We are pooling peak, off-peak, and incident here. The next slides split the regimes.

Look at the reduction line. It does not move. Five percent, ten, fifteen, twenty — about five and three-quarter percent overall versus Dijkstra in every case. The ANOVA F is about 0.001, p equals 1.00. That does not mean the study failed. It means the four policies produce the same travel time.

Why? In the incident regime, corridor speed falls by forty percent. Remaining time jumps by more than twenty percent. So even the strictest policy, delta 0.20, still fires. About one replan per incident journey at every setting.

When travel time is the same, decision support prefers the quieter alert. That is delta 0.20. Replans overall fall slightly from 0.45 to 0.39.

Chapter 3 put 0.10 in the middle of a five-to-twenty percent band as the value to test. After measurement, 0.20 is the default. Delta is not alpha. Alpha stays point-zero-five for the t-tests.

---

## Slide 8 · 6:20–7:40 · Figure — seconds (point at the three clusters)

Objective 4. These bars are mean journey time in seconds — clock time from origin to destination after we drive every method on the real future speeds.

Start with incident, the tall cluster. Dijkstra, the current-map path, averages 728 seconds. The framework averages 599 seconds. That is about two minutes and ten seconds saved on that test graph when the planned road is disrupted. Reactive A-star, which replans once the jam is already on the snapshot, is 604 seconds — close to us. The oracle, with perfect future knowledge, is 581. We sit a little behind the oracle, as we must.

Why is reactive close in incidents? Once the slowdown is visible in current speeds, a thirty-minute forecast adds little. The value of the GRU is anticipatory: it can divert before the vehicle is fully committed. That is the keen reading of this figure. We are not claiming to dominate a reactive router after the jam is obvious.

Peak. Both methods are around 510 seconds. Widespread congestion leaves few quiet alternatives, so looking ahead helps only modestly: 506 versus 513.

Off-peak. Every serious method sits near 403 seconds. Empty roads are the negative control. A forecast and a current map should agree. They do. That is success, not a dead model.

---

## Slide 9 · 7:40–9:10 · Figure — percent (headline — go slowly)

This figure is the same experiment as the seconds, now as a percentage against Dijkstra.

N equals 300 in each regime. That is seventy-five pairs, times four delta values. We can pool delta because Objective 3 showed travel time does not depend on which of the four policies we pick. N is not seventy-five here, and it is not nine hundred. Nine hundred is the whole study. Three hundred is one regime.

Percentage reduction: how much shorter the framework journey is than Dijkstra’s, on the same origin, destination, and clock. Positive means we were faster.

Incident: plus 16.19 percent. t is 26.43, p less than .001. About one replan per journey. That is the result that matches the purpose: when the planned corridor breaks, looking thirty minutes ahead and triggering on remaining time cuts realised delay.

Peak: plus 1.03 percent. Statistically detectable, p equals .0002. Operationally small. The network is busy in every direction.

Off-peak: plus 0.01 percent, p equals .90. Not significant. The negative control held.

Overall plus 5.74 percent is a mixture of those three worlds. If you quote one number from this talk, quote 16 percent under incidents, not 5.74 percent as if it applied to every ambulance.

Versus historical A-star we are 7.39 percent faster — an average day is not enough. Versus reactive A-star, 0.61 percent. I report that small gap on purpose. Versus the oracle we are 1.69 percent slower. The ceiling is intact.

---

## Slide 10 · 9:10–10:00 · Figure — latency

Latency. The operational cap was one thousand milliseconds — one second — so a recommendation can be issued inside a dispatch click.

Time-dependent A-star averages 0.37 milliseconds. The GRU averages 39.3 milliseconds. Combined, about 40 milliseconds. That combined figure is the system wait. Do not quote 0.37 as if the dispatcher only waits for search.

The predictor is the slower part, and the loop still fits comfortably inside one second.

I did not pre-build a continental contraction hierarchy. At two hundred and seven nodes it was unnecessary. That is useful: edge weights can be rewritten every five minutes when a new forecast arrives.

---

## Slide 11 · 10:00–11:20 · Limits and what you already did

These percentages describe Los Angeles freeway detectors with a sensor on every edge. Transfer to a mixed-traffic city needs local sensors. That is a real limit, not a hidden error. Here is what I already did about it.

I did not route on a sparse street map and fill missing roads with guessed free-flow. I used the detector graph so every edge had a measured speed. The honest next step is to downsample that same graph to ten or thirty percent coverage and repeat the nine hundred journeys — not to pretend this 16 percent is already a sparse-city number.

I stopped the future leaking into the past: time-ordered split, scaler fitted on training only.

I stopped a method looking good because it was scored on its own forecast: everyone is walked on actual future speeds.

I stopped a weak baseline making 16 percent look larger than it is: reactive A-star and an oracle are in the table. The small gap to reactive, and the small gap behind the oracle, are part of the result.

PEMS-BAY shows the architecture still predicts in a second city. It does not yet show routing there. That is further work, with a Bay routing graph.

Single vehicle. Fleet interference is out of scope.

If there is a next study, it starts from this 100 percent detector graph and thins the sensors.

---

## Slide 12 · 11:20–12:00 · Close

Three sentences.

One. Under incident conditions the framework cut current-map Dijkstra time by 16.19 percent — about 599 seconds versus 728 — with about one replan.

Two. Delta from 5 to 20 percent did not change travel time. I recommend 0.20.

Three. Combined wait is about 40 milliseconds. Compute is not the barrier. Sensors are.

Thank you. I welcome your questions.

---

## If asked (do not put these on slides)

| They ask | You say |
|---|---|
| What is N? | 900 = whole study. 225 = one δ across 3 regimes. 300 = one regime across 4 δ. |
| Why not Nairobi numbers? | Public fully instrumented archive so the 900-run can be repeated. Method transfers; these % do not until local detectors exist. |
| Why so close to reactive A*? | Once the jam is on the snapshot, a 30-minute forecast adds little. The gain is before that. |
| Why p = 1.00 on δ? | The four policies give the same travel time. Not “the experiment found nothing.” |
| Why off-peak is ~0? | Negative control. Empty roads should not need a forecast. |
| Did you beat the oracle? | No. 1.69% slower. Required if B4 is honest. |
| Why not a GNN? | MAE can be better; wait at every refresh would not fit this one-second loop. |
| 37 papers? | Do not quote 37. Five themes. See the reference list. |
| Old draft 78% / 3.42 MAE / 17 epochs / 397 nodes? | Those are withdrawn. Defended file: `results/full_report.txt`. |
