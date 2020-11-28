import multiprocessing
import time
manager = multiprocessing.Manager()

# Example:
#------------------------------------------------------------------------
# manager = multiprocessing.Manager()
# final_list = manager.list()
# input_list_one = ['one', 'two', 'three', 'four', 'five']
# input_list_two = ['six', 'seven', 'eight', 'nine', 'ten']

# def worker(data):
#     for item in data:
#         final_list.append(item)

# process1 = multiprocessing.Process(target=worker, args=[input_list_one])
# process2 = multiprocessing.Process(target=worker, args=[input_list_two])

# process1.start()
# process2.start()
# process1.join()
# process2.join()
# print(final_list)
#------------------------------------------------------------------------
from pynput import mouse, keyboard
import sys
import paho.mqtt.client as mqtt

HOST_URL = "broker.emqx.io"
HOST_PORT = 1883
KEEP_ALIVE = 60
TOPIC = "linhnv/gyro"

is_recording = manager.Value('i', False)

def on_press(key):
    print(f'{key} pressed')
    if key == keyboard.Key.space:
        is_recording.value = not is_recording.value


def on_release(key):
    print(f'{key} release')
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
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    print(f"[INFO] Is recording: {is_recording.value}")

def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)  
        
def get_mqtt_message():
    mqttc = mqtt.Client()   
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    print(mqttc.connect(HOST_URL,HOST_PORT,KEEP_ALIVE))
    print(mqttc.subscribe(TOPIC, 0))
    mqttc.loop_forever()
    mqttc.disconnect()
    

def collect_data():

    process_get_headpose = multiprocessing.Process(target=get_mqtt_message, args=[])
    process_handle_key_event = multiprocessing.Process(target=get_keyboard_event, args=[])

   
    process_handle_key_event.start()
    process_get_headpose.start()

    process_get_headpose.join()
    process_handle_key_event.join()

if __name__ == "__main__":
    collect_data()