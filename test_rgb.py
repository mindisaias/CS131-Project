from gpiozero import PWMLED
from time import sleep

# Setup
red = PWMLED(17)
green = PWMLED(27)
blue = PWMLED(22)

# Test red
print("🔴 Red")
red.value = 1
green.value = 0
blue.value = 0
sleep(2)

# Test green
print("🟢 Green")
red.value = 0
green.value = 1
blue.value = 0
sleep(2)

# Test blue
print("🔵 Blue")
red.value = 0
green.value = 0
blue.value = 1
sleep(2)

# Test white (all on)
print("⚪ White")
red.value = 1
green.value = 1
blue.value = 1
sleep(2)

# Turn off
print("❌ Off")
red.off()
green.off()
blue.off()

