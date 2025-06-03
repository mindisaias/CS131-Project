import time
import board
import busio
import adafruit_tsl2591
from gpiozero import PWMLED, MotionSensor
import firebase_admin
from firebase_admin import credentials, db
import logging
from datetime import datetime

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# --- Firebase Setup ---
cred = credentials.Certificate('/home/pi/firebase-key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cs131-smart-light-default-rtdb.firebaseio.com/'
})

# --- Hardware Setup ---
pir = MotionSensor(4)
i2c = busio.I2C(board.SCL, board.SDA)
lux_sensor = adafruit_tsl2591.TSL2591(i2c)

# --- RGB Pins ---
red = PWMLED(17)
green = PWMLED(27)
blue = PWMLED(22)

# --- Helper Functions ---
def interpolate_color(lux, min_lux, max_lux, color_start, color_end):
    ratio = min(max((lux - min_lux) / (max_lux - min_lux), 0), 1)
    r = color_start[0] + (color_end[0] - color_start[0]) * ratio
    g = color_start[1] + (color_end[1] - color_start[1]) * ratio
    b = color_start[2] + (color_end[2] - color_start[2]) * ratio
    return r, g, b

def get_color_by_lux(lux):
    steps = [
        (0, (0.1, 0.1, 0.3), 'dark blue'),
        (20, (0.0, 0.0, 1.0), 'blue'),
        (40, (0.0, 0.5, 1.0), 'sky blue'),
        (60, (0.0, 1.0, 1.0), 'cyan'),
        (80, (0.5, 1.0, 0.5), 'light green'),
        (100, (1.0, 1.0, 0.0), 'yellow'),
        (120, (1.0, 0.7, 0.0), 'amber'),
        (140, (1.0, 0.5, 0.0), 'orange'),
        (160, (1.0, 0.3, 0.3), 'light red'),
        (180, (1.0, 0.0, 0.0), 'red'),
        (200, (1.0, 1.0, 1.0), 'white')
    ]
    for i in range(len(steps) - 1):
        low_lux, low_rgb, _ = steps[i]
        high_lux, high_rgb, _ = steps[i + 1]
        if lux < high_lux:
            r, g, b = interpolate_color(lux, low_lux, high_lux, low_rgb, high_rgb)
            return r, g, b, f"{steps[i][2]} → {steps[i + 1][2]}"
    return *steps[-1][1], steps[-1][2]

def set_rgb_color(r, g, b):
    red.value = r
    green.value = g
    blue.value = b

def turn_off_rgb():
    red.off()
    green.off()
    blue.off()

def log_to_firebase(motion, lux, led_status, color_name):
    data = {
        'device': 'raspberry pi',
        'motion': motion,
        'lux': lux,
        'led_status': led_status,
        'color': color_name,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        db.reference(f'logs/{today}').push(data)
        logging.info(f"📡 Logged to Firebase: {data}")
    except Exception as e:
        logging.error(f"[Firebase Error] {e}")

# --- Main Loop ---
logging.info("🚦 System Ready. Waiting for motion...")
motion_active = False
light_on = False
last_motion_time = None

def get_lux():
    try:
        return lux_sensor.lux or 0
    except RuntimeError:
        logging.warning("[Sensor Warning] Lux overflow, using 200")
        return 200

try:
    while True:
        current_time = time.time()

        if pir.motion_detected:
            if not motion_active:
                motion_active = True
                logging.info("🛎 Motion detected! Turning light ON.")
            last_motion_time = current_time
            lux = get_lux()
            r, g, b, color_name = get_color_by_lux(lux)
            set_rgb_color(r, g, b)
            log_to_firebase(True, lux, 'ON', color_name)
            light_on = True

        elif light_on and last_motion_time and current_time - last_motion_time > 10:
            logging.info("❌ No motion for 10s. Turning light OFF.")
            turn_off_rgb()
            lux = get_lux()
            log_to_firebase(False, lux, 'OFF', 'off')
            motion_active = False
            light_on = False

        time.sleep(0.2)

except KeyboardInterrupt:
    logging.info("\n🚩 Exiting. Cleaning up...")
    turn_off_rgb()
