import serial
import time
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from firebase_admin import credentials, db

# Connect to Arduino (adjust /dev/ttyUSB0 if needed)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to reset

# === Training Data ===
# Features: [motion, light, hour]
X = np.array([
    [0, 5, 21],      # dark room
    [0, 250, 13],    # daylight
    [1, 50, 19],     # evening dim
    [1, 15, 22],     # occupied low
    [1, 10, 23],     # occupied low
    [0, 150, 10],    # daylight
    [1, 5, 2],       # night motion
    [0, 20, 6],      # low morning
    [0, 200, 14],    # idle bright
    [0, 40, 18],     # idle dim
    [1, 180, 18],    # evening bright
    [1, 240, 12],    # daylight
    [1, 30, 5],      # night motion
    [0, 10, 4],      # dark room
    [0, 80, 8],      # low morning
    [1, 120, 9],     # daylight

    # More samples
    [0, 5, 0],       # dark room
    [1, 20, 1],      # night motion
    [0, 100, 7],     # morning moderate
    [1, 30, 7],      # occupied morning
    [0, 220, 15],    # idle bright
    [1, 240, 15],    # active afternoon
    [0, 190, 16],    # idle bright
    [1, 190, 16],    # active afternoon
    [0, 60, 17],     # idle dim
    [1, 60, 17],     # occupied dim
    [0, 15, 20],     # dark room
    [1, 15, 20],     # night motion
    [0, 180, 11],    # daylight
    [1, 180, 11],    # active daylight
    [0, 90, 6],      # low morning
    [1, 90, 6],      # occupied morning
    [0, 130, 13],    # daylight
    [1, 130, 13],    # active daylight
    [0, 0, 3],       # dark room
    [1, 0, 3],       # night motion
])

y = [
    # Labels for original samples
    'dark room', 'daylight', 'evening dim', 'occupied low', 'occupied low', 'daylight',
    'night motion', 'low morning', 'idle bright', 'idle dim', 'evening bright', 'daylight',
    'night motion', 'dark room', 'low morning', 'daylight',

    # Labels for new samples
    'dark room', 'night motion', 'morning moderate', 'occupied morning',
    'idle bright', 'active afternoon', 'idle bright', 'active afternoon',
    'idle dim', 'occupied dim', 'dark room', 'night motion',
    'daylight', 'active daylight', 'low morning', 'occupied morning',
    'daylight', 'active daylight', 'dark room', 'night motion',
]


# Train model
clf = RandomForestClassifier()
clf.fit(X, y)

# === Light Control Functions ===
def classify_scene(motion, light, hour):
    return clf.predict([[motion, light, hour]])[0]

def turn_on_light(level=100):
    print(f"🟡 Light ON at brightness {level}%")

def turn_off_light():
    print("⚫ Light OFF")

# === Main Loop ===
print("Listening for Arduino sensor data...")
while True:
    try:
        try:
            line = ser.readline().decode('utf-8').strip()
        except UnicodeDecodeError:
            print("⚠️ Skipping malformed byte sequence")
            continue

        if not line:
            continue

        try:
            motion_str, light_str = line.split(',')
            motion = int(motion_str.strip())
            light = float(light_str.strip())
            hour = datetime.now().hour

            # Predict scene
            scene = classify_scene(motion, light, hour)
            print(f"[Motion: {motion}, Light: {light:.2f}, Hour: {hour}] → Scene: {scene}")

            # === Scene Control Logic ===
            if scene in ['dark room', 'night motion']:
                ser.write(b'1')  # Full brightness
                ser.flush()
                turn_on_light(100)

            elif scene in ['low morning', 'morning moderate', 'occupied morning']:
                ser.write(b'2')  # Morning setting
                ser.flush()
                turn_on_light(60)

            elif scene in ['idle dim', 'evening dim']:
                ser.write(b'3')  # Dim light
                ser.flush()
                turn_on_light(40)

            elif scene in ['occupied dim', 'occupied low']:
                ser.write(b'4')  # Moderate brightness
                ser.flush()
                turn_on_light(70)

            elif scene in ['idle bright']:
                ser.write(b'5')  # Low brightness (not off)
                ser.flush()
                turn_on_light(30)

            elif scene in ['evening bright', 'active afternoon', 'active daylight']:
                ser.write(b'6')  # Moderate brightness
                ser.flush()
                turn_on_light(50)

            else:  # 'daylight' or any other unrecognized scene
                ser.write(b'0')  # Lights off
                ser.flush()
                turn_off_light()

            time.sleep(0.1)  # Allow Arduino time to process

        except ValueError:
            print("Malformed data:", line)

        time.sleep(2)

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
        break
