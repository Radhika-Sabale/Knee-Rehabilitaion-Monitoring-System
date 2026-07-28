from angle_calculation import calculate_angle

# -------- GLOBAL VARIABLES --------
prev_angle = None
frame_drop_counter = 0
buffer = []

def process(landmarks):
    global prev_angle, frame_drop_counter, buffer

    try:
        # -------- GET LANDMARKS (RIGHT LEG) --------
        hip = [landmarks[24].x, landmarks[24].y]
        knee = [landmarks[26].x, landmarks[26].y]
        ankle = [landmarks[28].x, landmarks[28].y]

        # -------- CALCULATE & SMOOTH ANGLE --------
        raw_angle = calculate_angle(hip, knee, ankle)
        if raw_angle is None:
            return None, "no detection"

        buffer.append(raw_angle)
        if len(buffer) > 5:
            buffer.pop(0)
        angle = sum(buffer) / len(buffer)

        # -------- STATE LOGIC (Rehab Standards) --------
        if angle > 170: # Standard for full standing extension
            state = "up"
        elif angle < 95: # 90-95 is the 'parallel' goal
            state = "down"
        else:
            state = "mid"

        # -------- SPEED CHECK (ANTI-PLUNGE) --------
        if prev_angle is not None:
            diff = prev_angle - angle # Positive = dropping down
            if diff > 25 and angle < 140: # Only check speed in the active zone
                frame_drop_counter += 1
            else:
                frame_drop_counter = 0

        # -------- SPATIAL SAFETY (KNEE TRAVEL) --------
        # If knee horizontal distance from ankle is too large
        if abs(knee[0] - ankle[0]) > 0.12:
            state = "danger_knee_forward"

        # -------- DANGER LOCK OVERRIDE --------
        if frame_drop_counter >= 2:
            state = "danger_plop"
            
        prev_angle = angle
        return round(angle, 2), state

    except Exception:
        return None, "no detection"

def reset():
    global prev_angle, frame_drop_counter, buffer
    prev_angle = None
    frame_drop_counter = 0
    buffer = []