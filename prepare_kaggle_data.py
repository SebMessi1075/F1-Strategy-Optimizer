import pandas as pd
import numpy as np

# Load raw Kaggle data
lap_times = pd.read_csv("data/raw/lap_times.csv")
races = pd.read_csv("data/raw/races.csv")
circuits = pd.read_csv("data/raw/circuits.csv")

# Merge races with circuits
races = races.merge(circuits, on="circuitId", how="left")

# Keep recent seasons
races = races[(races["year"] >= 2018) & (races["year"] <= 2024)]

# Map race names to track names used in app
TRACK_MAP = {
    "Monaco Grand Prix": "Monaco",
    "Italian Grand Prix": "Monza",
    "British Grand Prix": "Silverstone",
    "Spanish Grand Prix": "Barcelona"
}

# IMPORTANT: after merge, race name is name_x
races = races[races["name_x"].isin(TRACK_MAP.keys())]

# Merge lap times with race info
lap_times = lap_times.merge(
    races[["raceId", "year", "name_x"]],
    on="raceId",
    how="inner"
)

rows = []

for race_id, group in lap_times.groupby("raceId"):
    race_name = group["name_x"].iloc[0]
    track = TRACK_MAP[race_name]

    total_laps = group["lap"].max()

    for _, row in group.iterrows():
        if pd.isna(row["milliseconds"]):
            continue

        # Synthetic but realistic tyre modeling
        compound = np.random.choice([0, 1, 2], p=[0.3, 0.4, 0.3])
        tyre_age = np.random.randint(1, 20)
        track_temp = np.random.randint(30, 45)

        rows.append({
            "lap": int(row["lap"]),
            "tyre_age": tyre_age,
            "compound_encoded": compound,
            "track_temperature": track_temp,
            "laps_total": int(total_laps),
            "track": track,
            "lap_time": row["milliseconds"] / 1000.0
        })

df = pd.DataFrame(rows)

df = df[df["lap_time"] < 200]
df.to_csv("data/f1_strategy_dataset.csv", index=False)

print("===================================")
print("✅ Kaggle F1 dataset prepared")
print("Rows:", len(df))
print("Tracks:", df["track"].unique())
print("Saved to data/f1_strategy_dataset.csv")
print("===================================")
