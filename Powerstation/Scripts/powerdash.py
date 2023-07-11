#!/usr/bin/env python3

import signal
import sys
import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
import drivers
from encoder import Encoder

Power = 0
ActPower = 0
MaxPower = 0
Produced = 0
BatSOC = 0
BatVoltage = 0
PVVoltage1 = 0
PVVoltage2 = 0
PVVoltage3 = 0
PVCurrent1 = 0
PVCurrent2 = 0
PVCurrent3 = 0
A_input = 0
Day = 0
Week = 0
Month = 0
Year = 0

bar_repr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def valueChanged(value, direction):
    #print("* New value: {}, Direction: {}".format(value, direction))
    if direction == 'L':
      print(client.publish("PowerStation/SoyoSource/MaxPower", MaxPower - 10))
      print(MaxPower - 10)
    if direction == 'R':
      print(client.publish("PowerStation/SoyoSource/MaxPower", MaxPower + 10))
      print(MaxPower + 10)

def signal_handler(sig, frame):
    client.loop_stop() #stop the loop
    display1.lcd_clear()
    display2.lcd_clear()
    display3.lcd_clear()
    display4.lcd_clear()
#    print('by, by...')
    sys.exit(0)

def on_message(client, userdata, message):

    print(">> message received=", message.payload.decode("utf-8"))
#    print(">> message topic=",message.topic)
    global Power
    global ActPower
    global MaxPower
    global Produced
    global BatSOC
    global BatVoltage
    global PVVoltage1
    global PVVoltage2
    global PVVoltage3
    global PVCurrent1
    global PVCurrent2
    global PVCurrent3
    global A_input
    global Day
    global Week
    global Month
    global Year

    if (message.payload.decode("utf-8") != ""):
      value = float(message.payload.decode("utf-8"))
    else:
      value = 0

    if "SetPower" in message.topic:
      Power = value
    elif "Produced" in message.topic:
      Produced = value
    elif "BatSOC" in message.topic:
      BatSOC = value
    elif "BatVoltage" in message.topic:
      BatVoltage = value
    elif "1/PVVoltage" in message.topic:
      PVVoltage1 = value
    elif "1/PVCurrent" in message.topic:
      PVCurrent1 = value
    elif "2/PVVoltage" in message.topic:
      PVVoltage2 = value
    elif "2/PVCurrent" in message.topic:
      PVCurrent2 = value
    elif "3/PVVoltage" in message.topic:
      PVVoltage3 = value
    elif "3/PVCurrent" in message.topic:
      PVCurrent3 = value
    elif "A_input" in message.topic:
      A_input = value
    elif "ActPower" in message.topic:
      ActPower = value
    elif "MaxPower" in message.topic:
      MaxPower = value
    elif "Day" in message.topic:
      Day = value
    elif "Week" in message.topic:
      Week = value
    elif "Month" in message.topic:
      Month = value
    elif "Year" in message.topic:
      Year = value

def display():

  for i in range(10):
      if BatSOC >= ((i + 1) * 10):
          bar_repr[i] = 1
      else:
          bar_repr[i] = 0

  # Render charge bar:
  bar_string = ""
  for i in range(10):
      if i == 0:
          # Left character
          if bar_repr[i] == 0:
              # Left empty character
              bar_string = bar_string + "{0x01}"
          else:
              # Left full character
              bar_string = bar_string + "{0x00}"
      elif i == 9:
          # Right character
          if bar_repr[i] == 0:
              # Right empty character
              bar_string = bar_string + "{0x05}"
          else:
              # Right full character
              bar_string = bar_string + "{0x04}"
      else:
          # Central character
          if bar_repr[i] == 0:
              # Central empty character
              bar_string = bar_string + "{0x03}"
          else:
              # Central full character
              bar_string = bar_string + "{0x02}"

  # Print the string to display:

  display1.lcd_display_string("C:{0:>5.1f}W T:{1:>2.0f}kWh".format(Power, Produced), 1)
  display1.lcd_display_string("A:{0:>3.0f}W   M:{1:>3.0f}W".format(ActPower, MaxPower), 2)
  display2.lcd_display_string("D:{0:>3.0f} W:{1:>4.0f} kWh".format(Day, Week), 1)
  display2.lcd_display_string("M:{0:>3.0f} Y:{1:>4.0f} kWh".format(Month, Year), 2)
  display3.lcd_display_string("{0:>4.1f} {1:>4.1f} {2:>4.1f} V".format(PVVoltage1, PVVoltage2, PVVoltage3), 1)
  display3.lcd_display_string("{0:>4.1f} {1:>4.1f} {2:>4.1f} A".format(PVCurrent1, PVCurrent2, PVCurrent3), 2)
  display4.lcd_display_string("L:{0:>4.1f}A    {1:>4.1f}V".format(A_input, BatVoltage), 1)
  display4.lcd_display_extended_string(bar_string + " {0}% ".format(BatSOC), 2)

########################################

display1 = drivers.Lcd(0x23)
display2 = drivers.Lcd(0x25)
display3 = drivers.Lcd(0x26)
display4 = drivers.Lcd(0x27)

# Create an object with custom characters data
cc = drivers.CustomCharacters(display4)

# Redefine the default characters that will be used to create the process bar:
# Left full character. Code {0x00}.
cc.char_1_data = ["01111", "11000", "10011", "10111", "10111", "10011", "11000", "01111"]

# Left empty character. Code {0x01}.
cc.char_2_data = ["01111", "11000", "10000", "10000", "10000", "10000", "11000", "01111"]

# Central full character. Code {0x02}.
cc.char_3_data = ["11111", "00000", "11011", "11011", "11011", "11011", "00000", "11111"]

# Central empty character. Code {0x03}.
cc.char_4_data = ["11111", "00000", "00000", "00000", "00000", "00000", "00000", "11111"]

# Right full character. Code {0x04}.
cc.char_5_data = ["11110", "00011", "11001", "11101", "11101", "11001", "00011", "11110"]

# Right empty character. Code {0x05}.
cc.char_6_data = ["11110", "00011", "00001", "00001", "00001", "00001", "00011", "11110"]

# Load custom characters data to CG RAM:
cc.load_custom_characters_data()


signal.signal(signal.SIGINT, signal_handler)
#print("creating new instance")
client = mqtt.Client("PowerDash") #create new instance
client.on_message=on_message #attach function to callback

#print("connecting to broker")
client.username_pw_set("iobroker", "xxxx")
client.connect("192.168.178.230") #connect to broker

client.subscribe("PowerStation/Feed/Day")
client.subscribe("PowerStation/Feed/Week")
client.subscribe("PowerStation/Feed/Month")
client.subscribe("PowerStation/Feed/Year")
client.subscribe("PowerStation/SoyoSource/SetPower")
client.subscribe("PowerStation/SoyoSource/MaxPower")
client.subscribe("PowerStation/SoyoSource/ActPower")
client.subscribe("PowerStation/SoyoSource/Produced")
client.subscribe("PowerStation/Epever/1/BatSOC")
client.subscribe("PowerStation/Epever/1/BatVoltage")
client.subscribe("PowerStation/Epever/1/PVVoltage")
client.subscribe("PowerStation/Epever/1/PVCurrent")
client.subscribe("PowerStation/Epever/2/PVVoltage")
client.subscribe("PowerStation/Epever/2/PVCurrent")
client.subscribe("PowerStation/Epever/3/PVCurrent")
client.subscribe("PowerStation/Epever/3/PVVoltage")
client.subscribe("PowerStation/Epever/3/PVCurrent")
client.subscribe("PowerStation/Soyo/A_input")

client.loop_start() #start the loop

GPIO.setmode(GPIO.BCM)
e1 = Encoder(21, 20, valueChanged)

while True:

  display()

  time.sleep(1) # wait 1 sec
