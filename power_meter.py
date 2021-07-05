from datetime import datetime
from gpiozero import Button
import pdb
import time
import sys

import platform
import paho.mqtt.client as paho

def timestamp_of_pulse(gpio):
    gpio.wait_for_active()
    now = datetime.now()
    print('Pulse Received')
    return now

first_pulse = True
tlast = None
current_power = None

def pulse_cbk():

    global first_pulse
    global tlast
    global current_power


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

node = platform.node()

def on_connect(client, userdata, flags, rc):
    print('Connected')

def on_disconnect(client, userdata, rc):
    print('Disconnected')

client_name = 'client-{0}-{1}'.format(node, sys.argv[0])
print('Will connect as: {0}'.format(client_name))

cl = paho.Client(client_name)
cl.on_connect = on_connect
cl.on_disconnect = on_disconnect

while True:
    try:
        cl.connect('wujskie-rpi-router')
    except Exception as ex:
        print ('Caught {0}, will retry.'.format(str(ex)))
        continue
    break

cl.loop_start()

b = Button(6)
b.when_pressed = pulse_cbk


print('Waiting...')
tlast = timestamp_of_pulse(b)
while True:
    time.sleep(10)
    if current_power != None:
        if current_power < 2000:
            print(f'Publishing power as {current_power} ')
            cl.publish('computing/nodes/{0}/power'.format(node), current_power)
        else:
            print(f'Filtered out bizarre reading of {current_power}, not published')
