#!/usr/bin/python


#  License  
##################################################################################################
#                                                #
#                   "Python PiUSV Controller" by Philipp Seidel is licensed under a              #
#      Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.      #
#   To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/  #
#                               http://www.forum-raspberrypi.de/         #
#                                                #
##################################################################################################

##################################################################################################
#                                                #
#                   "Python PiUSV Controller" V2 by Armin Pipp is based on the code from     #
#                              Phillip Seidel and is licensed under a                            #
#      Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.      #
#   To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/  #
#                                                #
##################################################################################################

import smbus
import time
import os
import sys

#  Configuration
##############################################################################################################
bus_id    = 1;    # 1=Rev2  0=Rev1
address   = 0x18  # i2c adress of PiUSV ; find out with "sudo i2cdetect -y 1" or "sudo i2cdetect -y 0"
off_timer = 20     # time in seconds to power off the raspberry pi
# Pipp V2
on_battery_time = 60 # seconds running on battery before shutdown starts
##############################################################################################################

# Workaround becaus of this:
# http://stackoverflow.com/questions/22077293/write-i2c-block-data-how-to-convert-decimal-to-i2c-bytes
# 5 10 15 20 25 30 35 40 50 60
off_timer_hex = 0x1e
    
if off_timer == 5:
    off_timer_hex = 0x05
elif off_timer== 10:
    off_timer_hex = 0x0a
elif off_timer== 15:
    off_timer_hex = 0x0f
elif off_timer== 20:
    off_timer_hex = 0x14
elif off_timer== 25:
    off_timer_hex = 0x19
elif off_timer== 30:
    off_timer_hex = 0x1e
elif off_timer== 35:
    off_timer_hex = 0x23
elif off_timer== 40:
    off_timer_hex = 0x28
elif off_timer== 50:
    off_timer_hex = 0x32
elif off_timer== 60:
    off_timer_hex = 0x3c

#
#  Configuration for experts
##############################################################################################################
delay     = 0.1   # delay time between loops ans "reads" -> time.sleep(delay)
##############################################################################################################

bus = smbus.SMBus(bus_id)
time.sleep(delay) 

# maximum 'off_timer' message
if off_timer > 256 :
    print ("Error: the off_timer' must not exceed 256 seconds! The script was stopped!")
    sys.exit();

#off_timer_hex = format(off_timer, '#04x'); #convert decimal to i2c hex

# bus.write_word_data(address, 0x00, 0);
# status = bus.read_byte(address);
# print status;
    
# sys.exit();       
    
Current_State  = 0
Previous_State = 0 
i = 1
n = 10
status = bus.read_byte(address);
time.sleep(delay)

while True :

    status = ""
    status = bus.read_byte(address);

    Current_State = status
    #1 = green  (everything is fine)
    #5 = orange (battery removed)
    #2 = red    (power lost or powercable disconnected)
        
    #print Current_State
    
    if Current_State==1 and Previous_State!=1:
      print ("green")
      Previous_State=1
    elif Current_State==5 and Previous_State!=5:
      print ("orange")
      Previous_State=5
    elif Current_State==2 and Previous_State!=2:
      print ("red")
      print ("on-battery="+str(on_battery_time))
      Previous_State=2
      i = 1
      while i <= on_battery_time:
        # wait on_battery and check ever second for state change
        time.sleep(1)
        status = bus.read_byte(address)
        time.sleep(delay)
        Current_State = status
        #print i
        if Current_State!=Previous_State: i=on_battery_time
        i = i+1
    elif Current_State==2 and Previous_State==2:
      # power off Raspberry Pi
      # os.system("sudo shutdown -h now") 
      # send poweroff to PiUSV
      # send 10 times - add from Pipp
      i = 1
      print ("SHUTDOWN start")
      while i <= n :
        bus.write_byte_data(address, 0x00, 0x10) 
        time.sleep(delay)
        # power off Raspberry pi after x seconds
        #bus.write_byte_data(address, 0x00, off_timer_hex) 
        #time.sleep(delay)
        i = i+1
      Previous_State=2
      os.system("sudo shutdown -h now")  

    time.sleep(delay)




