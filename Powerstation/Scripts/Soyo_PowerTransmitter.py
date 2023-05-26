#!/usr/bin/env python3
import config

import signal
import sys
import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
import serial

LED = 16
MAX_POWER = 500

PORT = "/dev/ttyUSB0"
BAUDRATE = 4800

soyo_power_data = [b'\x24', b'\x56', b'\x00', b'\x21', b'\x00', b'\x00', b'\x80', b'\x08']

GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BCM)   # Use physical pin numbering
GPIO.setup(LED, GPIO.OUT, initial=GPIO.LOW)

def setSoyoPowerData(power):
    soyo_power_data[0] = 36
    soyo_power_data[1] = 86
    soyo_power_data[2] = 0
    soyo_power_data[3] = 33
    soyo_power_data[4] = power >> 8
    soyo_power_data[5] = power & 255
    soyo_power_data[6] = 128
    soyo_power_data[7] = calc_checksumme(soyo_power_data[1], soyo_power_data[2], soyo_power_data[3], soyo_power_data[4], soyo_power_data[5], soyo_power_data[6])

def calc_checksumme(b1, b2, b3, b4, b5, b6):
    calc = (255 - b1 - b2 - b3 - b4 - b5 - b6) % 256
    return calc & 255

def signal_handler(sig, frame):
    client.publish("PowerStation/SoyoSource/ActPower", 0)
    client.loop_stop() #stop the loop
    ser.close();
    print('by, by...')
    sys.exit(0)

############
def on_message(client, userdata, message):

    GPIO.output(LED, GPIO.LOW)

    if not hasattr(on_message, "MaxPower"):
      on_message.MaxPower = 0
    if not hasattr(on_message, "LastPower"):
      on_message.LastPower = 0
    if not hasattr(on_message, "SoyoActive"):
      on_message.SoyoActive = 1

    print(">> message received=", message.payload.decode("utf-8"))
    print(">> message topic=",message.topic)
    print(">> message qos=",message.qos)
    print(">> message retain flag=",message.retain)

    if message.payload.decode("utf-8") != "":
      value = int(float(message.payload.decode("utf-8")))
    else:
      value = 0

    if "MaxPower" in message.topic:
      on_message.MaxPower = value
      print("MaxPower set to %s Watt", value)

    if "SoyoActive" in message.topic:
      on_message.SoyoActive = value
      print("SoyoActive set to %s", value)

    if "SetPower" in message.topic:
      if value > on_message.MaxPower:
        SetPower = on_message.MaxPower
      else:
        SetPower =  on_message.LastPower + value

        if SetPower > on_message.MaxPower:
          SetPower = on_message.MaxPower
        if SetPower < 0:
          SetPower = 0

        print(">>>> last: ", on_message.LastPower)
        print(">>>> act: ", value)
        print(">>>> set: ", SetPower)

      on_message.LastPower = SetPower

      if True:
        if SetPower > 0:
          print(">>>>>> Soyo limiter set to Watt ", SetPower)
        else:
          SetPower = 0
          print(">>>>>> Soyo limiter set to 0")

        setSoyoPowerData(SetPower)

        client.publish("PowerStation/SoyoSource/ActPower", SetPower)

        GPIO.output(LED, GPIO.HIGH)
########################################

signal.signal(signal.SIGINT, signal_handler)

print("creating new instance")
client = mqtt.Client(config.INSTANCE) #create new instance
client.on_message=on_message #attach function to callback

print("connecting to broker")
client.username_pw_set(config.USER, config.PASSWD)
client.connect(config.BROKER) #connect to broker

print("open serial port")
ser = serial.Serial(
               port=PORT,
               baudrate = BAUDRATE,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS)

if (ser.isOpen() == True):
  ser.close()
ser.open()
ser.reset_input_buffer

client.loop_start() #start the loop

print("Subscribing to topic","PowerStation/SoyoSource/SetPower")
client.subscribe("PowerStation/SoyoSource/SetPower")

print("Subscribing to topic","PowerStation/SoyoSource/ActPower")
client.subscribe("PowerStation/SoyoSource/ActPower")

print("Subscribing to topic","PowerStation/SoyoSource/MaxPower")
client.subscribe("PowerStation/SoyoSource/MaxPower")
client.publish("PowerStation/SoyoSource/MaxPower", MAX_POWER)

print("Subscribing to topic","PowerStation/SoyoSource/SoyoActive")
client.subscribe("PowerStation/SoyoSource/SoyoActive")
client.publish("PowerStation/SoyoSource/SoyoActive", 1)

setSoyoPowerData(0)

while True:

  client.publish("PowerStation/SoyoSource/TimeStamp", int(time.time()));

  if ser.isOpen():
    ser.write(soyo_power_data)

  time.sleep(1) # wait 1 sec
