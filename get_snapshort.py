from PIL import Image
import time
import os
from utils import get_img_from_url

def get_snapshot_from_ipcam(url, saving_dir="", time=time.time(), x=0, y=0, z=0):
    file_name = f"{time}_{x}_{y}_{z}.jpeg"
    saving_path = os.path.join(saving_dir, file_name)
    get_img_from_url(url, saving_path)

if __name__ == "__main__":
    while True:
        get_snapshot_from_ipcam("http://admin:abcd1234@192.168.10.75:80/ISAPI/Streaming/channels/1/picture", saving_dir="imgs", time=time.time())
        time.sleep(0.5)
        break
