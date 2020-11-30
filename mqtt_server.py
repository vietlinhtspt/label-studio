import sys
import paho.mqtt.client as mqtt
import json
import time 

HOST_URL = "broker.emqx.io"
HOST_PORT = 1883
KEEP_ALIVE = 60
TOPIC = "linhnv/gyro"
SAVED_LOG_PATH = f"./data/logs/test_{time.time()}.txt"

def on_connect(mqttc, obj, flags, rc):
    print("rc: "+str(rc))

def on_message(mqttc, obj, msg):
    print("on_message: ", msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    # Opening TXT file 
    f = open(SAVED_LOG_PATH, "a")
    f.write(str(msg.payload) + "\n")
    f.close()

def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

mqttc = mqtt.Client()   
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
print(mqttc.connect(HOST_URL,HOST_PORT,KEEP_ALIVE))
print(mqttc.subscribe(TOPIC, 0))
mqttc.loop_forever()
mqttc.disconnect()