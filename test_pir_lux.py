import time
import board
import busio
import adafruit_tsl2591
from gpiozero import MotionSensor

# Setup
pir = MotionSensor(4)
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tsl2591.TSL2591(i2c)

motion_active = False

print("👀 Monitoring for motion...")

while True:
    if pir.motion_detected and not motion_active:
        motion_active = True
        lux = sensor.lux
        print("🚶 Motion Detected")
        print(f"🌞 Ambient Light: {lux:.2f} lux")

    elif not pir.motion_detected and motion_active:
        motion_active = False
        print("❌ Motion Stopped")

    time.sleep(0.1)  # Fast check (100ms)

