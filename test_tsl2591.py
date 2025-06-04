import time
import board
import busio
import adafruit_tsl2591

# Set up I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the TSL2591 sensor
sensor = adafruit_tsl2591.TSL2591(i2c)

while True:
    lux = sensor.lux
    print(f"Lux: {lux}")
    time.sleep(1)
