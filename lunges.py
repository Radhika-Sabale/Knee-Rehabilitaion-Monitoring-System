from angle_calculation import calculate_angle

# -------- GLOBAL VARIABLES --------
prev_angle = None
unstable_counter = 0
fast_drop_counter = 0
buffer = []

def process(landmarks):
    global prev_angle, unstable_counter, fast_drop_counter, buffer

    try:
        # -------- LANDMARK SELECTION (Right Leg as Front) --------
        # Lead Leg
        hip = [landmarks[24].x, landmarks[24].y]
        knee = [landmarks[26].x, landmarks[26].y]
        ankle = [landmarks[28].x, landmarks[28].y]

        # Trailing Leg (for stability)
        knee_l = [landmarks[25].x, landmarks[25].y]
        ankle_l = [landmarks[27].x, landmarks[27].y]

        # -------- ANGLE CALCULATION & SMOOTHING --------
        raw_angle = calculate_angle(hip, knee, ankle)

        if raw_angle is None:
            return None, "no detection"

        # Smoothing buffer to prevent jitter
        buffer.append(raw_angle)
        if len(buffer) > 5:
            buffer.pop(0)
        angle = sum(buffer) / len(buffer)

        # -------- PRIMARY STATE LOGIC --------
        if angle > 170:
            state = "up"
        elif angle < 95:
            state = "down"
        else:
            state = "mid"

        # -------- SAFETY: KNEE OVER TOE (Direction Agnostic) --------
        # Uses absolute difference so it works regardless of which way user faces
        if abs(knee[0] - ankle[0]) > 0.12:
            state = "danger_knee_forward"

        # -------- SAFETY: FAST DROP (ECCENTRIC CONTROL) --------
        if prev_angle is not None:
            diff = prev_angle - angle  # Positive diff = moving downward
            if diff > 25 and angle < 145:
                fast_drop_counter += 1
            else:
                fast_drop_counter = 0

        # -------- SAFETY: BALANCE (BACK LEG DRIFT) --------
        # Measures if the back leg is wobbling significantly
        if abs(knee_l[0] - ankle_l[0]) > 0.20:
            unstable_counter += 1
        else:
            unstable_counter = 0

        # -------- FINAL STATE OVERRIDE --------
        if fast_drop_counter >= 2:
            state = "danger_plop"
        elif unstable_counter >= 3:
            state = "danger_unstable"
        
        # Lock state if knee-forward is critical
        if abs(knee[0] - ankle[0]) > 0.15:
            state = "danger_lock"

        prev_angle = angle
        return round(angle, 2), state

    except Exception:
        return None, "error in processing"

def reset():
    global prev_angle, unstable_counter, fast_drop_counter, buffer
    prev_angle = None
    unstable_counter = 0
    fast_drop_counter = 0
    buffer = []

class RepCounter:
    def __init__(self, good_angle=85):
        self.counter = 0
        self.stage = "up"
        self.min_angle = 180
        self.feedback = ""
        self.good_angle = good_angle

    def update(self, state, angle):

        # -------- HANDLE ALL DANGER STATES --------
        if state.startswith("danger_"):
            self.feedback = "Bad Rep"
            return self.counter, self.stage, self.feedback

        # -------- IGNORE INVALID --------
        if state == "no detection" or angle is None:
            return self.counter, self.stage, self.feedback

        if angle < 30 or angle > 170:
            return self.counter, self.stage, self.feedback

        # -------- MID STATE --------
        if state == "mid":
            return self.counter, self.stage, self.feedback

        # -------- GOING DOWN --------
        if state == "down":
            if self.stage != "down":
                self.stage = "down"
                self.min_angle = angle
            self.min_angle = min(self.min_angle, angle)

        # -------- COMING UP → REP COMPLETE --------
        elif state == "up" and self.stage == "down":
            self.stage = "up"
            self.counter += 1

            print("Min angle for this rep:", self.min_angle)

            if self.min_angle <= self.good_angle:
                self.feedback = "Good Rep"
            else:
                self.feedback = "Bad Rep"

            self.min_angle = 180

        return self.counter, self.stage, self.feedback