from angle_calculation import calculate_angle

def analyze_knee_angle(angle):
    """
    Analyze knee angle and return exercise state (Rehab-focused).

    States:
    - "up"        -> correct rehab range (safe top)
    - "down"      -> start position (bent)
    - "vmo"       -> terminal extension (optional zone)
    - "mid"       -> transition zone
    - "danger"    -> hyperextension
    """

    if angle is None:
        return "no detection"

    # True danger: hyperextension
    if angle > 180:
        return "danger"

    # VMO / terminal extension zone (advanced rehab)
    if 150 <= angle <= 180:
        return "vmo"

    # SAFE rehab top (MOST IMPORTANT)
    if 135 <= angle < 150:
        return "up"

    # Start position
    elif angle < 100:
        return "down"

    # Transition zone
    else:
        return "mid"


def process(landmarks):
    """
    Processes landmarks for Seated Knee Extension.

    Returns:
        angle (float)
        state (str)
    """

    # LEFT leg landmarks
    hip = (landmarks[23].x, landmarks[23].y)
    knee = (landmarks[25].x, landmarks[25].y)
    ankle = (landmarks[27].x, landmarks[27].y)

    # Calculate angle
    angle = calculate_angle(hip, knee, ankle)

    if angle is None:
        return None, "no detection"

    # Analyze state
    state = analyze_knee_angle(angle)

    return angle, state