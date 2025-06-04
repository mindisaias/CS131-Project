import socket
import time
import board
import busio
import adafruit_tsl2591
from gpiozero import MotionSensor, RGBLED

# Setup sensors
pir = MotionSensor(4)
i2c = busio.I2C(board.SCL, board.SDA)
lux_sensor = adafruit_tsl2591.TSL2591(i2c)

# Jetson Nano's Tailscale IP and port
JETSON_IP = '100.74.255.40'
JETSON_PORT = 65432

# Setup RGB LED pins (adjust pins to your wiring)
led = RGBLED(red=17, green=27, blue=22)

def color_name_to_rgb(color_name):
    # Map color strings to RGB values (0-1)
    if color_name == 'dark blue':
        return (0, 0, 1)      # Blue
    elif color_name == 'orange/yellow':
        return (1, 0.5, 0)    # Orange-ish
    elif color_name == 'white':
        return (1, 1, 1)      # White
    else:
        return (0, 0, 0)      # Off / unknown

def smooth_transition(current_rgb, target_rgb, duration=2.0, steps=50):
    """
    Smoothly transitions LED color from current_rgb to target_rgb
    over `duration` seconds in `steps` increments.
    """
    step_delay = duration / steps
    delta = (
        (target_rgb[0] - current_rgb[0]) / steps,
        (target_rgb[1] - current_rgb[1]) / steps,
        (target_rgb[2] - current_rgb[2]) / steps,
    )
    r, g, b = current_rgb
    for _ in range(steps):
        r += delta[0]
        g += delta[1]
        b += delta[2]
        # Clamp values between 0 and 1
        led.color = (max(0, min(r,1)), max(0, min(g,1)), max(0, min(b,1)))
        time.sleep(step_delay)
    # Ensure final color set exactly
    led.color = target_rgb

def send_lux_and_get_color(lux_value):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((JETSON_IP, JETSON_PORT))
            message = str(lux_value)
            sock.sendall(message.encode())
            print(f"Sent lux: {message}")

            # Wait for color response
            color_data = sock.recv(1024).decode()
            print(f"Received color: {color_data}")
            return color_data
    except Exception as e:
        print(f"Connection error: {e}")
        return None

print("Waiting for motion...")

current_color = (0, 0, 0)  # Start with LED off

while True:
    pir.wait_for_motion()
    print("Motion detected!")
    lux = lux_sensor.lux
    color_name = send_lux_and_get_color(lux)
    if color_name:
        target_color = color_name_to_rgb(color_name)
        smooth_transition(current_color, target_color, duration=2.0, steps=50)
        current_color = target_color
    time.sleep(2)
