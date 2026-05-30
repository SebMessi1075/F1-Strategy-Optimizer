# optimizer/strategy_dp.py - REALISTIC VERSION

import numpy as np
import joblib

# Load models and constraints
lap_time_model = joblib.load("models/lap_time_model.pkl")
feature_scaler = joblib.load("models/feature_scaler.pkl")
strategy_config = joblib.load("models/strategy_config.pkl")


def engineer_features(lap, tyre_age, compound, temp, laps, track_id, track):
    """Engine 16 features for prediction."""
    
    lap_norm = lap / max(laps, 1)
    tyre_age_norm = tyre_age / max(laps, 1)
    is_soft = 1 if compound == 0 else 0
    is_medium = 1 if compound == 1 else 0
    is_hard = 1 if compound == 2 else 0
    temp_norm = (temp - 20) / (55 - 20)
    stint_progress = tyre_age / (laps / 2.5)
    stint_progress = min(stint_progress, 1.0)
    
    try:
        from optimizer.track_config import TRACK_CONFIG
        track_info = TRACK_CONFIG.get(track, {})
        if isinstance(track_info, dict):
            track_length = track_info.get('length', 5.0) / 10
            track_corners = track_info.get('corners', 15) / 30
        else:
            track_length = 0.5
            track_corners = 0.5
    except:
        track_length = 0.5
        track_corners = 0.5
    
    degradation_factor = (tyre_age / max(laps, 1)) ** 2
    tyre_life_remaining = max(0, min(1 - (tyre_age / (laps / 2.5)), 1.0))
    track_id_norm = track_id / 100
    
    features = np.array([
        lap, tyre_age, compound, temp, lap_norm, tyre_age_norm,
        is_soft, is_medium, is_hard, temp_norm, stint_progress,
        track_length, track_corners, degradation_factor,
        tyre_life_remaining, track_id_norm,
    ])
    
    return features.reshape(1, -1)


def predict(lap, tyre_age, compound, temp, laps, track_id, track):
    """Predict lap time."""
    try:
        X = engineer_features(lap, tyre_age, compound, temp, laps, track_id, track)
        X_scaled = feature_scaler.transform(X)
        lap_time = lap_time_model.predict(X_scaled)[0]
        return float(lap_time)
    except Exception as e:
        raise RuntimeError(f"Prediction failed for lap {lap}: {str(e)}")


def get_max_stint_length(compound):
    """Get realistic max stint length for compound."""
    max_stints = {
        0: strategy_config['soft_max_laps'],      # Soft
        1: strategy_config['medium_max_laps'],    # Medium
        2: strategy_config['hard_max_laps'],      # Hard
    }
    return max_stints.get(compound, 25)


def is_bad_strategy(tyre_age, compound):
    """Check if tyre is too old (unrealistic to continue)."""
    max_length = get_max_stint_length(compound)
    # Flag as bad if we've exceeded realistic stint length
    return tyre_age > max_length


def optimize_strategy(laps, temp, start_compound, track, track_id, events):
    """
    Dynamic Programming strategy optimization with REALISTIC constraints.
    """
    
    pit_penalty = strategy_config['pit_penalty']
    INF = float('inf')
    memo = {}
    parent = {}
    
    # Don't allow pits in final 15% of race (too late to be useful)
    pit_deadline = int(laps * 0.85)
    
    def dp(lap, compound, tyre_age):
        """Recursive DP with memoization."""
        
        # Base case: race finished
        if lap > laps:
            return 0, []
        
        # Memoization
        key = (lap, compound, tyre_age)
        if key in memo:
            return memo[key], parent.get(key, [])
        
        # Check if tyre is unrealistically old - MUST PIT (but only if not too late)
        if is_bad_strategy(tyre_age, compound) and lap <= pit_deadline:
            # Must pit now
            best_time = INF
            best_plan = []
            
            # Try each compound except current
            for new_compound in [0, 1, 2]:
                if new_compound != compound:
                    # Pit penalty + restart with fresh tyres
                    remaining_time, remaining_plan = dp(lap + 1, new_compound, 1)
                    total = pit_penalty + remaining_time
                    
                    if total < best_time:
                        best_time = total
                        best_plan = [("pit", lap, new_compound)] + remaining_plan
            
            # If no good pit option found (too late in race), just continue
            if best_time == INF:
                current_time = predict(lap, tyre_age, compound, temp, laps, track_id, track)
                if lap in events:
                    if events[lap] == "SC":
                        current_time += 2
                    elif events[lap] == "VSC":
                        current_time += 0.5
                remaining_time, remaining_plan = dp(lap + 1, compound, tyre_age + 1)
                best_time = current_time + remaining_time
                best_plan = remaining_plan[:]
            
            memo[key] = best_time
            parent[key] = best_plan
            return best_time, best_plan
        
        # Get current lap time
        current_time = predict(lap, tyre_age, compound, temp, laps, track_id, track)
        
        # Apply race events
        if lap in events:
            if events[lap] == "SC":
                current_time += 2
            elif events[lap] == "VSC":
                current_time += 0.5
        
        # Option 1: Continue on current compound
        remaining_time, remaining_plan = dp(lap + 1, compound, tyre_age + 1)
        best_time = current_time + remaining_time
        best_plan = remaining_plan[:]
        
        # Option 2: Pit (only if strategic and not too late)
        min_stint = 5  # At least 5 laps before pitting
        laps_remaining = laps - lap
        
        # Don't pit if:
        # 1. Too early in current stint
        # 2. Past pit deadline (last 15% of race)
        # 3. Not enough laps remaining to benefit (need at least 8 laps)
        if tyre_age >= min_stint and lap <= pit_deadline and laps_remaining >= 8:
            pit_window_min, pit_window_max = {
                0: strategy_config['soft_pit_window'],
                1: strategy_config['medium_pit_window'],
                2: strategy_config['hard_pit_window'],
            }.get(compound, (10, 20))
            
            # Only pit if in realistic window
            if pit_window_min <= tyre_age <= pit_window_max:
                for new_compound in [0, 1, 2]:
                    if new_compound != compound:
                        pit_time = current_time + pit_penalty
                        remaining_time, remaining_plan = dp(lap + 1, new_compound, 1)
                        total = pit_time + remaining_time
                        
                        if total < best_time:
                            best_time = total
                            best_plan = [("pit", lap, new_compound)] + remaining_plan
        
        memo[key] = best_time
        parent[key] = best_plan
        return best_time, best_plan
    
    # Solve DP
    total_time, strategy_plan = dp(1, start_compound, 1)
    
    return total_time, strategy_plan


def simulate_strategy(laps, temp, start_compound, pit_laps, compounds, track, track_id, events):
    """Simulate a pit strategy."""
    
    cumulative_time = []
    total_time = 0
    current_compound = start_compound
    tyre_age = 1
    pit_idx = 0
    
    for lap in range(1, laps + 1):
        # Check if pitting
        if pit_idx < len(pit_laps) and lap == pit_laps[pit_idx]:
            pit_penalty = strategy_config['pit_penalty']
            total_time += pit_penalty
            current_compound = compounds[pit_idx + 1]
            tyre_age = 1
            pit_idx += 1
        
        # Predict lap time
        lap_time = predict(lap, tyre_age, current_compound, temp, laps, track_id, track)
        
        # Apply race events
        if lap in events:
            if events[lap] == "SC":
                lap_time += 2
            elif events[lap] == "VSC":
                lap_time += 0.5
        
        total_time += lap_time
        cumulative_time.append(total_time)
        tyre_age += 1
    
    return np.array(cumulative_time)