import time
from datetime import datetime, timedelta

class MotionSensor:
    def detect_motion(self) -> bool:
        return True

class LightSensor:
    def count_users(self) -> int:
        return 0

class LEDController:
    def set_brightness(self, level: int):
        print(f"[LED] Brightness set to: {level}%")

class CloudDatabase:
    def log_event(self, data: dict):
        print(f"[Cloud] Logged: {data}")
        
    def fetch_config(self):
        return {"min_brightness": 10, "max_brightness": 100}

class LightingSystem:
    def __init__(self):
        self.motion_sensor = MotionSensor()
        self.light_sensor = LightSensor()
        self.led_controller = LEDController()
        self.cloud_db = CloudDatabase()
        self.last_motion_time = datetime.now()

    def evaluate(self):
        motion_detected = self.motion_sensor.detect_motion()

        if motion_detected:
            self.last_motion_time = datetime.now()

        #"Active" if motion within last 5 minutes
        active = datetime.now() - self.last_motion_time < timedelta(minutes=5)

        if user_count == 0 or not active:
            brightness = 0
        else:
            config = self.cloud_db.fetch_config()
            brightness = min(config["max_brightness"], user_count * 20)
            brightness = max(config["min_brightness"], brightness)

        self.led_controller.set_brightness(brightness)
        self.cloud_db.log_event({
            "timestamp": datetime.now().isoformat(),
            "users": user_count,
            "active": active,
            "brightness": brightness
        })

if __name__ == "__main__":
    system = LightingSystem()
    while True:
        system.evaluate()
        time.sleep(5)
