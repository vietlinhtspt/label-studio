import paho.mqtt.client as mqtt 
import time
import json
import cv2

HOST_URL = "broker.emqx.io"
HOST_PORT = 1883
KEEP_ALIVE = 60 
TOPIC = "linhnv/thread01/gyro"
TOPIC2 = "linhnv/thread02/gyro"
SAVED_LOGS_PATH = ""

IS_RECORD = False

"""
KEEP_ALIVE : Maximum period in seconds between communications with the
        broker. If no other messages are being exchanged, this controls the
        rate at which the client will send ping messages to the broker.
"""


def on_connect(mqttc, obj, flags, rc):
    print("rc: "+str(rc))

def on_message(mqttc, obj, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

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

mqttc2 = mqtt.Client()   
mqttc2.on_message = on_message
mqttc2.on_connect = on_connect
mqttc2.on_publish = on_publish
mqttc2.on_subscribe = on_subscribe
print(mqttc2.connect(HOST_URL,HOST_PORT,KEEP_ALIVE))
print(mqttc2.subscribe(TOPIC, 0))

count = 0
start = time.time()
while True:
    data_set = {"time": time.time(), "x":1, "y":2, "z":3}
    message = json.dumps(data_set)
    mqttc.publish(TOPIC,message)
    mqttc2.publish(TOPIC2,message)
    if time.time() - start >= 10:
        break
    count += 1
    # if cv2.waitKey(33) == ord('a') or count == 1000:
    #     break
    # time.sleep(0.001) # wait
    
mqttc.loop_stop() #stop the loop
mqttc2.loop_stop() #stop the loop