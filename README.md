<div align="center">

# 🏎️ F1 Race Strategy Optimizer

**AI-powered pit stop strategy engine for Formula 1 racing**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

*Combines Gradient Boosting lap-time prediction with Dynamic Programming strategy optimization across 21 real F1 circuits.*

</div>

---

## Overview

The F1 Race Strategy Optimizer is a full-stack race intelligence tool that answers the question every F1 strategist faces: **when to pit, and on which tire compound?**

Given a circuit, race distance, track temperature, starting compound, and any safety car events, the app computes the mathematically optimal pit stop schedule — then simulates it lap by lap and compares it against a conventional baseline strategy, showing exactly how many seconds are gained.

The engine has two core components working in tandem:

- **ML Lap-Time Predictor** — a Gradient Boosting model trained on 8,000 synthetic samples with realistic F1 degradation physics, predicting lap time given tire age, compound, temperature, and track characteristics.
- **Dynamic Programming Optimizer** — a memoized DP solver over the state space `(lap, compound, tire_age)` that finds the globally optimal pit sequence, not just a locally greedy one.

---

## Features

- **21 real F1 circuits** — Bahrain, Monaco, Silverstone, Monza, Singapore, Suzuka, and more, each with accurate track length, corner count, and DRS zone data.
- **Three tire compounds** — Soft (peak speed, short life), Medium (balanced), Hard (durable, slower) with realistic degradation curves and stint-length constraints.
- **Safety Car / VSC handling** — inject SC or VSC events at any lap; the optimizer adjusts lap times and strategy accordingly.
- **Lap-by-lap telemetry chart** — cumulative race time curves for optimized vs. baseline strategy, with event markers.
- **Rich metrics dashboard** — total race time, pit count, compounds used, average stint length, and time advantage over baseline.
- **Dark F1 aesthetic UI** — custom CSS with the official F1 red (#E10600) and gold accent (#FFD700) on a near-black background.

---

## How It Works

```
User inputs (circuit, laps, temp, compound, SC events)
         │
         ▼
  TrackConfig lookup ──► circuit metadata (length, corners, DRS zones)
         │
         ▼
  RaceConditions ──► SC/VSC lap-time penalties applied
         │
         ▼
  GradientBoostingRegressor ──► predicts lap time for every (lap, compound, tire_age) state
         │                       (16 engineered features, StandardScaler normalized)
         ▼
  Dynamic Programming Solver ──► memoized over state (lap, compound, tire_age)
         │                        pit penalty: 22s | pit deadline: last 15% of race
         │                        compound switch enforced on every pit
         ▼
  Strategy Simulation ──► replays optimal sequence lap by lap
         │
         ▼
  Streamlit UI ──► metrics, pit cards, telemetry chart, baseline comparison
```

### Tire Degradation Model

| Compound | Peak Delta | Max Stint | Cliff After |
|----------|-----------|-----------|-------------|
| Soft     | −3.0 s    | 18 laps   | ~15 laps    |
| Medium   | 0.0 s     | 25 laps   | ~20 laps    |
| Hard     | +1.5 s    | 40 laps   | ~35 laps    |

Temperature effects are modelled with a quadratic penalty outside the optimal 30–40 °C window.

### Dynamic Programming Constraints

- Pit stops incur a **22-second** time loss (stationary + pit lane delta).
- No pitting in the **final 15%** of race distance.
- A compound **must change** on every pit (cannot re-fit the same type).
- If tire age exceeds the compound's max stint, a pit is forced.
- Pit window opens at **lap 5** minimum.

---

## Installation

```bash
git clone https://github.com/shaauryaa/F1-Strategy-Optimizer.git
cd F1-Strategy-Optimizer

pip install -r requirements.txt
```

> **Microsoft Store Python users:** if `streamlit` isn't recognized as a command, run it via `python -m streamlit run app.py` or add your Python Scripts folder to PATH.

### Train the model (optional)

A pre-trained model is included in `models/`. To retrain from scratch:

```bash
python models.py
```

This generates 8,000 synthetic training samples, fits a `GradientBoostingRegressor`, and saves the model + scaler to `models/`.

---

## Usage

```bash
streamlit run app.py
# or
python -m streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

### Sidebar controls

| Control | Range | Description |
|---------|-------|-------------|
| Circuit | 21 options | Selects track metadata |
| Race Distance | 40–75 laps | Total race laps |
| Track Temperature | 20–55 °C | Affects lap-time predictions |
| Starting Compound | Soft / Medium / Hard | Tire you start on |
| VSC Lap | Optional | Lap a Virtual Safety Car is deployed |
| SC Lap | Optional | Lap a full Safety Car is deployed |

Click **Analyze Strategy** to run the optimizer.

---

## Project Structure

```
F1-Strategy-Optimizer/
│
├── app.py                   # Streamlit UI (hero section, sidebar, charts, metrics)
├── models.py                # Training script — generates data, trains & saves model
├── prepare_kaggle_data.py   # Optional: processes raw Kaggle F1 historical data
│
├── optimizer/
│   ├── strategy_dp.py       # Memoized DP solver over (lap, compound, tire_age)
│   ├── simulate_strategy.py # Replays a pit sequence and returns per-lap times
│   ├── race_conditions.py   # SC / VSC time adjustment functions
│   └── track_config.py      # 21-circuit metadata dictionary
│
├── models/
│   ├── lap_time_model.pkl   # Trained GradientBoostingRegressor
│   ├── scaler.pkl           # Fitted StandardScaler
│   └── model_metadata_*.json
│
└── requirements.txt
```

---

## Tech Stack

| Layer | Library |
|-------|---------|
| UI | Streamlit 1.58 |
| ML model | scikit-learn `GradientBoostingRegressor` |
| Optimization | Custom memoized DP (pure Python) |
| Data | NumPy, Pandas |
| Visualization | Matplotlib |
| Serialization | Joblib |

---

## Results

The optimizer consistently finds strategies that outperform a naive 1-stop baseline by **15–45 seconds** depending on circuit, temperature, and safety car events. On high-degradation tracks (Singapore, Monaco) with a Soft starting compound, multi-stop strategies can save over a minute of race time.

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
  Built for the love of motorsport and machine learning.
</div>
