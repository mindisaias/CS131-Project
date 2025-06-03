import serial
import time
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# --- Connect to Arduino ---

# On jetson nano, run this command to get port: ls /dev/ttyACM* or dmesg | grep tty
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

# === Training Data ===
# Features: [motion (0/1), light (lux), hour of day (0-23)]

X_train = np.array([
    [0, 5, 22],     # dark, no motion, late night
    [0, 250, 14],   # bright, no motion, afternoon
    [1, 50, 19],    # dim, motion, evening
    [1, 30, 23],    # very dark, motion, late night
    [1, 100, 12],   # medium bright, motion, noon
    [0, 120, 9],    # medium bright, no motion, morning
    [1, 10, 6],     # very dark, motion, early morning
    [0, 15, 20],    # dark, no motion, evening
    [1, 200, 16],   # bright, motion, afternoon
    [0, 180, 13],   # bright, no motion, early afternoon
    [1, 80, 21],    # dim, motion, night
    [0, 40, 5],     # dark, no motion, very early morning
    [1, 5, 18],     # very dark, motion, early evening
])

# Labels (commands to Arduino):
# 0 = Turn LED OFF
# 1 = Very bright light (dark room)
# 2 = Bright light (slightly lit room)
# 3 = Balanced light (50/50 lit room)

y_train = [
    0,  # OFF
    0,  # OFF
    3,  # Balanced light
    1,  # Bright light
    2,  # Medium bright light
    0,  # OFF
    1,  # Bright light
    0,  # OFF
    2,  # Medium bright light
    0,  # OFF
    3,  # Balanced light
    0,  # OFF
    1,  # Bright light
]

clf = RandomForestClassifier()
clf.fit(X_train, y_train)

def send_command(command):
    ser.write(str(command).encode('utf-8'))
    print(f"Sent command: {command}")

print("Starting sensor data reading and light control loop...")

while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        if not line:
            continue

        try:
        # Arduino sends "motion,light"
            motion_str, light_str = line.split(',')
            motion = int(motion_str)
            light = float(light_str)
            hour = datetime.now().hour

            # Prepare feature vector and predict command
            features = np.array([[motion, light, hour]])
            command = clf.predict(features)[0]

            print(f"Received - Motion: {motion}, Light: {light:.2f} lux, Hour: {hour}")
            print(f"Predicted command to Arduino: {command}")

            # Send command back to Arduino
            send_command(command)

        except ValueError:
            print(f"⚠️ Malformed data received: {line}")

        time.sleep(2)

    except KeyboardInterrupt:
        print("Program stopped by user.")
        break

