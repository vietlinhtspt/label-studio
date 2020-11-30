import multiprocessing
import time
from pynput import keyboard

import sys
import paho.mqtt.client as mqtt
import time
import json

from pathlib import Path
from utils import process_json_message, convert_timestamp, write_message_to_txt

manager = multiprocessing.Manager()

HOST_URL = "broker.emqx.io"
HOST_PORT = 1883
KEEP_ALIVE = 60
TOPIC = "linhnv/gyro"
SAVED_LOG_PATH = f"./data/logs/{convert_timestamp(time.time())}.txt"
TIME_CHANGE = time.time()


list_log_start = manager.list()
list_log_end = manager.list()
is_recording = manager.Value('i', False)

def on_press(key):
    # print(f'{key} pressed')
    if key == keyboard.Key.space:
        if is_recording.value:
            list_log_end.append(time.time())
        else:
            list_log_start.append(time.time())
        is_recording.value = not is_recording.value

def on_release(key):
    # print(f'{key} release')
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def get_keyboard_event():
    # Collect events until released
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()   

def on_connect(mqttc, obj, flags, rc):
    print("rc: "+str(rc))

def on_message(mqttc, obj, msg):
    # print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    message_string = str(msg.payload)[1:]
    message_object = process_json_message(message_string=message_string)
    
    if is_recording.value:
        print(f"{convert_timestamp(int(time.time()))}[INFO] Is labeling", end="\r")
    else:
        print(f"{convert_timestamp(int(time.time()))}[INFO] NOT labeled", end="\r")

    # Check time message created, if it in period then save.
    # print("Start: ", list_log_start)
    # print("End: ", list_log_end)
    # print(min(len(list_log_start), len(list_log_end)))
    for period in range(0,min(len(list_log_start), len(list_log_end))):
        if message_object['time'] > list_log_start[period] and message_object['time'] < list_log_end[period]:
            # Opening TXT file 
            # print("[INFO] Recording delay message")
            write_message_to_txt(SAVED_LOG_PATH, message_string)

    if len(list_log_start) != len(list_log_end) and message_object['time'] > list_log_start[-1]:
        # print("[INFO] Recording message")
        write_message_to_txt(SAVED_LOG_PATH, message_string)

    

def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)  
        
def get_mqtt_message(save_log):

    mqttc = mqtt.Client()   
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    print(mqttc.connect(HOST_URL,HOST_PORT,KEEP_ALIVE))
    print(mqttc.subscribe(TOPIC, 0))
    mqttc.loop_forever()
    mqttc.disconnect()
    

def collect_data(save_path):

    # Create dir
    save_dir = Path(save_path)
    save_dir.mkdir(parents=True, exist_ok=True)

    save_log = save_dir / "logs"

    # Create, start, join 2 process
    process_get_headpose = multiprocessing.Process(target=get_mqtt_message, args=[save_log])
    process_handle_key_event = multiprocessing.Process(target=get_keyboard_event, args=[])

    process_handle_key_event.start()
    process_get_headpose.start()

    process_get_headpose.join()
    process_handle_key_event.join()

if __name__ == "__main__":
    save_path = "./data"
    collect_data(save_path)