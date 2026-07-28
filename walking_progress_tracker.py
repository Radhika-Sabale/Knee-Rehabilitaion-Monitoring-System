import cv2
import mediapipe as mp
import numpy as np
import time
import sys
from data_manager import DataManager

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180.0 / np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

# -------- GET EMAIL FROM ARGS --------
email = sys.argv[2] if len(sys.argv) > 2 else "unknown"
data_manager = DataManager(email=email)

# -------- VARIABLES --------
step_count = 0
good_steps = 0
bad_steps = 0
last_step_time = 0
prev_left_x = None
prev_right_x = None
STEP_COOLDOWN = 0.6      # longer wait between steps
STEP_THRESHOLD = 0.08    # needs bigger movement to count
start_time = time.time()
total_distance = 0
feedback = ""

cap = cv2.VideoCapture(0)

with mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # -------- LANDMARKS --------
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,
                    landmarks[mp_pose.PoseLandmark.NOSE.value].y]
            

            # -------- ANGLES --------
            left_angle = calculate_angle(left_hip, left_knee, left_ankle)
            right_angle = calculate_angle(right_hip, right_knee, right_ankle)

            # -------- POSTURE --------
            posture = "Good"
            mid_hip_x = (left_hip[0] + right_hip[0]) / 2
            if abs(nose[0] - mid_hip_x) > 0.1:
                posture = "Leaning"
            if left_angle < 70 or right_angle < 70:
                posture = "Improper"

            # -------- STEP DETECTION (only when landmarks visible) --------
            current_time = time.time()

            if prev_left_x is not None and prev_right_x is not None:
                left_movement = abs(left_ankle[0] - prev_left_x)
                right_movement = abs(right_ankle[0] - prev_right_x)

                if (left_movement > STEP_THRESHOLD or
                        right_movement > STEP_THRESHOLD):
                    if (current_time - last_step_time) > STEP_COOLDOWN:
                        step_count += 1
                        last_step_time = current_time

                        if posture == "Good":
                            good_steps += 1
                            feedback = "Good Step"
                        else:
                            bad_steps += 1
                            feedback = "Bad Step"

                        data_manager.save(
                            "walking",
                            0,
                            step_count,
                            feedback
                        )

            prev_left_x = left_ankle[0]
            prev_right_x = right_ankle[0]

            # -------- DISTANCE & SPEED --------
            stride = distance(left_ankle, right_ankle)
            total_distance += stride
            elapsed_time = time.time() - start_time
            speed = total_distance / elapsed_time if elapsed_time > 0 else 0

            # -------- ACCURACY --------
            accuracy = (good_steps / step_count * 100) if step_count > 0 else 0

            # -------- DRAW POSE --------
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
            )

            # -------- DISPLAY (like other exercises) --------
            cv2.putText(image, f"Exercise: walking", (50, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)

            cv2.putText(image, f"Steps: {step_count}", (50, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(image, f"Posture: {posture}", (50, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            cv2.putText(image, f"Accuracy: {round(accuracy, 1)}%", (50, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            color = (0, 255, 0) if feedback == "Good Step" else (0, 0, 255)
            cv2.putText(image, f"{feedback}", (50, 210),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        else:
            # -------- NO PERSON DETECTED --------
            cv2.putText(image, "No person detected", (50, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Walking Tracker", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# -------- SESSION SUMMARY --------
total = good_steps + bad_steps
accuracy = (good_steps / total * 100) if total > 0 else 0

data_manager.save_session(
    "walking",
    total,
    good_steps,
    bad_steps,
    accuracy
)

cap.release()
cv2.destroyAllWindows()

# -------- PROGRESS GRAPH --------
from progress_graph import generate_graph
generate_graph("walking", email)
