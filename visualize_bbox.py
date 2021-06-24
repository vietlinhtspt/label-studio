import math
import os
import json
from glob import glob
import sys
from pathlib import Path
import tqdm
import cv2
from math import cos, sin
import numpy as np
from PIL import Image

from preprocess_data import draw_axis

seed = 2020
np.random.seed(seed)

def visulize(path_data, path_txt_file):
   
    new_paths = []
    
    txt_file = open(path_txt_file, "r")
    # print(os.path.dirname(path_txt_file))
    dir_name = os.path.basename(str(os.path.dirname(path_txt_file)))
    txt_lines = txt_file.readlines()
    for txt_line in txt_lines[:]:
        
        new_paths.append(os.path.join(dir_name, txt_line))

    print(len(new_paths[:]))

    for i, line_txt in tqdm.tqdm(enumerate(new_paths[:])):
        print(f"{i+1}_{line_txt}")
        img_path = path_data + "/" + line_txt.split(",")[0]
        # print(img_path)
        img = np.array(cv2.imread(img_path)).astype(np.uint8)
        img = img[:,:,::-1]
        # padded_img = np.zeros((1080, 1917, 3))
        # padded_img[:img.shape[0],:img.shape[1]] = img

        
        # if img.shape[0] < 64 or img.shape[1] < 64:
        #     img_error += 1


        # print(img)
        angles = line_txt.split(",")
        # print(angles)
        yaw = float(angles[-3])
        yaw = yaw - 90
        if yaw >= 180: yaw = yaw - 360
        pitch = float(angles[-2])
        roll = float(angles[-1])
        # print(yaw, roll, pitch)
        Image.fromarray(draw_axis(np.copy(img), yaw, pitch, roll)).save("visualized_imgs/"f'Uet_val_img_{i}.jpg')

if "__main__":
    path_data = "/media/2tb/projects/VL's/UetHeadpose/pre_processed"
    path_data_label = "/media/2tb/projects/VL's/UetHeadpose/pre_processed/09/09_annotation_crop_imgs.txt"
    visulize(path_data, path_data_label)    