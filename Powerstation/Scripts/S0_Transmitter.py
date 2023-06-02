#!/usr/bin/python3
import config
import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt

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


print("creating new instance")
client = mqtt.Client("S0_Transmitter") #create new instance
#client.on_message=on_message #attach function to callback

print("connecting to broker")
client.username_pw_set(config.USER, config.PASSWD)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.connect(config.BROKER) #connect to broker

client.loop_start() #start the loop

# Zaehler-Variable, global
Counter = 0

# Pinreferenz waehlen
GPIO.setmode(GPIO.BCM)

# GPIO 18 (Pin 12) als Input definieren und Pullup-Widerstand aktivieren
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Callback-Funktion
def Interrupt(channel):
  global Counter
  # Counter um eins erhoehen und ausgeben
  Counter = Counter + 1
  print("Counter " + str(Counter))
  client.publish("PowerStation/SoyoSource/S0Trigger", Counter)

# Interrupt-Event hinzufuegen, steigende Flanke
GPIO.add_event_detect(23, GPIO.RISING, callback = Interrupt, bouncetime = 250)

# Endlosschleife, bis Strg-C gedrueckt wird
try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  GPIO.cleanup()
  client.loop_stop() #stop the loop
  print("\nBye")
