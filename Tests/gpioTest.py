import RPi.GPIO as GPIO
import time

GPIO.setmode (GPIO.BCM)
GPIO.setup (17, GPIO.OUT)
GPIO.setup (27, GPIO.OUT)
GPIO.setup (22, GPIO.OUT)
while True:
    print("0")
    GPIO.output(17, False)
    GPIO.output(27, False)
    GPIO.output(22, False)
    time.sleep(3)
    print("1")
    GPIO.output(17, True)
    GPIO.output(27, False)
    GPIO.output(22, False)
    time.sleep(3)
    print("2")
    GPIO.output(17, False)
    GPIO.output(27, True)
    GPIO.output(22, False)
    time.sleep(3)
    print("3")
    GPIO.output(17, True)
    GPIO.output(27, True)
    GPIO.output(22, False)
    time.sleep(3)
    print("4")
    GPIO.output(17, False)
    GPIO.output(27, False)
    GPIO.output(22, True)
    time.sleep(3)
    print("5")
    GPIO.output(17, True)
    GPIO.output(27, False)
    GPIO.output(22, True)
    time.sleep(3)
    print("6")
    GPIO.output(17, False)
    GPIO.output(27, True)
    GPIO.output(22, True)
    time.sleep(3)
    print("7")
    GPIO.output(17, True)
    GPIO.output(27, True)
    GPIO.output(22, True)
    time.sleep(3)

