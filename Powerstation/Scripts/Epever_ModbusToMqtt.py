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

def f():
    excs = [OSError('error 1'), SystemError('error 2')]
    raise ExceptionGroup('there were problems', excs)

signal.signal(signal.SIGINT, signal_handler)

logging.debug("creating new instance")
client = mqtt.Client(config.INSTANCE + "1") #create new instance
client.on_message=on_message #attach function to callback

logging.debug("connecting to broker")
client.username_pw_set(config.USER, config.PASSWD)
client.connect(config.BROKER) #connect to broker

# Set to true to edit values
WRITE = False

instrument = minimalmodbus.Instrument("/dev/ttyUSB1", 1)
# port name, slave address (in decimal)

instrument.serial.baudrate = 115200  # Baud
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1  # seconds

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

    time.sleep(1) 
    try:
        high_voltage_disconnect = instrument.read_register(HIGH_VOLTAGE_DISCONNECT, 2)
        print("high_voltage_disconnect:", high_voltage_disconnect, "V")
    except minimalmodbus.NoResponseError:
        continue        
    
    time.sleep(1) 
    try:
        charging_limit_voltage = instrument.read_register(CHARGING_LIMIT_VOLTAGE, 2)
        print("charging_limit_voltage:", charging_limit_voltage, "V")
    except minimalmodbus.NoResponseError:
        continue     
    
    time.sleep(1) 
    try:    
        over_voltage_reconnect = instrument.read_register(OVER_VOLTAGE_RECONNECT, 2)
        print("over_voltage_reconnect:", over_voltage_reconnect, "V")
    except minimalmodbus.NoResponseError:
        continue     
    
    time.sleep(1) 
    try:
        equalization_voltage = instrument.read_register(EQUALIZATION_VOLTAGE, 2)
        print("equalization_voltage:", equalization_voltage, "V")
    except minimalmodbus.NoResponseError:
        continue     
    
    time.sleep(1) 
    try:
        boost_voltage = instrument.read_register(BOOST_VOLTAGE, 2)
        print("boost_voltage:", boost_voltage, "V")
    except minimalmodbus.NoResponseError:
        continue     
            
    time.sleep(1) 
    try:
        float_voltage = instrument.read_register(FLOAT_VOLTAGE, 2)
        print("float_voltage:", float_voltage, "V")
    except minimalmodbus.NoResponseError:
        continue     
    
    time.sleep(1) 
    try:    
        boost_reconnect_voltage = instrument.read_register(BOOST_RECONNECT_VOLTAGE, 2)
        print("boost_reconnect_voltage:", boost_reconnect_voltage, "V")
    except minimalmodbus.NoResponseError:
        continue     
    
    time.sleep(1) 
    try:
        low_voltage_reconnect = instrument.read_register(LOW_VOLTAGE_RECONNECT, 2)
        print("low_voltage_reconnect:", low_voltage_reconnect, "V")
    except minimalmodbus.NoResponseError:
        continue     
    
    time.sleep(1) 
    try:
        under_voltage_recover = instrument.read_register(UNDER_VOLTAGE_RECOVER, 2)
        print("under_voltage_recover:", under_voltage_recover, "V")
    except minimalmodbus.NoResponseError:
        continue
        
    time.sleep(1) 
    try:
        under_voltage_warning = instrument.read_register(UNDER_VOLTAGE_WARNING, 2)
        print("under_voltage_warning:", under_voltage_warning, "V")
    except minimalmodbus.NoResponseError:
        continue        
    
    time.sleep(1) 
    try:
        low_voltage_disconnect = instrument.read_register(LOW_VOLTAGE_DISCONNECT, 2)
        print("low_voltage_disconnect:", low_voltage_disconnect, "V")
    except minimalmodbus.NoResponseError:
        continue        
    
    time.sleep(1) 
    try:    
        discharging_limit_voltage = instrument.read_register(DISCHARGING_LIMIT_VOLTAGE, 2)
        print("discharging_limit_voltage:", discharging_limit_voltage, "V")
    except minimalmodbus.NoResponseError:
        continue        
    
    # Print panel info
    time.sleep(1) 
    try:
        pv_voltage = instrument.read_register(PV_VOLTAGE, 2, 4, False)  # Registernumber, number of decimals
        print("Panel voltage:\t" + str(pv_voltage) + "V")
    except minimalmodbus.NoResponseError:
        continue        

    time.sleep(1) 
    try:
        pv_current = instrument.read_register(PV_CURRENT, 2, 4, False)  # Registernumber, number of decimals
        print("Panel current:\t" + str(pv_current) + "A")
    except minimalmodbus.NoResponseError:
        continue        

    # Print battery info
    time.sleep(1) 
    try:
        bat_voltage = instrument.read_register(BAT_VOLTAGE, 2, 4, False)  # Registernumber, number of decimals
        print("Batt. voltage:\t" + str(bat_voltage) + "V")
        client.publish("PowerStation/Epever/" + "1" + "/BatVoltage", bat_voltage)
    except minimalmodbus.NoResponseError:
        continue        
 
    time.sleep(1) 
    try:
        bat_soc = instrument.read_register(BAT_SOC, 0, 4, False)
        print("Batt. SOC:\t" + str(bat_soc) + "%")
        client.publish("PowerStation/Epever/" + "1" + "/BatSOC", str(bat_soc))
    except minimalmodbus.NoResponseError:
        continue        

    time.sleep(1) 
    try:
        temperature = instrument.read_register(BAT_TEMP, 2, 4, False)  # Registernumber, number of decimals
        print("Batt. temp:\t" + str(temperature) + "C")
    except minimalmodbus.NoResponseError:
        continue        

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

    time.sleep(1) 
    try:
        battery_capacity = instrument.read_register(BAT_CAPACITY, 0, 3, False)  # Registernumber, number of decimals
        print("Battery capac.:\t" + str(battery_capacity) + "Ah")
    except minimalmodbus.NoResponseError:
        continue        

    if WRITE:
      # Set battery voltage, 0 = auto detect, 1 = 12 V, 2 = 24V
      v_auto = 0
      v_12 = 1
      v_24 = 2
      instrument.write_register(BAT_RATED_VOLTAGE, v_12, 0, functioncode=0x10, signed=False)

    time.sleep(1) 
    try:
        battery_rated_volt = instrument.read_register(BAT_RATED_VOLTAGE, 0, 3, False)  # Registernumber, number of decimals
       
        if battery_rated_volt == 0:
          volt_string = "autodetect"
        else:
          volt_string = str(12 * battery_rated_volt) + "V"
        
        print("System voltage:\t" + volt_string)
    except minimalmodbus.NoResponseError:
        continue        

    time.sleep(1) 
    try:
        val = instrument.read_register(0x900E, 2, 3, False)
        print("Voltage configuration:\t" + str(val) + "V")
    except minimalmodbus.NoResponseError:
        continue        

    client.publish("PowerStation/Epever/1/TimeStamp", int(time.time()))

    time.sleep(10)
