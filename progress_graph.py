import csv
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
from collections import defaultdict
import os

def generate_graph(exercise_type, email):
    file_name = "session_summary.csv"

    if not os.path.exists(file_name):
        return None

    date_accuracy = defaultdict(list)

    with open(file_name, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["exercise"] == exercise_type and row["email"] == email:
                date = row["timestamp"].split(" ")[0]
                acc = float(row["accuracy"])
                date_accuracy[date].append(acc)

    if len(date_accuracy) == 0:
        return None

    dates = []
    avg_accuracy = []
    for date in sorted(date_accuracy.keys()):
        dates.append(date)
        avg_accuracy.append(sum(date_accuracy[date]) / len(date_accuracy[date]))

    plt.figure()
    plt.plot(dates, avg_accuracy, marker='o')
    plt.xlabel("Date")
    plt.ylabel("Accuracy (%)")
    plt.title(f"Daily Progress - {exercise_type} ({email})")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save to static folder
    safe_email = email.replace('@', '_').replace('.', '_')
    filename = f"progress_{exercise_type}_{safe_email}.png"
    plt.savefig(os.path.join("static", filename))
    plt.close()

    return filename

def show_graph(exercise_type, email):
    generate_graph(exercise_type, email)