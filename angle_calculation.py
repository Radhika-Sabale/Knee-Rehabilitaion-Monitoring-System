import numpy as np

def calculate_angle(a, b, c):
    """
    Calculate the angle at point b (knee) using three points:
    a = hip (x, y)
    b = knee (x, y)
    c = ankle (x, y)
    """

    # Safety check
    if a is None or b is None or c is None:
        return None

    # Convert to numpy arrays
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    # Calculate angle using arctan2
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])

    angle = np.degrees(np.abs(radians))

    # Normalize angle (0–180 degrees)
    if angle > 180:
        angle = 360 - angle

    return angle