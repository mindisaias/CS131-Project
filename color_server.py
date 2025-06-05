import socket
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://cs131-smart-light-default-rtdb.firebaseio.com/'
    })

import numpy as np

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

clf = RandomForestClassifier()
clf.fit(X, y)

def classify_scene(motion, light, hour):
    return clf.predict([[motion, light, hour]])[0]



def get_color_from_data(lux):
    hour = datetime.now().hour
    scene = classify_scene(True, lux, hour)

    if scene == 'unoccupied dark':
        return 'off', scene
    elif scene == 'occupied dark (day)':
        return 'white', scene
    elif scene == 'occupied dark (night)':
        return 'amber', scene
    elif scene == 'unoccupied dim':
        return 'off', scene
    elif scene == 'occupied dim (day)':
        return 'blue', scene
    elif scene == 'occupied dim (night)':
        return 'orange/yellow'
    elif scene == 'unoccupied lit':
        return 'off', scene
    elif scene == 'occupied lit (day)':
        return 'dark blue', scene
    elif scene == 'occupied lit (night)':
        return 'soft white', scene
    else:
        return 'unknown error occurred', scene

def log_to_firebase(motion, lux, color_name, scene):
    data = {
        'device': 'raspberry pi',
        'motion': motion,
        'lux': lux,
        'scene': scene,
        'color': color_name,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        db.reference('current_data').set(data)
        today = datetime.now().strftime("%Y-%m-%d")
        db.reference(f'logs/{today}').push(data)
        logging.info(f"Logged to Firebase: {data}")
    except Exception as e:
        logging.error(f"[Firebase Error] {e}")

# --- Server Setup ---
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('0.0.0.0', 65432)
server_socket.bind(server_address)
server_socket.listen(1)

print("Jetson server is waiting for connection...")

while True:
    connection, client_address = server_socket.accept()
    try:
        print(f"Connection from {client_address}")
        while True:
            data = connection.recv(1024).decode()
            if not data:
                break
            print(f"Received lux value: {data}")

            try:
                lux_value = float(data)
            except ValueError:
                logging.warning(f"Invalid lux value received: {data}")
                continue
            color_name, scene = get_color_from_data(lux_value)
            log_to_firebase(True, lux_value, color_name, scene)

            # Send color string back to Pi
            connection.sendall(color_name.encode())

    finally:
        connection.close()


