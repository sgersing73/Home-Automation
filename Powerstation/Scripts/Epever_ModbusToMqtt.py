#!/usr/bin/env python3
import minimalmodbus
import config

import signal
import sys
import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
import serial
import logging

def signal_handler(sig, frame):

    client.loop_stop() #stop the loop
    print('by, by...')
    sys.exit(0)

def on_message(client, userdata, message):

    logging.info(">> message received=%s", message.payload.decode("utf-8"))
    logging.info(">> message topic=%s",message.topic)

signal.signal(signal.SIGINT, signal_handler)

#logging.debug("creating new instance")
client = mqtt.Client(config.INSTANCE + "1") #create new instance
client.on_message=on_message #attach function to callback

#logging.debug("connecting to broker")
client.username_pw_set(config.USER, config.PASSWD)
client.connect(config.BROKER) #connect to broker

# Set to true to edit values
WRITE = False

# port name, slave address (in decimal)
instrument = minimalmodbus.Instrument("/dev/ttyUSB1", 1)  

instrument.serial.baudrate = 115200  # Baud
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.2  # seconds

instrument.mode = minimalmodbus.MODE_RTU  # rtu or ascii mode
instrument.clear_buffers_before_each_transaction = True

PV_VOLTAGE = 0x3100
PV_CURRENT = 0x3101
PV_POWERL = 0x3102
PV_POWERH = 0x3103
BAT_VOLTAGE = 0x331A
BAT_POWERL = 0x3106
BAT_POWERH = 0x3107
LOAD_VOLTAGE = 0x310C
LOAD_CURRENT = 0x310D
LOAD_POWERL = 0x310E
LOAD_POWERH = 0x310E
BAT_TEMP = 0x3110
EQUIPMENT_TEMP = 0x3111
BAT_SOC = 0x311A
BAT_RATED_VOLTAGE = 0x9067
BAT_STATE = 0x3200
CHARGE_STATE = 0x3201

# Holding registers
BAT_TYPE = 0x9000
BAT_CAPACITY = 0x9001
HIGH_VOLTAGE_DISCONNECT = 0x9003
CHARGING_LIMIT_VOLTAGE = 0x9004
OVER_VOLTAGE_RECONNECT = 0x9005
EQUALIZATION_VOLTAGE = 0x9006
BOOST_VOLTAGE = 0x9007
FLOAT_VOLTAGE = 0x9008
BOOST_RECONNECT_VOLTAGE = 0x9009
LOW_VOLTAGE_RECONNECT = 0x900A
UNDER_VOLTAGE_RECOVER = 0x900B
UNDER_VOLTAGE_WARNING = 0x900C
LOW_VOLTAGE_DISCONNECT = 0x900D
DISCHARGING_LIMIT_VOLTAGE = 0x900E

client.subscribe("PowerStation/Epever/1/BatVoltage")
client.subscribe("PowerStation/Epever/1/TimeStamp")

while True:

  high_voltage_disconnect = instrument.read_register(HIGH_VOLTAGE_DISCONNECT, 2)
  charging_limit_voltage = instrument.read_register(CHARGING_LIMIT_VOLTAGE, 2)
  over_voltage_reconnect = instrument.read_register(OVER_VOLTAGE_RECONNECT, 2)
  equalization_voltage = instrument.read_register(EQUALIZATION_VOLTAGE, 2)
  boost_voltage = instrument.read_register(BOOST_VOLTAGE, 2)
  float_voltage = instrument.read_register(FLOAT_VOLTAGE, 2)
  boost_reconnect_voltage = instrument.read_register(BOOST_RECONNECT_VOLTAGE, 2)
  low_voltage_reconnect = instrument.read_register(LOW_VOLTAGE_RECONNECT, 2)
  under_voltage_recover = instrument.read_register(UNDER_VOLTAGE_RECOVER, 2)
  under_voltage_warning = instrument.read_register(UNDER_VOLTAGE_WARNING, 2)
  low_voltage_disconnect = instrument.read_register(LOW_VOLTAGE_DISCONNECT, 2)
  discharging_limit_voltage = instrument.read_register(DISCHARGING_LIMIT_VOLTAGE, 2)

  print("high_voltage_disconnect:", high_voltage_disconnect, "V")
  print("charging_limit_voltage:", charging_limit_voltage, "V")
  print("over_voltage_reconnect:", over_voltage_reconnect, "V")
  print("equalization_voltage:", equalization_voltage, "V")
  print("boost_voltage:", boost_voltage, "V")
  print("float_voltage:", float_voltage, "V")
  print("boost_reconnect_voltage:", boost_reconnect_voltage, "V")
  print("low_voltage_reconnect:", low_voltage_reconnect, "V")
  print("under_voltage_recover:", under_voltage_recover, "V")
  print("under_voltage_warning:", under_voltage_warning, "V")
  print("low_voltage_disconnect:", low_voltage_disconnect, "V")
  print("discharging_limit_voltage:", discharging_limit_voltage, "V")

  # Print panel info
  pv_voltage = instrument.read_register(
      PV_VOLTAGE, 2, 4, False
  )  # Registernumber, number of decimals
  print("Panel voltage:\t" + str(pv_voltage) + "V")
  pv_current = instrument.read_register(
      PV_CURRENT, 2, 4, False
  )  # Registernumber, number of decimals
  print("Panel current:\t" + str(pv_current) + "A")

  # Print battery info
  bat_voltage = instrument.read_register(
      BAT_VOLTAGE, 2, 4, False
  )  # Registernumber, number of decimals
  print("Batt. voltage:\t" + str(bat_voltage) + "V")
  client.publish("PowerStation/Epever/" + "1" + "/BatVoltage", bat_voltage)

  bat_soc = instrument.read_register(
      BAT_SOC, 0, 4, False
  )
  print("Batt. SOC:\t" + str(bat_soc) + "%")
  client.publish("PowerStation/Epever/" + "1" + "/BatSOC", str(bat_soc))

  temperature = instrument.read_register(
      BAT_TEMP, 2, 4, False
  )  # Registernumber, number of decimals
  print("Batt. temp:\t" + str(temperature) + "C")

  if WRITE:
    # Set battery type, 1 = Sealed
    sealed = 1
    instrument.write_register(BAT_TYPE, sealed, 0, functioncode=0x10, signed=False)
    battery_type = instrument.read_register(BAT_TYPE, 0, 3, False)  # Registernumber, number of decimals

    type_string = ""
    if battery_type == 1:
      type_string = "Sealed"
    elif battery_type == 2:
      type_string = "Gel"
    elif battery_type == 3:
      type_string = "Flooded"
    elif battery_type == 0:
      type_string = "User defined"
    print("Battery type:\t" + type_string)

  if WRITE:
    # Set capacity
    capacity = 75
    instrument.write_register(BAT_CAPACITY, capacity, 0, functioncode=0x10, signed=False)

  battery_capacity = instrument.read_register(BAT_CAPACITY, 0, 3, False)  # Registernumber, number of decimals
  print("Battery capac.:\t" + str(battery_capacity) + "Ah")

  if WRITE:
    # Set battery voltage, 0 = auto detect, 1 = 12 V, 2 = 24V
    v_auto = 0
    v_12 = 1
    v_24 = 2
    instrument.write_register(BAT_RATED_VOLTAGE, v_12, 0, functioncode=0x10, signed=False)

  battery_rated_volt = instrument.read_register(BAT_RATED_VOLTAGE, 0, 3, False)  # Registernumber, number of decimals
  volt_string = ""
  if battery_rated_volt == 0:
    volt_string = "autodetect"
  else:
    volt_string = str(12 * battery_rated_volt) + "V"

  print("System voltage:\t" + volt_string)

  val = instrument.read_register(0x900E, 2, 3, False)
  print("Voltage configuration:\t" + str(val) + "V")

  client.publish("PowerStation/Epever/1/TimeStamp", int(time.time()));

  time.sleep(10)
