class RepCounter:
    def __init__(self, good_angle=85):
        self.counter = 0
        self.stage = "up"
        self.min_angle = 180
        self.feedback = ""
        self.good_angle = good_angle

    def update(self, state, angle):
        """
        state: 'up', 'down', 'mid', 'no detection'
        angle: smoothed knee angle
        """

        if state == "danger_plop":
            self.feedback = "Danger: Plopping Down"
            return self.counter, self.stage, self.feedback

        # Ignore invalid frames
        if state == "no detection" or angle is None:
            return self.counter, self.stage, self.feedback

        # Ignore unrealistic angles (noise)
        if angle < 30 or angle > 170:
            return self.counter, self.stage, self.feedback

        # MID STATE → do nothing (prevents false triggers)
        if state == "mid":
            return self.counter, self.stage, self.feedback

        # GOING DOWN
        if state == "down":
            if self.stage != "down":
                self.stage = "down"
                self.min_angle = angle  # reset at start
            
            # track lowest angle
            self.min_angle = min(self.min_angle, angle)

        # COMING UP → REP COMPLETE
        elif state == "up" and self.stage == "down":
            self.stage = "up"
            self.counter += 1

            print("Min angle for this rep:", self.min_angle)

            # CLASSIFICATION 
            if self.min_angle <= self.good_angle:
                self.feedback = "Good Rep"
            else:
                self.feedback = "Bad Rep"

            # reset
            self.min_angle = 180

        return self.counter, self.stage, self.feedback