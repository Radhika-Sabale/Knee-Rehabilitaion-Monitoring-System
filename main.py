import os
import sys
import lunges
import squats
import step_ups

if os.path.exists("exercise_data.csv"):
    os.remove("exercise_data.csv")

import cv2
import progress_graph

from exercise_selector import get_exercise
from pose_detection import PoseDetector
from rep_counter import RepCounter
from data_manager import DataManager

from seated_knee_extension import process as knee_extension_process
from sit_to_stand import process as sit_to_stand_process, reset as sit_reset
from squats import process as squats_process
from lunges import process as lunges_process
from step_ups import process as step_ups_process

# ---------------- GET ARGS ----------------
choice = sys.argv[1] if len(sys.argv) > 1 else None
email = sys.argv[2] if len(sys.argv) > 2 else "unknown"

exercise_type = get_exercise(choice)

# -------- WALKING — launch separately --------
if exercise_type == "walking":
    import subprocess
    subprocess.Popen([sys.executable, "walking_progress_tracker.py", choice, email])
    sys.exit()

# RESET
if exercise_type == "sit_to_stand":
    sit_reset()
elif exercise_type == "squats":
    squats.reset()
elif exercise_type == "lunges":
    lunges.reset()
elif exercise_type == "step_ups":
    step_ups.reset()

# ---------------- INITIALIZATION ----------------
cap = cv2.VideoCapture(0)
detector = PoseDetector()

if exercise_type == "knee_extension":
    rep_counter = RepCounter(good_angle=70)
elif exercise_type == "sit_to_stand":
    rep_counter = RepCounter(good_angle=85)
elif exercise_type == "step_ups":
    rep_counter = RepCounter(good_angle=95)
elif exercise_type == "squats":
    rep_counter = RepCounter(good_angle=100)
elif exercise_type == "lunges":
    rep_counter = RepCounter(good_angle=105)
else:
    rep_counter = RepCounter(good_angle=70)

data_manager = DataManager(email=email)

angle_history = []
SMOOTHING_WINDOW = 5
last_count = 0
good_reps = 0
bad_reps = 0

# ---------------- MAIN LOOP ----------------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    image, results = detector.process_frame(frame)
    smooth_angle = None
    state = ""
    count = 0
    feedback = ""
    angle = None

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        if exercise_type == "knee_extension":
            angle, state = knee_extension_process(landmarks)
        elif exercise_type == "sit_to_stand":
            angle, state = sit_to_stand_process(landmarks)
        elif exercise_type == "step_ups":
            angle, state = step_ups_process(landmarks)
        elif exercise_type == "squats":
            angle, state = squats_process(landmarks)
        elif exercise_type == "lunges":
            angle, state = lunges_process(landmarks)
    else:
        cv2.putText(image, "No person detected", (50, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if angle is not None:
        angle_history.append(angle)
        if len(angle_history) > SMOOTHING_WINDOW:
            angle_history.pop(0)

        smooth_angle = sum(angle_history) / len(angle_history)
        count, stage, feedback = rep_counter.update(state, smooth_angle)

        if count != last_count:
            if feedback == "Good Rep":
                good_reps += 1
            elif feedback == "Bad Rep":
                bad_reps += 1

            data_manager.save(
                exercise_type,
                round(smooth_angle, 2),
                count,
                feedback
            )
            last_count = count

        cv2.putText(image, f"Exercise: {exercise_type}", (50, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
        cv2.putText(image, f"Angle: {int(smooth_angle)}", (50, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(image, f"State: {state}", (50, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(image, f"Reps: {count}", (50, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        color = (0, 255, 0) if feedback == "Good Rep" else (0, 0, 255)
        cv2.putText(image, f"{feedback}", (50, 210),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    image = detector.draw_landmarks(image, results)
    cv2.imshow("Knee Rehabilitation System", image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------- SESSION SUMMARY ----------------
total = good_reps + bad_reps
accuracy = (good_reps / total) * 100 if total != 0 else 0

data_manager.save_session(
    exercise_type, total, good_reps, bad_reps, accuracy
)

cap.release()
cv2.destroyAllWindows()

progress_graph.show_graph(exercise_type, email)