#!/usr/bin/python3
import config
import serial
import time
import paho.mqtt.client as mqtt
import time

serial_port = serial.Serial(
    port='/dev/ttyAMA0',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

def chksum(data):
  cs = 0
  for i in range(1,14):
    cs = cs+(data[i])
  return (0xff - cs) & 0xff

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

def on_disconnect(client, userdata, rc):
    print("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        print("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            print("Reconnected successfully!")
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

if __name__ == '__main__':

    try:

        print(time.strftime("%y%m%d%H%M%S") + " creating new instance")
        client = mqtt.Client("SoyoDataToMqtt") #create new instance

        client.on_message=on_message #attach function to callback
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect

        print(time.strftime("%y%m%d%H%M%S") + " connecting to broker")
        client.username_pw_set(config.USER, config.PASSWD)
        client.connect(config.BROKER) #connect to broker

        print("start loop")
        client.loop_start()

        while True :

            time.sleep(1)
            if serial_port.readable():

                serial_port.flushInput()
                serial_port.timeout = None

                data = serial_port.read(15)

                l_data = list(data)

                if l_data[0] == 0xa6:
                  if (chksum(l_data) == l_data[14]):
                  
                    print("Frame: " , str.join("", ("0x%02X " % i for i in l_data)))
                    
                    msgty = l_data[3] & 0x0f;
                    if (msgty == 0x01):
                    
                        reqpower = int((l_data[1]<<8)+l_data[2])
                        opmode   = int(l_data[3])
                        errstat  = int(l_data[4])
                        V_input  = round(0.1 * (float((l_data[5]<<8)+l_data[6])), 2)
                        A_input  = round(0.1 * (float((l_data[7]<<8)+l_data[8])), 2)
                        V_main   =       (float((l_data[9]<<8)+l_data[10]))
                        net_HZ   = 0.5 * (float(l_data[11]))
                        temp     = round(0.1 * (float((l_data[12]<<8)+l_data[13]) - 30.0), 2)

                        print(reqpower, errstat, opmode, V_input, V_main, net_HZ, temp)
                    
                        client.publish("PowerStation/Soyo/ReqPower", reqpower)
                        client.publish("PowerStation/Soyo/ErrStat", errstat)
                        client.publish("PowerStation/Soyo/OpMode", opmode)
                        client.publish("PowerStation/Soyo/V_input", V_input)
                        client.publish("PowerStation/Soyo/A_input", A_input)
                        client.publish("PowerStation/Soyo/V_main", V_main)
                        client.publish("PowerStation/Soyo/net_HZ", net_HZ)
                        client.publish("PowerStation/Soyo/Temp", temp)
                        client.publish("PowerStation/Soyo/TimeStamp", int(time.time()))
                        
    except KeyboardInterrupt:
      serial_port.close()
      client.loop_stop() #stop the loop
      print("\nBye")
