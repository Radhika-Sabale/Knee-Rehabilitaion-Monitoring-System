from angle_calculation import calculate_angle

# -------- GLOBAL VARIABLES --------
prev_angle = None
unstable_counter = 0
fast_movement_counter = 0
buffer = []

def process(landmarks):
    global prev_angle, unstable_counter, fast_movement_counter, buffer

    try:
        # RIGHT LEG (WORKING LEG)
        hip = [landmarks[24].x, landmarks[24].y]
        knee = [landmarks[26].x, landmarks[26].y]
        ankle = [landmarks[28].x, landmarks[28].y]

        # LEFT LEG (SUPPORT/TRAILING LEG)
        knee_l = [landmarks[25].x, landmarks[25].y]
        ankle_l = [landmarks[27].x, landmarks[27].y]

        raw_angle = calculate_angle(hip, knee, ankle)
        if raw_angle is None:
            return None, "no detection"

        # 1. Smoothing Buffer
        buffer.append(raw_angle)
        if len(buffer) > 5: buffer.pop(0)
        angle = sum(buffer) / len(buffer)

        # 2. Corrected State Logic
        if angle > 165:
            state = "up"      # Leg straight, standing ON the step
        elif angle < 105:
            state = "down"    # Foot on step, knee bent (Start position)
        else:
            state = "mid"     # Transitioning

        # 3. Shin Verticality (Safety)
        # Standard: Shin should be close to vertical (small horizontal offset)
        if abs(knee[0] - ankle[0]) > 0.12:
            state = "danger_shin_slant"

        # 4. Speed Check (Control)
        if prev_angle is not None:
            diff = abs(prev_angle - angle)
            # In rehab, controlled ascent/descent is key. 
            # 25 degrees per 5-frame window is a standard limit for 'controlled'
            if diff > 25:
                fast_movement_counter += 1
            else:
                fast_movement_counter = 0

        # 5. Balance Check (Support Leg)
        if abs(knee_l[0] - ankle_l[0]) > 0.15:
            unstable_counter += 1
        else:
            unstable_counter = 0

        prev_angle = angle

        # 6. Final Danger Logic
        if fast_movement_counter >= 2:
            state = "danger_speed"
        elif unstable_counter >= 3:
            state = "danger_unstable"

        return round(angle, 2), state

    except Exception:
        return None, "no detection"

def reset():
    global prev_angle, unstable_counter, fast_movement_counter, buffer
    prev_angle = None
    unstable_counter = 0
    fast_movement_counter = 0
    buffer = []