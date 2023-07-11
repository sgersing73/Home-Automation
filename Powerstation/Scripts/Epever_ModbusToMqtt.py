#!/usr/bin/env python3
import minimalmodbus
import config

import signal
import sys
import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
import serial

def signal_handler(sig, frame):
    client.loop_stop() #stop the loop
    print(time.strftime("%y%m%d%H%M%S") + "by, by...")
    sys.exit(0)

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

DELAY = 10

def on_disconnect(client, userdata, rc):
    print("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        print("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            print("Reconnected successfully!")

            #client.subscribe("PowerStation/Epever/1/BatVoltage")
            #client.subscribe("PowerStation/Epever/1/TimeStamp")

            client.loop_start() #start the loop
            return
        except Exception as err:
            print("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    print("Reconnect failed after %s attempts. Exiting...", reconnect_count)


def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, message):
    print(time.strftime("%y%m%d%H%M%S") + " >> message received=", message.payload.decode("utf-8"))
    print(time.strftime("%y%m%d%H%M%S") + " >> message topic=",message.topic)

signal.signal(signal.SIGINT, signal_handler)

print(time.strftime("%y%m%d%H%M%S") + " creating new instance")
client = mqtt.Client("EpeverModbusToMqtt") #create new instance
client.on_message=on_message #attach function to callback

print(time.strftime("%y%m%d%H%M%S") + " connecting to broker")
client.username_pw_set(config.USER, config.PASSWD)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.connect(config.BROKER) #connect to broker

print("start loop")
client.loop_start()

# Set to true to edit values
WRITE = False

instrument = minimalmodbus.Instrument("/dev/ttyUSB0", 2)
# port name, slave address (in decimal)

instrument.serial.baudrate = 115200  # Baud
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.2  # seconds

instrument.mode = minimalmodbus.MODE_RTU  # rtu or ascii mode
instrument.clear_buffers_before_each_transaction = True
instrument.close_port_after_each_call = True

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
GEN_ENERGY_TODAY = 0x330C
GEN_ENERGY_TOTAL = 0x3312

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

print(time.strftime("%y%m%d%H%M%S") + " starting main loop...")

counter = 1

while True:

    if counter > 3:
      counter = 1

    instrument = minimalmodbus.Instrument("/dev/ttyUSB0", counter)

    time.sleep(DELAY)
    try:
        value = instrument.read_register(GEN_ENERGY_TODAY, 0, 4, False) / 100
        print(time.strftime("%y%m%d%H%M%S") + " Slave: " + str(counter) + " GEN_ENERGY_TODAY:\t" + str(value) + "KWh")
        client.publish("PowerStation/Epever/" + str(counter) + "/GenEnergyToday", str(value))
    except minimalmodbus.NoResponseError:
        continue

    time.sleep(DELAY)
    try:
        value = instrument.read_register(GEN_ENERGY_TOTAL, 0, 4, False) / 100
        print(time.strftime("%y%m%d%H%M%S") + " Slave: " + str(counter) + " GEN_ENERGY_TOTAL:\t" + str(value) + "KWh")
        client.publish("PowerStation/Epever/" + str(counter) + "/GenEnergyTotal", str(value))
    except minimalmodbus.NoResponseError:
        continue

    time.sleep(DELAY)
    try:
        bat_voltage = instrument.read_register(BAT_VOLTAGE, 2, 4, False)  # Registernumber, number of decimals
        print(time.strftime("%y%m%d%H%M%S") + " Slave: " + str(counter) + " Batt. voltage:\t" + str(bat_voltage) + "V")
        client.publish("PowerStation/Epever/" + str(counter) + "/BatVoltage", bat_voltage)
    except minimalmodbus.NoResponseError:
        continue

    time.sleep(DELAY)
    try:
        bat_soc = instrument.read_register(BAT_SOC, 0, 4, False)
        print(time.strftime("%y%m%d%H%M%S") + " Slave: " + str(counter) + " Batt. SOC:\t" + str(bat_soc) + "%")
        client.publish("PowerStation/Epever/" + str(counter) + "/BatSOC", str(bat_soc))
    except minimalmodbus.NoResponseError:
        continue


    time.sleep(DELAY)
    try:
        value = instrument.read_register(PV_CURRENT, 2, 4, False)
        print(time.strftime("%y%m%d%H%M%S") + " Slave: " + str(counter) + " PV Current:\t" + str(value) + "A")
        client.publish("PowerStation/Epever/" + str(counter) + "/PVCurrent", str(value))
    except minimalmodbus.NoResponseError:
        continue

    time.sleep(DELAY)
    try:
        value = instrument.read_register(PV_VOLTAGE, 2, 4, False)
        print(time.strftime("%y%m%d%H%M%S") + " Slave: " + str(counter) + " PV Voltage:\t" + str(value) + "V")
        client.publish("PowerStation/Epever/" + str(counter) + "/PVVoltage", str(value))
    except minimalmodbus.NoResponseError:
        continue


    time.sleep(DELAY)
    try:
        value = instrument.read_register(EQUIPMENT_TEMP, 2, 4, False)
        print(time.strftime("%y%m%d%H%M%S") + " Slave: " + str(counter) + " Temp:\t" + str(value) + "C")
        client.publish("PowerStation/Epever/" + str(counter) + "/EquipmentTemp", str(value))
    except minimalmodbus.NoResponseError:
        continue

    client.publish("PowerStation/Epever/" + str(counter) + "/TimeStamp", int(time.time()))

    counter = counter + 1
