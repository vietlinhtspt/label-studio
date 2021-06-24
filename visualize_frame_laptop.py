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

from get_frame import read_log_file

from visualize import read_frames, read_log_file, get_bbox_YOLO_format, draw_annotates, generate_video

def check_pose(pose_cache, yaw_penalty, head_yaw):
    """
    input:
        pose_cache: [] list of 2 last pose
    output:
        new_cache: new cache with current head_yaw
    """
    
    if len(pose_cache) < 2:
        pose_cache.append(head_yaw)
        return pose_cache, yaw_penalty
    else:
        print(pose_cache, head_yaw)
        print(head_yaw - pose_cache[-1])
        if abs(head_yaw - pose_cache[-1]) > 75 and  abs(head_yaw - pose_cache[-1]) < 100:
            yaw_penalty += pose_cache[-1] - head_yaw
        print(yaw_penalty)
        pose_cache.append(head_yaw)
        pose_cache.pop(0)
        return pose_cache, yaw_penalty
            
    


def visualize(camera_yaw, camera_pitch, camera_roll, dir_imgs, label_box_imgs, label_pose_imgs, save_imgs_path=None, save_video_path=None):
    """
    input:
        camera_yaw: yaw camera
        camera_pitch: pitch camera
        camera_roll: roll camera
        dir_imgs: path to saved imgs directory
        label_box_imgs: path to saved bbox directory
        label_pose_imgs: path to saved pose file
    output:
        draw bboxs and poses on images.
        Export to imgs and video(option)
    """

    list_imgs = read_frames(dir_imgs)
    list_poses, head_pose_init = read_log_file(label_pose_imgs)

    # head_pose_offset = [head_pose_init[0] - camera_yaw, head_pose_init[1] - camera_pitch, head_pose_init[2] - camera_roll]
    pose_cache = []
    yaw_penalty = 0
    print("[INFO] Drawing ...")
    for index, img_path in enumerate(tqdm.tqdm(list_imgs[:])):
        # print(img_path)
        img = cv2.imread(img_path)
        head_poses = list_poses[index]
        # head_yaw =  int(head_pose_init[0] - head_poses['yaw'])
        # head_pitch = int(head_pose_init[1] - head_poses['pitch'])
        # head_roll = int(head_pose_init[2] - head_poses['roll'])
        head_yaw =  int(head_poses['yaw'] - camera_yaw)
        head_pitch = int(camera_pitch + head_poses['pitch'])
        head_roll = int(head_poses['roll'] - camera_roll)
        height, width, channels = img.shape

        # Check angle to detect "gymbal lock". 
        pose_cache, yaw_penalty = check_pose(pose_cache, yaw_penalty, head_yaw)
        head_yaw += yaw_penalty

        # print(height, width)
        img_name = os.path.basename(img_path)
        # label_name = img_name.replace(".jpg", ".txt")
        # label_path = os.path.join(label_box_imgs, label_name)
        # bboxs = get_bbox_YOLO_format(label_path, width, height)
        bboxs = [[width//2-10, height//2-10, width//2+10, height//2+10]]
        # print(bboxs)
        drawed_img = draw_annotates(img, bboxs, pose=[- head_yaw, head_pitch, - head_roll])
        if save_imgs_path:
            cv2.imwrite(os.path.join(save_imgs_path, img_name), drawed_img)

        # print(img_name)
        # print(f"[INFO] Head sensor: [{head_poses['yaw']}, {head_poses['pitch']}, {head_poses['pitch']}]")
        # print(f"[INFO] Head init: [{head_pose_init[0], head_pose_init[1], head_pose_init[2]}]")
        # # print(f"[INFO] Camera sensor: [{camera_yaw}, {camera_pitch}, {camera_roll}]")
        # print(f"[INFO] Img pose: [{head_yaw}, {head_pitch}, {head_roll}]")
        
        # print(label_path)
    # print(len(list_imgs))
    # print(len(list_label_boxs))
    if save_video_path:
        generate_video(save_imgs_path, save_video_path)

if __name__ == "__main__":
    dir_imgs = "/home/linhnv/projects/label-studio/imgs"
    label_box_imgs = "/media/2tb/projects/VL's/label-studio/labels/Test_02_01"
    label_pose_imgs = "data/logs/2021_01_31_21_58_49.109253_1612105129.1092527.txt"

    save_dir = "/media/2tb/projects/VL's/label-studio/processed"

    # data_name = os.path.basename(dir_imgs)
    data_name = "Test_03_03"
    save_path = os.path.join(save_dir, data_name)

    #359.81,57.44,4.69
    yaw_camera = 0
    pitch_camera = 40
    roll_camera = 5
    
    save_imgs_path = os.path.join(save_path, "imgs")
    save_video_path = os.path.join(save_path, "videos")
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    Path(save_imgs_path).mkdir(parents=True, exist_ok=True)
    Path(save_video_path).mkdir(parents=True, exist_ok=True)
    
    visualize(yaw_camera, pitch_camera, roll_camera, dir_imgs, label_box_imgs, label_pose_imgs=label_pose_imgs, save_imgs_path=save_imgs_path, save_video_path=save_video_path)
    
