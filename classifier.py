import serial
import time
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# Connect to Arduino (adjust /dev/ttyUSB0 if needed)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
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

            # Send LED control command to Arduino
            if scene == 'dark room':
                ser.write(b'1')
                ser.flush()  # ensure it's sent
                turn_on_light(100)

            elif scene == 'evening dim':
                ser.write(b'2')
                ser.flush()
                turn_on_light(50)

            elif scene == 'occupied low':
                ser.write(b'3')
                ser.flush()
                turn_on_light(70)

            else:  # scene == 'daylight' or anything else
                ser.write(b'0')
                ser.flush()
                turn_off_light()

            time.sleep(0.1)  # Give Arduino time to process command

        except ValueError:
            print("Malformed data:", line)

        time.sleep(2)  # Control loop speed

    except KeyboardInterrupt:
        print("\n Program stopped by user.")
        break

