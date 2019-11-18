#! /usr/bin/python

import RPi.GPIO as IO 
import time 

# see RPi docs for correct pin to connect white PWM cable to
# also connect black cable to ground pin of RPi
INPUT_PIN = 18

# print warnings and error messages to console
IO.setwarnings(True)

IO.setmode(IO.BCM)

# set input pin
IO.setup(INPUT_PIN, IO.OUT)

# set frequency to 350Hz
p = IO.PWM(INPUT_PIN, 350)

# set PWM duty cycle to 33%
# this makes 1ms pulses that the camera interprets as standby
p.start(33)

# allow half a second of 1ms pulses
time.sleep(0.5)

# set PWM duty cycle to 66% 
# this makes 2ms pulses that the camera interprets as trigger
p.ChangeDutyCycle(66)

# allow 0.2 seconds for the trigger
time.sleep(0.2)

# return to standby pulses
p.ChangeDutyCycle(33)

# allow half a second of 1ms pulses
time.sleep(0.5)

# give input pin back to the OS
IO.cleanup()
