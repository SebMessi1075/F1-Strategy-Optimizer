# train_model_realistic.py - REALISTIC F1 DATA

import numpy as np
import joblib
import os
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

os.makedirs("models", exist_ok=True)

print("=" * 60)
print("F1 REALISTIC STRATEGY OPTIMIZER - MODEL TRAINING")
print("=" * 60)

# ============================================================================
# STEP 1: TRACK ENCODER
# ============================================================================
print("\n[1] Creating Track Encoder...")

tracks = [
    'Bahrain', 'Saudi Arabia', 'Australia', 'Japan', 'China',
    'Miami', 'Monaco', 'Canada', 'Spain', 'Austria',
    'Silverstone', 'Hungary', 'Belgium', 'Netherlands', 'Monza',
    'Singapore', 'Japan', 'USA', 'Mexico', 'Brazil',
    'Abu Dhabi'
]

track_encoder = LabelEncoder()
track_encoder.fit(tracks)
joblib.dump(track_encoder, "models/track_encoder.pkl")
print(f"✓ Track encoder saved with {len(tracks)} circuits")

# ============================================================================
# STEP 2: REALISTIC SYNTHETIC TRAINING DATA
# ============================================================================
print("\n[2] Generating REALISTIC F1 Training Data...")

np.random.seed(42)
n_samples = 8000

data = []

for _ in range(n_samples):
    lap = np.random.randint(1, 60)
    tyre_age = np.random.randint(0, 45)
    compound = np.random.randint(0, 3)  # 0=Soft, 1=Medium, 2=Hard
    temp = np.random.uniform(20, 55)
    total_laps = 58
    track_id = np.random.randint(0, 21)
    
    # Feature engineering
    lap_norm = lap / max(total_laps, 1)
    tyre_age_norm = tyre_age / max(total_laps, 1)
    is_soft = 1 if compound == 0 else 0
    is_medium = 1 if compound == 1 else 0
    is_hard = 1 if compound == 2 else 0
    temp_norm = (temp - 20) / (55 - 20)
    stint_progress = tyre_age / (total_laps / 2.5)  # Realistic stint length
    stint_progress = min(stint_progress, 1.0)
    track_length = np.random.uniform(3.5, 7.0) / 10
    track_corners = np.random.uniform(10, 27) / 30
    degradation_factor = (tyre_age / max(total_laps, 1)) ** 2
    tyre_life_remaining = max(0, min(1 - (tyre_age / (total_laps / 2.5)), 1.0))
    track_id_norm = track_id / 100
    
    features = np.array([
        lap, tyre_age, compound, temp, lap_norm, tyre_age_norm,
        is_soft, is_medium, is_hard, temp_norm, stint_progress,
        track_length, track_corners, degradation_factor,
        tyre_life_remaining, track_id_norm,
    ])
    
    # =====================================================================
    # REALISTIC LAP TIME SIMULATION
    # =====================================================================
    
    # Base lap time (85-95 seconds typical)
    base_time = 88 + np.random.normal(0, 2)
    
    # SOFT TYRES: Fast initial, rapid degradation
    if compound == 0:  # SOFT
        if tyre_age == 0:
            base_time -= 3.0  # Fresh softs = -3s
        elif tyre_age <= 5:
            base_time -= 2.5 - (tyre_age * 0.3)  # Linear loss
        elif tyre_age <= 15:
            base_time -= 0.5 - (tyre_age * 0.15)  # Continued loss
        else:
            base_time += 2.0 + ((tyre_age - 15) * 0.5)  # Falls off cliff after 15 laps
    
    # MEDIUM TYRES: Balanced, moderate degradation
    elif compound == 1:  # MEDIUM
        if tyre_age == 0:
            base_time -= 1.0
        elif tyre_age <= 20:
            base_time -= 0.8 - (tyre_age * 0.05)
        else:
            base_time -= 0.2 - ((tyre_age - 20) * 0.1)
    
    # HARD TYRES: Slow start, very durable
    else:  # HARD
        if tyre_age == 0:
            base_time += 1.5  # Cold hards = slower
        elif tyre_age <= 30:
            base_time += 0.8 - (tyre_age * 0.03)  # Very gradual loss
        else:
            base_time += 0.2 - ((tyre_age - 30) * 0.02)  # Minimal loss
    
    # Temperature effect (optimal 30-40°C)
    if temp < 25:
        base_time += (25 - temp) * 0.3
    elif temp > 45:
        base_time += (temp - 45) * 0.2
    else:
        optimal_temp = 35
        temp_delta = abs(temp - optimal_temp) / 10
        base_time += temp_delta * 1.5
    
    # Lap 1 cold start penalty
    if lap == 1:
        base_time += 2.5
    
    # Track characteristics
    if track_id in [6, 14]:  # Monaco, Monza - fast circuits
        base_time -= 4
    elif track_id in [8, 15]:  # Singapore - slow tight circuit
        base_time += 5
    
    # Clamp to realistic range
    lap_time = max(70, min(120, base_time))
    
    data.append(list(features) + [lap_time])

print(f"✓ Generated {n_samples} realistic F1 samples")

# ============================================================================
# STEP 3: TRAIN MODEL
# ============================================================================
print("\n[3] Training Gradient Boosting Model...")

X = np.array([row[:-1] for row in data])
y = np.array([row[-1] for row in data])

print(f"   Feature shape: {X.shape}")
print(f"   Lap time range: {y.min():.1f}s - {y.max():.1f}s")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = GradientBoostingRegressor(
    n_estimators=120,
    learning_rate=0.08,
    max_depth=6,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    verbose=0
)

model.fit(X_train_scaled, y_train)

train_score = model.score(X_train_scaled, y_train)
test_score = model.score(X_test_scaled, y_test)

print(f"   Train R² Score: {train_score:.4f}")
print(f"   Test R² Score: {test_score:.4f}")

joblib.dump(model, "models/lap_time_model.pkl")
joblib.dump(scaler, "models/feature_scaler.pkl")

print("✓ Model and scaler saved")

# ============================================================================
# STEP 4: STRATEGY CONSTRAINTS (for DP optimizer)
# ============================================================================
print("\n[4] Saving Tyre Strategy Constraints...")

# Realistic tyre stint lengths and compound switching
strategy_config = {
    # Max laps per compound (realistic)
    'soft_max_laps': 18,      # Softs last ~15-18 laps max
    'medium_max_laps': 25,    # Mediums last ~20-25 laps
    'hard_max_laps': 40,      # Hards can go 35-40+ laps
    
    # Pit stop penalty (seconds)
    'pit_penalty': 22,
    
    # Optimal pit windows (laps into stint)
    'soft_pit_window': (12, 18),     # Pit soft between lap 12-18
    'medium_pit_window': (15, 25),   # Pit medium between lap 15-25
    'hard_pit_window': (25, 40),     # Pit hard between lap 25-40
    
    # Can't pit for same compound (must switch)
    'must_switch_compound': True,
    
    # Race strategy patterns (1-stop, 2-stop, 3-stop)
    'typical_strategies': [
        # 1-stop: rare in modern F1, only ~40 lap races
        {'stops': 1, 'compounds': [1, 2]},  # Med-Hard
        
        # 2-stop: most common
        {'stops': 2, 'compounds': [1, 0, 2]},  # Med-Soft-Hard
        {'stops': 2, 'compounds': [0, 1, 2]},  # Soft-Med-Hard
        {'stops': 2, 'compounds': [0, 2, 1]},  # Soft-Hard-Med
        
        # 3-stop: used in some races
        {'stops': 3, 'compounds': [1, 0, 1, 2]},  # Med-Soft-Med-Hard
        {'stops': 3, 'compounds': [0, 1, 0, 2]},  # Soft-Med-Soft-Hard
    ]
}

joblib.dump(strategy_config, "models/strategy_config.pkl")
print("✓ Strategy constraints saved")

# ============================================================================
# STEP 5: SUMMARY
# ============================================================================
print("\n" + "=" * 60)
print("✅ REALISTIC SETUP COMPLETE!")
print("=" * 60)
print("\nKey improvements:")
print("  ✓ Soft tyres degrade rapidly after 15 laps (realistic)")
print("  ✓ Medium tyres last 20-25 laps with moderate degradation")
print("  ✓ Hard tyres extremely durable (35-40+ laps)")
print("  ✓ Temperature effects on all compounds")
print("  ✓ Realistic pit window constraints")
print("  ✓ Strategy patterns based on modern F1")
print("\nFiles created:")
print("  ✓ models/lap_time_model.pkl")
print("  ✓ models/feature_scaler.pkl")
print("  ✓ models/track_encoder.pkl")
print("  ✓ models/strategy_config.pkl")
print("\nRun: streamlit run app.py")
print("=" * 60)