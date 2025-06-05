import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cs131-smart-light-default-rtdb.firebaseio.com/'
})

def push_data_to_firebase(data):
    #Real Time Data
    try:
        db.reference('current_data').set(data)
    except Exception as e:
        print(f"[Firebase Error] {e}")

    #Logs
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        db.reference(f'logs/{today}').push(data)
    except Exception as e:
        print(f"[Firebase Error] {e}")

    print("[Firebase] Data pushed!")

if __name__ == "__main__":
    data = {
        "device": "raspberry pi", #What is capturing the data?
        "room": "bedroom", #Where is the data being captured?
        "motion": True, #Are PIR Sensors detecting motion
        "lux": 73, #Represents the ambient light level
        "led_status": "ON", #Is the light on?
        "color": "Red", #What color is our light?
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S") #When this data was logged
    }
    push_data_to_firebase(data)