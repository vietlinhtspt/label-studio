import os
import time

def get_img_from_url(url, saving_path="picture.jpg"):
    start_time = time.time()
    print(time.ctime(int(start_time)))

    run_bash(f"wget -O \"{saving_path}\" {url}")

    end_time = time.time()
    print(end_time-start_time)


def run_bash(bash_command):
    os.system(bash_command)

if __name__ == "__main__":
    get_img_from_url("http://admin:abcd1234@192.168.10.75:80/ISAPI/Streaming/channels/1/picture")