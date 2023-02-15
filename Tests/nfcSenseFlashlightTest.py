#https://www.elektronik-kompendium.de/sites/raspberry-pi/2611151.htm
import RPi.GPIO as GPIO
import time

GPIO.setmode (GPIO.BCM)
GPIO.setup (25, GPIO.OUT)
GPIO.setup (3, GPIO.IN) #GPIO.setup(taste, GPIO.IN, pull_up_down = GPIO.PUD_UP) # https://cool-web.de/raspberry/interne-raspberry-pullup-vorwiderstaende-nutzen.htm

dly = 10
while True:
    if GPIO.input(3) == True:
       GPIO.output(25, True)
       time.sleep(1)
       GPIO.output(25, False)

