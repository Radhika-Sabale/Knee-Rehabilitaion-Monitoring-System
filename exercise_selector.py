def get_exercise(choice=None):
    if choice is None:
        print("Select Exercise:")
        print("1 : Seated Knee Extension")
        print("2 : Squats")
        print("3 : Sit-to-Stand")
        print("4 : Step-Ups")
        print("5 : Lunges")
        print("6 : Walking")
        choice = input("Enter choice (1/2/3/4/5/6): ")

    mapping = {
        "1": "knee_extension",
        "2": "squats",
        "3": "sit_to_stand",
        "4": "step_ups",
        "5": "lunges",
        "6": "walking"
    }

    exercise = mapping.get(str(choice), "knee_extension")
    if exercise == "knee_extension" and str(choice) not in mapping:
        print("Invalid choice, defaulting to knee extension.")
    return exercise