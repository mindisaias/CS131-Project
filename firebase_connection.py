import time
import board
import busio
import adafruit_tsl2591
from gpiozero import PWMLED, MotionSensor
import firebase_admin
from firebase_admin import credentials, db
import logging
from datetime import datetime
from threading import Timer

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

# --- Globals ---
light_on = False
off_timer = None
OFF_DELAY = 10  # seconds to wait after last motion before turning off

def get_color_by_lux(lux):
    if lux < 50:
        return 0.1, 0.1, 0.3, 'dark blue'
    elif lux < 150:
        ratio = (lux - 50) / 100
        r = 1.0
        g = 0.4 + (1.0 - 0.4) * ratio
        b = 0.0
        return r, g, b, 'orange/yellow'
    else:
        return 1.0, 1.0, 1.0, 'white'

def set_rgb_color(r, g, b):
    red.value = r
    green.value = g
    blue.value = b

def turn_off_rgb():
    global light_on
    red.off()
    green.off()
    blue.off()
    light_on = False
    logging.info("❌ Light turned OFF")

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

def get_lux():
    try:
        return lux_sensor.lux or 0
    except RuntimeError:
        logging.warning("[Sensor Warning] Lux overflow, using 200")
        return 200

def motion_detected():
    global light_on, off_timer
    lux = get_lux()
    r, g, b, color_name = get_color_by_lux(lux)
    set_rgb_color(r, g, b)
    log_to_firebase(True, lux, 'ON', color_name)

    if off_timer:
        off_timer.cancel()  # cancel scheduled off if motion detected again
    light_on = True
    logging.info("🛎 Motion detected! Light ON.")

def no_motion():
    global off_timer
    # Schedule turning off the light after OFF_DELAY seconds
    if off_timer:
        off_timer.cancel()

    def off_light():
        lux = get_lux()
        log_to_firebase(False, lux, 'OFF', 'off')
        turn_off_rgb()

    off_timer = Timer(OFF_DELAY, off_light)
    off_timer.start()
    logging.info(f"⌛ No motion detected. Will turn off light in {OFF_DELAY}s if no new motion.")

# Assign callbacks
pir.when_motion = motion_detected
pir.when_no_motion = no_motion

logging.info("🚦 System Ready. Waiting for motion...")

try:
    # Keep the program running so callbacks work
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("\n🚩 Exiting. Cleaning up...")
    if off_timer:
        off_timer.cancel()
    turn_off_rgb()
