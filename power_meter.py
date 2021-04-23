from datetime import datetime
from gpiozero import Button
import pdb
import time

def timestamp_of_pulse(gpio):
    gpio.wait_for_active()
    now = datetime.now()
    print('Pulse Received')
    return now

first_pulse = True
tlast = None

def pulse_cbk():

    global first_pulse
    global tlast


    now = datetime.now()

    if first_pulse:
        first_pulse = False
        tlast = now
        return

    td = (now - tlast).total_seconds()
    tlast = now
    print(f'Pulse Received, current len is {td} s')
    current_power = 3600 / td
    print(f'Current power is {current_power} W')

b = Button(6)
b.when_pressed = pulse_cbk


print('Waiting...')
tlast = timestamp_of_pulse(b)
while True:
    time.sleep(1)
