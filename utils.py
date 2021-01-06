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
    # print(f"Gettting json message: {message_string}")
    # '1608820149,-890,32,-7'
    # print(str(message_string).split("'"))

    list_strings = str(message_string).split("'")[0]
    if len(list_strings) == 0:
        list_strings = str(message_string).split("'")[1]
    # 1608820149,-890,32,-7
    list_strings = str(list_strings).split(",")
    if checkIsNumberics(list_strings):
        # print(list_strings)
        # print(int(list_strings[0]))
        # print(float(list_strings[1]))
        # print(float(list_strings[2]))
        # print(float(list_strings[3]))
        message_object = {"time": int(list_strings[0]), "yaw": float(list_strings[1]), "pitch": float(list_strings[2]), "roll": float(list_strings[3]), "error": False}
        
        # print(f"Message objects ", message_object)
        return message_object
    else:
        return {"error": True, "message": message_string}

def checkIsNumberics(lists):
    isNumberic = True
    # print(f"List number: {lists}")
    for element in lists:
        if not is_number(element):
            isNumberic = False
            print("\nNot number: ", element)
            print("\n")
            break
    # print(lists)
    # print(isNumberic)
    return isNumberic

def is_number(n):
    is_number = True
    try:
        num = float(n)
        # check for "nan" floats
        is_number = num == num   # or use `math.isnan(num)`
    except ValueError:
        is_number = False
    return is_number

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
