import socket
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# --- Firebase Setup ---
cred = credentials.Certificate('/home/ivill058-awang236/final-project/CS131-Project/firebase-key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cs131-smart-light-default-rtdb.firebaseio.com/'
})

def get_color_from_lux(lux):
    if lux < 50:
        return 'dark blue'
    elif lux < 150:
        return 'orange/yellow'
    else:
        return 'white'

def log_to_firebase(motion, lux, color_name):
    data = {
        'device': 'raspberry pi',
        'motion': motion,
        'lux': lux,
        'color': color_name,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        db.reference(f'logs/{today}').push(data)
        logging.info(f"📡 Logged to Firebase: {data}")
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

            color_name = get_color_from_lux(lux_value)

            # Log to Firebase without led_status
            log_to_firebase(
                motion=True,
                lux=lux_value,
                color_name=color_name
            )

            # Send color string back to Pi
            connection.sendall(color_name.encode())

    finally:
        connection.close()

