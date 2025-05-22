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
    def __init__(self):
        self.logs = []  # Stores in memory

    def log_event(self, data: dict):
        self.logs.append(data)
        print(f"[Cloud] Logged: {data}")
        
    def fetch_config(self):
        return {"min_brightness": 10, "max_brightness": 100}
        
    def get_logs(self):
        return self.logs

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
        user_count = self.light_sensor.count_users()

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
    for _ in range(3):  # Run 3 evaluations, 5 seconds apart
        system.evaluate()
        time.sleep(5)

    print("\n[TEST] Fetching logs from CloudDatabase:")
    logs = system.cloud_db.get_logs()
    for log in logs:
        print(log)

