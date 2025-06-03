import time
import board
import busio
import adafruit_tsl2591
from gpiozero import PWMLED, MotionSensor

# --- Setup ---
pir = MotionSensor(4)
i2c = busio.I2C(board.SCL, board.SDA)
lux_sensor = adafruit_tsl2591.TSL2591(i2c)

# --- RGB Pins ---
red = PWMLED(17)
green = PWMLED(27)
blue = PWMLED(22)

# --- Color Logic ---
def set_color_by_lux(lux):
    print(f"🌞 Lux: {lux:.2f}")
    if lux < 50:
        # Dark room: blue
        red.value = 0.1
        green.value = 0.1
        blue.value = 1.0
    elif lux < 100:
        # Medium: white-ish
        red.value = 0.7
        green.value = 0.7
        blue.value = 0.6
    else:
        # Bright: yellow-orange
        red.value = 1.0
        green.value = 0.6
        blue.value = 0.0
def turn_off_rgb():
    red.off()
    green.off()
    blue.off()

# --- Main Loop ---
print("🚦 System Ready. Waiting for motion...")

motion_active = False

try:
    while True:
        if pir.motion_detected and not motion_active:
            motion_active = True
            print("🚶 Motion detected!")
            lux = lux_sensor.lux or 0
            set_color_by_lux(lux)

        elif not pir.motion_detected and motion_active:
            motion_active = False
            print("❌ Motion ended. Turning off LED.")
            turn_off_rgb()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🛑 Exiting. Cleaning up...")
    turn_off_rgb()
