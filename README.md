<div align="center">

# PITWALL

**Formula 1 race strategy, decided by a model trained on 215,000 real laps.**

Every legal pit strategy, simulated and ranked by expected finishing time under safety car uncertainty.

[**Live demo**](https://f1-strategy-optimizer.vercel.app) · [API](https://pitwall-h25o.onrender.com/health) · [Model card](#model-card)

![Python](https://img.shields.io/badge/Python-3.10+-1f2937?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.8-1f2937?logo=scikitlearn&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=nextdotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![Tests](https://img.shields.io/badge/tests-11%20passing-3B7A57)

</div>

---

## The problem

A Formula 1 car loses roughly a tenth of a second per lap as its tyres wear. Fitting
fresh ones costs about 22 seconds in the pit lane. Three compounds trade outright
pace against durability, the regulations require at least two of them in a dry race,
and a safety car can appear at any lap and make a pit stop half price.

So the question is a constrained scheduling problem under uncertainty: **when do you
stop, what do you fit, and how do you plan for an event you cannot predict?**

PITWALL answers it end to end, from raw historical lap times to a deployed interface.

---

## How it works

Lap time is composed from two deliberately separated layers, so nothing is a black box
and neither layer double counts the other:

```
lap_time  =  base_pace(circuit, fuel_load, temperature)     ← learned from real laps
          +  tyre_delta(compound, tyre_age, temperature)    ← physical, calibratable
          ×  track_status(green | VSC | safety car)         ← race conditions
```

**Base pace** is a gradient boosted model trained on ~215,000 clean green flag laps
(2014 to 2024, 32 circuits). It learns circuit pace, temperature, and the fuel burn
trend, recovering a ~1.9 s/lap gain from full tank to empty purely from the data.

**Tyre degradation** is a transparent physical model: each compound has a fresh pace
offset, a linear wear rate, and a cliff once it ages past a threshold, all scaled by
track temperature. The historical dataset contains no tyre compound labels, so rather
than fabricate them this layer stays an explicit, tunable assumption. The included
FastF1 pipeline replaces it with wear rates learned from real compound data.

**Strategy search** enumerates every legal one, two, and three stop plan across all
compound sequences and a grid of pit laps, simulates each through the shared lap time
model, enforces the two compound rule, then ranks the leaders by Monte Carlo expected
time across 200 randomised safety car scenarios.

**Reactive policy.** A passive simulation measures the cost of a safety car but never
the value of responding to one. Each simulated race therefore uses a one step
lookahead: when a safety car appears, it simulates finishing the race both ways and
takes the cheaper. This is provably never worse than ignoring the opportunity, and it
correctly declines when the timing does not help.

<div align="center">

| Safety car lap | Reaction | Time gained |
|:--|:--|--:|
| 2  | none, tyres too fresh | 0.0 s |
| 10 | pit early | 5.4 s |
| 26 | pit early | **8.9 s** |
| 42 | none, stops already done | 0.0 s |

<sub>Silverstone, 52 laps. The value of reacting peaks near a due stop and vanishes at either end of the race.</sub>

</div>

---

## Model card

Honest numbers, including where the model is weak.

| Metric | Value | How it was measured |
|:--|:--|:--|
| R² | **0.845** | 5 fold CV, grouped by race weekend |
| Mean absolute error | **2.63 s** | same grouped CV |
| Median error, unseen seasons | **2.0 s** | trained ≤2022, tested on 2023 and 2024 |
| Training data | 214,993 laps | 32 circuits, 2014 to 2024 |
| Learned fuel effect | 1.85 s/lap | full tank to empty, recovered from data |

**On the evaluation.** Laps from the same race are near duplicates, so a random train
test split leaks and flatters the score. Splitting by whole race weekends keeps every
circuit represented in training while testing only on races the model has never seen,
which is exactly how the optimiser is used in practice.

**On the failure modes.** Held out season accuracy is strong where history is dense
(Monza 0.77 s, Silverstone 1.06 s, Bahrain 1.16 s) and degrades where it is not.
Suzuka is the worst case at ~10 s, because it was not raced in 2020 or 2021 and the
model has too little history to extrapolate from. Wet races miss badly too, since
rain is not modelled. The median is the representative figure; the mean is dragged by
these known cases.

---

## Architecture

```
Build once                         Every request
─────────────────────────          ──────────────────────────────
raw laps                           Next.js frontend  (Vercel)
   ↓  data pipeline                     ↓  POST /optimise
clean dataset                      FastAPI service   (Render)
   ↓  training                          ↓
pace model + tyre model  ──────→   strategy engine
(pkl + json artifacts)                 ↓  simulate · search · rank
                                   ranked strategies + analysis
```

```
f1opt/
├── paths.py                 repo relative paths
├── data/
│   ├── build_dataset.py     raw laps → clean training set, offline
│   └── fastf1_pipeline.py   real compound, tyre life, temperature, needs network
├── model/
│   ├── features.py          single source of truth for features
│   ├── pace_model.py        learned base pace + grouped CV
│   ├── tyre_model.py        physical degradation, calibratable
│   └── lap_time.py          composes base + tyre + conditions
└── strategy/
    ├── conditions.py        safety car physics
    ├── simulator.py         deterministic, Monte Carlo, reactive
    └── optimizer.py         legal search, ranking, undercut analysis

api.py                       FastAPI service
web/                         Next.js + TypeScript frontend
tests/                       11 unit tests
```

---

## Running locally

**Requires** Python 3.10+ and Node.js 18+.

```bash
# Backend
pip install -r requirements.txt
python -m f1opt.data.build_dataset     # raw laps → dataset
python -m f1opt.model.pace_model       # train + evaluate
python -m f1opt.model.tyre_model       # build tyre layer
uvicorn api:app --reload --port 8000

# Frontend, in a second terminal
cd web && npm install && npm run dev   # → http://localhost:3000
```

Trained artifacts are committed, so you can skip straight to `uvicorn` and `npm run dev`.

**Optional, real tyre data.** The bundled dataset has no compound labels. To learn
real per compound wear rates from timing data (2018+, requires network):

```bash
python -m f1opt.data.fastf1_pipeline 2018 2024
python -m f1opt.model.pace_model
python -m f1opt.model.tyre_model       # now learns, instead of assuming
```

```bash
pytest -q                              # 11 tests
```

---

## API

| Endpoint | Returns |
|:--|:--|
| `GET /health` | service status and circuit count |
| `GET /circuits` | all 32 circuits with typical lap counts |
| `GET /model-card` | live evaluation metrics |
| `POST /optimise` | ranked strategies, pace curves, undercut analysis |

```bash
curl -X POST http://localhost:8000/optimise \
  -H "Content-Type: application/json" \
  -d '{"circuit":"silverstone","laps":52,"temp":35,"max_stops":2,"sc_lap":0,"vsc_lap":0}'
```

---

## Design decisions

**Why gradient boosted trees, not deep learning.** The data is tabular and moderate in
size, which is exactly where tree ensembles win. It trains in seconds and the fuel and
temperature effects stay interpretable.

**Why exhaustive search, not a heuristic.** The legal strategy space is small enough to
evaluate completely, so the result is the true optimum under the model rather than a
plausible guess, and every recommendation can be explained.

**Why a physical tyre model.** The dataset has no compound labels. Learning degradation
from it would mean inventing the signal. Keeping that layer explicit draws a clear line
between what is measured and what is assumed, and gives the FastF1 pipeline something
concrete to calibrate.

**Why expected time, not fastest time.** A plan that is quickest on paper can be fragile
to a badly timed safety car. Ranking on expected outcome across simulated scenarios
prefers strategies that hold up.

---

## Not modelled

Single car pace only, so the undercut figures are pure pace deltas and do not include
track position gained on rivals. No mid race weather changes, no driver specific pace
(available from FastF1 and a natural next step), and no traffic or dirty air.

---

<div align="center">
<sub>Built with real data, evaluated honestly.</sub>
</div>
