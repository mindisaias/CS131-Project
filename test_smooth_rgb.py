import time
import board
import busio
from gpiozero import PWMLED, MotionSensor
import adafruit_tsl2591
import logging
from threading import Timer

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Setup I2C and sensors
i2c = busio.I2C(board.SCL, board.SDA)
lux_sensor = adafruit_tsl2591.TSL2591(i2c)

red = PWMLED(17)
green = PWMLED(27)
blue = PWMLED(22)

pir = MotionSensor(4)

# Global variables
motion_active = False
last_motion_time = 0
motion_timeout = 10  # seconds light stays on after last motion
current_rgb = (0, 0, 0)
target_rgb = (0, 0, 0)
fade_steps = 50
fade_delay = 0.02

def clamp(value, minv, maxv):
    return max(minv, min(value, maxv))

def lux_to_rgb(lux):
    # Clamp lux to 0-200 for mapping
    lux = clamp(lux, 0, 200)
    # Map lux to a continuous blue->orange->white gradient
    if lux <= 60:
        # blue shades from dim to bright
        scale = lux / 60
        r = 0.0
        g = 0.0
        b = 0.2 + 0.8 * scale
        color_name = "blue"
    elif lux <= 120:
        # orange shades from dim to bright
        scale = (lux - 60) / 60
        r = 0.5 + 0.5 * scale
        g = 0.25 + 0.25 * scale
        b = 0.0
        color_name = "orange"
    else:
        # white shades from dim to bright
        scale = (lux - 120) / 80
        r = 0.5 + 0.5 * scale
        g = 0.5 + 0.5 * scale
        b = 0.5 + 0.5 * scale
        color_name = "white"
    return (r, g, b), color_name

def smooth_transition(from_rgb, to_rgb, steps=fade_steps, delay=fade_delay):
    for i in range(1, steps+1):
        r = from_rgb[0] + (to_rgb[0] - from_rgb[0]) * i / steps
        g = from_rgb[1] + (to_rgb[1] - from_rgb[1]) * i / steps
        b = from_rgb[2] + (to_rgb[2] - from_rgb[2]) * i / steps
        red.value = r
        green.value = g
        blue.value = b
        time.sleep(delay)

def turn_off():
    global current_rgb
    smooth_transition(current_rgb, (0,0,0))
    red.off()
    green.off()
    blue.off()
    current_rgb = (0,0,0)
    logging.info("💡 Light turned OFF.")

def update_light():
    global current_rgb, target_rgb
    lux = lux_sensor.lux or 0
    rgb, color_name = lux_to_rgb(lux)
    if rgb != target_rgb:
        logging.info(f"🌞 Lux: {lux:.2f} → Color: {color_name}")
        smooth_transition(current_rgb, rgb)
        current_rgb = rgb
        target_rgb = rgb

def on_motion():
    global motion_active, last_motion_time
    motion_active = True
    last_motion_time = time.time()
    logging.info("🚶 Motion detected! Light ON.")
    update_light()

def on_no_motion():
    global motion_active, last_motion_time
    motion_active = False
    last_motion_time = time.time()
    logging.info("⏳ Motion stopped. Light will turn off after timeout.")

# PIR event handlers
pir.when_motion = on_motion
pir.when_no_motion = on_no_motion

logging.info("🚦 System ready. Waiting for motion...")

try:
    while True:
        if motion_active:
            update_light()
        else:
            # If no motion, check if timeout passed to turn off light
            if current_rgb != (0,0,0) and (time.time() - last_motion_time) > motion_timeout:
                turn_off()
        time.sleep(0.1)

except KeyboardInterrupt:
    logging.info("🛑 Exiting. Cleaning up...")
    turn_off()
