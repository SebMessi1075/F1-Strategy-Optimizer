# optimizer/simulate_strategy.py - FIXED VERSION

import numpy as np
import joblib

# Load models
try:
    lap_time_model = joblib.load("models/lap_time_model.pkl")
    feature_scaler = joblib.load("models/feature_scaler.pkl")
except FileNotFoundError as e:
    raise FileNotFoundError(f"Model files not found: {e}. Run train_model.py first.")


def engineer_features(lap, tyre_age, compound, temp, laps, track_id, track):
    """
    Engineer 16 features for the ML model.
    Must match the features used in strategy_dp.py
    """
    
    # 1. Basic lap/tyre features
    lap_norm = lap / max(laps, 1)  # Normalized lap number
    tyre_age_norm = tyre_age / max(laps, 1)  # Normalized tyre age
    
    # 2. Tyre compound (one-hot encoded)
    is_soft = 1 if compound == 0 else 0
    is_medium = 1 if compound == 1 else 0
    is_hard = 1 if compound == 2 else 0
    
    # 3. Track temperature and normalized
    temp_norm = (temp - 20) / (55 - 20)  # Normalize to 0-1 range
    
    # 4. Stint information
    stint_progress = tyre_age / (laps / 3)  # Assume ~3 stints per race
    stint_progress = min(stint_progress, 1.0)  # Cap at 1.0
    
    # 5. Track characteristics (if available from TRACK_CONFIG)
    try:
        from optimizer.track_config import TRACK_CONFIG
        track_info = TRACK_CONFIG.get(track, {})
        if isinstance(track_info, dict):
            track_length = track_info.get('length', 5.0) / 10  # Normalize
            track_corners = track_info.get('corners', 15) / 30  # Normalize
        else:
            track_length = 0.5
            track_corners = 0.5
    except:
        track_length = 0.5
        track_corners = 0.5
    
    # 6. Tyre degradation curve (quadratic degradation)
    degradation_factor = (tyre_age / max(laps, 1)) ** 2
    
    # 7. Tyre life remaining
    tyre_life_remaining = 1 - (tyre_age / (laps / 2))  # Assume stint length ~laps/2
    tyre_life_remaining = max(0, min(tyre_life_remaining, 1.0))
    
    # 8. Track ID encoded (if needed)
    track_id_norm = track_id / 100  # Normalize if IDs are 0-100
    
    # Features array: 16 features total
    features = np.array([
        lap,                      # 0: Lap number
        tyre_age,                 # 1: Tyre age (laps)
        compound,                 # 2: Compound (0=soft, 1=med, 2=hard)
        temp,                     # 3: Track temp (°C)
        lap_norm,                 # 4: Normalized lap
        tyre_age_norm,            # 5: Normalized tyre age
        is_soft,                  # 6: Is soft compound
        is_medium,                # 7: Is medium compound
        is_hard,                  # 8: Is hard compound
        temp_norm,                # 9: Normalized temperature
        stint_progress,           # 10: Stint progress (0-1)
        track_length,             # 11: Track length (normalized)
        track_corners,            # 12: Track corners (normalized)
        degradation_factor,       # 13: Tyre degradation (squared)
        tyre_life_remaining,      # 14: Tyre life remaining
        track_id_norm,            # 15: Track ID (normalized)
    ])
    
    return features.reshape(1, -1)


def predict_lap_time(lap, tyre_age, compound, temp, laps, track_id, track):
    """
    Predict lap time with proper feature engineering and scaling.
    """
    try:
        # Engineer features to 16-feature vector
        X = engineer_features(lap, tyre_age, compound, temp, laps, track_id, track)
        
        # Apply scaling
        X_scaled = feature_scaler.transform(X)
        
        # Predict lap time
        lap_time = lap_time_model.predict(X_scaled)[0]
        
        # Sanity check: lap times should be 60-130 seconds
        if lap_time < 50 or lap_time > 200:
            print(f"Warning: Unusual lap time prediction: {lap_time}s at lap {lap}")
        
        return float(lap_time)
    
    except Exception as e:
        raise RuntimeError(f"Prediction failed for lap {lap}: {str(e)}")


def simulate_strategy(laps, temp, start_compound, pit_laps, compounds, track, track_id, events):
    """
    Simulate a given pit strategy to get lap-by-lap cumulative times.
    
    Args:
        laps: Total race laps
        temp: Track temperature (°C)
        start_compound: Starting compound (0=Soft, 1=Medium, 2=Hard)
        pit_laps: List of laps where we pit
        compounds: List of compounds after each pit (starting with initial compound)
        track: Track name string
        track_id: Encoded track ID
        events: Dict of {lap: event_type} (VSC, SC)
    
    Returns:
        numpy array of cumulative lap times
    """
    
    cumulative_time = []
    total_time = 0
    current_compound = start_compound
    tyre_age = 0
    pit_idx = 0
    
    for lap in range(1, laps + 1):
        # Check if pitting this lap
        if pit_idx < len(pit_laps) and lap == pit_laps[pit_idx]:
            pit_penalty = 22.0  # Seconds for pit stop
            total_time += pit_penalty
            current_compound = compounds[pit_idx + 1]
            tyre_age = 0
            pit_idx += 1
        
        # Predict lap time with 16 features
        lap_time = predict_lap_time(
            lap, 
            tyre_age, 
            current_compound, 
            temp, 
            laps, 
            track_id, 
            track
        )
        
        # Apply race events
        if lap in events:
            if events[lap] == "SC":
                lap_time += 2.0  # Safety Car = slower pace
            elif events[lap] == "VSC":
                lap_time += 0.5  # Virtual Safety Car = minimal impact
        
        total_time += lap_time
        cumulative_time.append(total_time)
        tyre_age += 1
    
    return np.array(cumulative_time)