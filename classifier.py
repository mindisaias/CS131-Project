import serial
import time
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# Connect to Arduino (adjust /dev/ttyUSB0 if needed)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to reset

# === Training Data ===
# Features: [motion, light, hour]
X = np.array([
    [0, 5, 21],
    [0, 250, 13],
    [1, 50, 19],
    [1, 15, 22],
    [1, 10, 23],
    [0, 150, 10]
])
y = [
    'dark room',
    'daylight',
    'evening dim',
    'occupied low',
    'occupied low',
    'daylight'
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
        line = ser.readline().decode('utf-8').strip()
        if not line:
            continue

        try:
            motion_str, light_str = line.split(',')
            motion = int(motion_str.strip())
            light = float(light_str.strip())
            hour = datetime.now().hour

            # Predict scene
            scene = classify_scene(motion, light, hour)
            print(f"[Motion: {motion}, Light: {light}, Hour: {hour}] → Scene: {scene}")

            # Light logic
            if scene == 'dark room':
                turn_on_light(100)
            elif scene == 'evening dim':
                turn_on_light(50)
            elif scene == 'occupied low':
                turn_on_light(70)
            else:
                turn_off_light()

        except ValueError:
            print("⚠️ Malformed data:", line)

        time.sleep(2)

    except KeyboardInterrupt:
        print("Stopping...")
        break

