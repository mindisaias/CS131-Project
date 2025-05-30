import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cs131-smart-light-default-rtdb.firebaseio.com/'  # Replace this
})

data = {
    "motion": True, #Are PIR Sensors detecting motion
    "lux": 73, #Represents the ambient light level
    "led_status": "ON", #Is the light on?
    "color": "Red", #What color is our light?
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S") #When this data was logged
}

#Real Time Data
db.reference('current_data').set(data)

#Logs
db.reference('logs').push(data)

print("Data pushed to Firebase!")