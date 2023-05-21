#!/usr/bin/env python3
import signal
import sys
import paho.mqtt.client as mqtt #import the client1
import time
import RPi.GPIO as GPIO
import serial

LED = 16
MAX_POWER = 800
INSTANCE = "PowerStation"
BROKER = "192.168.178.230"
USER = "iobroker"
PASSWD = "1evweiden1985"

PORT = "/dev/ttyUSB0"
BAUDRATE = 4800

soyo_power_data = [b'\x24', b'\x56', b'\x00', b'\x21', b'\x00', b'\x00', b'\x80', b'\x08']

GPIO.setwarnings(False)    # Ignore warning for now
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
    ser.close();
    client.loop_stop() #stop the loop
    print('by, by...')
    sys.exit(0)

############
def on_message(client, userdata, message):
    GPIO.output(LED, GPIO.LOW)

    if not hasattr(on_message, "MaxPower"):
      on_message.MaxPower = 0
    if not hasattr(on_message, "LastPower"):
      on_message.LastPower = 0

    #print("message received " ,str(message.payload.decode("utf-8")))
    #print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)

    value = int(float(message.payload.decode("utf-8")))

    if "MaxPower" in message.topic:
      on_message.MaxPower = value
      print("MaxPower set to ", value, " Watt" )
    if "SetPower" in message.topic:
      if value > on_message.MaxPower:
        SetPower = on_message.MaxPower
      else:
        SetPower = value

      if True:
        if SetPower > 0:
          setSoyoPowerData(SetPower)
          print("Soyo limiter set to ", SetPower, " Watt (act. ", value, "/max. ", on_message.MaxPower, ") > ", soyo_power_data)
        else:
          SetPower = 0
          setSoyoPowerData(SetPower)
          print("Soyo limiter set to 0")

      client.publish("PowerStation/SoyoSource/ActPower", SetPower)

      on_message.LastPower = SetPower

    GPIO.output(LED, GPIO.HIGH)
########################################

signal.signal(signal.SIGINT, signal_handler)

print("creating new instance")
client = mqtt.Client(INSTANCE) #create new instance
client.on_message=on_message #attach function to callback

print("connecting to broker")
client.username_pw_set(USER, PASSWD)
client.connect(BROKER) #connect to broker

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

setSoyoPowerData(0)

while True:

  print("SEND alive...");
  client.publish("PowerStation/SoyoSource/TimeStamp", int(time.time()));

  if ser.isOpen():
    ser.write(soyo_power_data)

  time.sleep(2) # wait 1 sec
