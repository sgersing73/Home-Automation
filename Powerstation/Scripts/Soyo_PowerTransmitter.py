#!/usr/bin/env python3
import signal
import sys
import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
import serial
import logging

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

LED = 16
MAX_POWER = 500
INSTANCE = "PowerStation"
BROKER = "192.168.178.230"
USER = "iobroker"
PASSWD = "1evweiden1985"

PORT = "/dev/ttyUSB0"
BAUDRATE = 4800

soyo_power_data = [b'\x24', b'\x56', b'\x00', b'\x21', b'\x00', b'\x00', b'\x80'                                                                             , b'\x08']

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
    soyo_power_data[7] = calc_checksumme(soyo_power_data[1], soyo_power_data[2],                                                                              soyo_power_data[3], soyo_power_data[4], soyo_power_data[5], soyo_power_data[6])

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

    if not hasattr(on_message, "CarChargeing"):
      on_message.CarCharging = 0
    if not hasattr(on_message, "MaxPower"):
      on_message.MaxPower = 0
    if not hasattr(on_message, "LastPower"):
      on_message.LastPower = MAX_POWER

    logging.info(">> message received=%s", message.payload.decode("utf-8"))
    logging.info(">> message topic=%s",message.topic)
    logging.info(">> message qos=%s",message.qos)
    logging.info(">> message retain flag=%s",message.retain)

    if message.payload.decode("utf-8") != "":
      value = int(float(message.payload.decode("utf-8")))
    else:
      value = 0

    if "CHARGING_STATE" in message.topic:
      on_message.CarCharging = value

    if "MaxPower" in message.topic:
      on_message.MaxPower = value
      logging.info("MaxPower set to %s Watt", value)

    if "SetPower" in message.topic:
      if value > on_message.MaxPower:
        SetPower = on_message.MaxPower
      else:
        SetPower =  on_message.LastPower + value

        if SetPower > on_message.MaxPower:
          SetPower = on_message.MaxPower
        if SetPower < 0:
          SetPower = 0

        logging.info(">>>> last: %s", on_message.LastPower)
        logging.info(">>>> act: %s", value)
        logging.info(">>>> set: %s", SetPower)

      if on_message.CarCharging != 0:
        logging.info("The car is charging...");
        SetPower = 0

      on_message.LastPower = SetPower

      if True:
        if SetPower > 0:
          logging.info(">>>>>> Soyo limiter set to %s Watt", SetPower)
        else:
          SetPower = 0
          logging.info(">>>>>> Soyo limiter set to 0")

        setSoyoPowerData(SetPower)

        client.publish("PowerStation/SoyoSource/ActPower", SetPower)

        GPIO.output(LED, GPIO.HIGH)
########################################

signal.signal(signal.SIGINT, signal_handler)

logging.debug("creating new instance")
client = mqtt.Client(INSTANCE) #create new instance
client.on_message=on_message #attach function to callback

logging.debug("connecting to broker")
client.username_pw_set(USER, PASSWD)
client.connect(BROKER) #connect to broker

logging.debug("open serial port")
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

logging.debug("Subscribing to topic","PowerStation/SoyoSource/SetPower")
client.subscribe("PowerStation/SoyoSource/SetPower")

logging.debug("Subscribing to topic","PowerStation/SoyoSource/ActPower")
client.subscribe("PowerStation/SoyoSource/ActPower")

logging.debug("Subscribing to topic","PowerStation/SoyoSource/MaxPower")
client.subscribe("PowerStation/SoyoSource/MaxPower")
client.publish("PowerStation/SoyoSource/MaxPower", MAX_POWER)

client.subscribe("modbus/2/inputRegisters/1/30063_CHARGING_STATE_IREG")

setSoyoPowerData(0)

while True:

  client.publish("PowerStation/SoyoSource/TimeStamp", int(time.time()));

  if ser.isOpen():
    ser.write(soyo_power_data)

  time.sleep(1) # wait 1 sec
