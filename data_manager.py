import csv
import os
from datetime import datetime

class DataManager:
    def __init__(self, email="unknown"):
        self.file_name = "exercise_data.csv"
        self.session_file = "session_summary.csv"
        self.email = email

        with open(self.file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp", "email", "exercise",
                "angle", "rep_count", "feedback"
            ])

        if not os.path.exists(self.session_file):
            with open(self.session_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "timestamp", "email", "exercise",
                    "total_reps", "good_reps", "bad_reps", "accuracy"
                ])

    def save(self, exercise, angle, rep_count, feedback):
        with open(self.file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.email, exercise, angle, rep_count, feedback
            ])

    def save_session(self, exercise, total, good, bad, accuracy):
        with open(self.session_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.email, exercise, total, good, bad, accuracy
            ])