import os
import time
import json
from datetime import datetime 

def get_img_from_url(url, saving_path="picture.jpg"):
    start_time = time.time()
    print(time.ctime(int(start_time)))

    run_bash(f"wget -O \"{saving_path}\" {url}")

    end_time = time.time()
    print(end_time-start_time)


def run_bash(bash_command):
    os.system(bash_command)

def process_json_message(message_string):
    list_strings = str(message_string).split("'")
    
    message_object = json.loads(list_strings[1])
    # print(message_object['time'])
    return message_object

def convert_timestamp(timestamp):
    dt_obj = datetime.fromtimestamp(timestamp) 
    converted_timestamp = str(dt_obj).replace("-", "_").replace(" ", "_").replace(":", "_")
    converted_timestamp = converted_timestamp + "_" + str(timestamp)
    # print(converted_timestamp)
    return converted_timestamp

def write_message_to_txt(path_file, message):
    # print("[INFO] Getting delay message")
    f = open(path_file, "a")
    f.write(message + "\n")
    f.close()

if __name__ == "__main__":
    # get_img_from_url("http://admin:abcd1234@192.168.10.75:80/ISAPI/Streaming/channels/1/picture")
    timestamp = time.time()
    convert_timestamp(timestamp=timestamp)
