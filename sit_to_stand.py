from angle_calculation import calculate_angle


# ---------------- STATE LOGIC ----------------
def analyze_sit_to_stand(angle):

    if angle is None:
        return "no detection"

    if angle < 70:
        return "danger_bend"

    if angle > 170:
        return "up"

    elif angle < 110:
        return "down"

    else:
        return "mid"


# ---------------- MAIN PROCESS ----------------
def process(landmarks):

    hip = (landmarks[23].x, landmarks[23].y)
    knee = (landmarks[25].x, landmarks[25].y)
    ankle = (landmarks[27].x, landmarks[27].y)

    angle = calculate_angle(hip, knee, ankle)

    if angle is None:
        return 0, "no detection"

    # smoothing buffer
    if not hasattr(process, "buffer"):
        process.buffer = []

    process.buffer.append(angle)

    if len(process.buffer) > 5:
        process.buffer.pop(0)

    angle = sum(process.buffer) / len(process.buffer)

    # initialize prev angle safely
    if not hasattr(process, "prev_angle") or process.prev_angle is None:
        process.prev_angle = angle
        angle_change = 0
    else:
        angle_change = process.prev_angle - angle
        process.prev_angle = angle

    # state detection
    state = analyze_sit_to_stand(angle)

    # plop detection
    if angle_change > 25 and angle < 130:
        state = "danger_plop"

    # ALWAYS RETURN
    return angle, state


# ---------------- RESET ----------------
def reset():
    process.prev_angle = None
    process.buffer = []