import serial
import time
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from firebase_admin import credentials, db
import firebase

# Connect to Arduino (adjust /dev/ttyUSB0 if needed)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to reset

# === Training Data ===
# Features: [motion, light, hour]
X = np.array([
    # unoccupied dark
    [0, 0, 1],
    [0, 3, 4],
    [0, 5, 23],

    # occupied dark (night)
    [1, 2, 0],
    [1, 1, 22],
    [1, 3, 2],

    # occupied dark (day)
    [1, 5, 10],
    [1, 4, 8],
    [1, 2, 18],
    
    # unoccupied dim
    [0, 6, 12],
    [0, 20, 7],
    [0, 25, 15],

    # occupied dim (day)
    [1, 15, 10],
    [1, 20, 14],
    [1, 24, 17],

    # occupied dim (night)
    [1, 10, 23],
    [1, 12, 1],
    [1, 18, 4],

    # unoccupied lit
    [0, 30, 12],
    [0, 50, 9],
    [0, 100, 16],

    # occupied lit (day)
    [1, 45, 13],
    [1, 70, 11],
    [1, 90, 17],

    # occupied lit (night)
    [1, 35, 21],
    [1, 60, 0],
    [1, 80, 3],
])

y = [
    "unoccupied dark",
    "unoccupied dark",
    "unoccupied dark",

    "occupied dark (night)",
    "occupied dark (night)",
    "occupied dark (night)",

    "occupied dark (day)",
    "occupied dark (day)",
    "occupied dark (day)",

    "unoccupied dim",
    "unoccupied dim",
    "unoccupied dim",

    "occupied dim (day)",
    "occupied dim (day)",
    "occupied dim (day)",

    "occupied dim (night)",
    "occupied dim (night)",
    "occupied dim (night)",

    "unoccupied lit",
    "unoccupied lit",
    "unoccupied lit",

    "occupied lit (day)",
    "occupied lit (day)",
    "occupied lit (day)",

    "occupied lit (night)",
    "occupied lit (night)",
    "occupied lit (night)"
]

# Train model
clf = RandomForestClassifier()
clf.fit(X, y)

# === Light Control Functions ===
def classify_scene(motion, light, hour):
    return clf.predict([[motion, light, hour]])[0]

def turn_on_light():
    print(f"🟡 Light ON")

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

            data = {
                'device': 'arduino',
                'motion': motion,
                'lux': light,
                'scene': scene,
                'color': "N/A",
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # === Scene Control Logic ===
            if scene == "occupied dark (night)":
                ser.write(b'1')  # amber
                ser.flush()
                turn_on_light()
                data.color = "amber"

            elif scene == "occupied dim (night)":
                ser.write(b'2')  # orange/yellow
                ser.flush()
                turn_on_light()
                data.color = "orange/yellow"

            elif scene == "occupied lit (night)":
                ser.write(b'3')  # soft white
                ser.flush()
                turn_on_light()
                data.color = "soft white"

            elif scene == "occupied dark (day)":
                ser.write(b'4')  # white
                ser.flush()
                turn_on_light()
                data.color = "white"

            elif scene == "occupied dim (day)":
                ser.write(b'5')  # blue
                ser.flush()
                turn_on_light()
                data.color = "blue"

            elif scene == "occupied lit (day)":
                ser.write(b'6')  # dark blue
                ser.flush()
                turn_on_light()
                data.color = "dark blue"

            else:  # 'daylight' or any other unrecognized scene
                ser.write(b'0')  # Lights off
                ser.flush()
                turn_off_light()
                data.color = "OFF"

            firebase.push_data_to_firebase(data)
            time.sleep(0.1)  # Allow Arduino time to process

        except ValueError:
            print("Malformed data:", line)

        time.sleep(2)

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
        break
