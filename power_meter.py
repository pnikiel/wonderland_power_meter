from datetime import datetime
from gpiozero import Button
import pdb
import time
import sys

import platform
import paho.mqtt.client as paho
import argparse
import json

def timestamp_of_pulse(gpio):
    gpio.wait_for_active()
    now = datetime.now()
    print('Pulse Received')
    return now

first_pulse = True
tlast = None
current_power = None
kwh_factor = 1000 # this is the prevalent case, and will be updated anyway later

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
    current_power = int(3600*1000 / (kwh_factor * td))
    print(f'Current power is {current_power} W')

node = platform.node()

def on_connect(client, userdata, flags, rc):
    print('Connected')

def on_disconnect(client, userdata, rc):
    print('Disconnected')

def main():


    global tlast

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_name', required=True)


    args = parser.parse_args()

    input_name = args.input_name

    hw_desc_f = open(f'/wonderland-main/hw_desc/{node}/power_meter.json')
    hw_desc_j = json.load(hw_desc_f)

    if not input_name in hw_desc_j:
        print(f'{input_nane} seems missing in da config')
        return
   
    hw_desc = hw_desc_j[input_name]

    client_name = f'client-{node}-power_meter-{input_name}'
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

    global kwh_factor
    kwh_factor = hw_desc['kwh_factor']
    b = Button(hw_desc['pin'])
    b.when_pressed = pulse_cbk

    topic = f"computing/nodes/{node}/power_{input_name}"

    print('Waiting...')
    tlast = timestamp_of_pulse(b)
    while True:
        time.sleep(10)
        if current_power != None:  # not the first time run
            # if there was no pulse for long time, assume power of zero.

            now = datetime.now()
            td = (now - tlast).total_seconds()
            timeup_5W = 1000*3600 / (kwh_factor * 5) # max pulse wait for 5W limit
            if td > timeup_5W:
                # just assume below 5W limit publish zero
                cl.publish(topic, 0)
            else:
                if current_power < 3600:
                    print(f'Publishing power as {current_power} ')
                    cl.publish(topic, current_power)
                else:
                    print(f'Filtered out bizarre reading of {current_power}, not published')


if __name__ == "__main__":
    main()

