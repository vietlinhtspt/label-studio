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

def draw_axis(img, yaw, pitch, roll, tdx=None, tdy=None, size=80):
    """
    input:
        img: cv2 image
        yaw: euler (360) 
        pitch: euler (360)
        roll: euler (360)
        tdx, tdy: tdx = width / 2, tdy = height / 2
    output:
    """
    
    yaw_euler = yaw 
    pitch_euler = pitch
    roll_euler = roll
    yaw = yaw - 90
    pitch = pitch * np.pi / 180
    yaw = -(yaw * np.pi / 180)
    roll = roll * np.pi / 180

    if tdx != None and tdy != None:
        tdx = tdx
        tdy = tdy
    else:
        height, width = img.shape[:2]
        tdx = width / 2
        tdy = height / 2

    # X-Axis pointing to right. drawn in red
    x1 = size * (cos(yaw) * cos(roll)) + tdx
    y1 = size * (cos(pitch) * sin(roll) + cos(roll)
                 * sin(pitch) * sin(yaw)) + tdy

    # Y-Axis | drawn in green
    #        v
    x2 = size * (-cos(yaw) * sin(roll)) + tdx
    y2 = size * (cos(pitch) * cos(roll) - sin(pitch)
                 * sin(yaw) * sin(roll)) + tdy

    # Z-Axis (out of the screen) drawn in blue
    x3 = size * (sin(yaw)) + tdx
    y3 = size * (-cos(yaw) * sin(pitch)) + tdy

    cv2.line(img, (int(tdx), int(tdy)), (int(x1), int(y1)), (0, 0, 255), 3)
    cv2.line(img, (int(tdx), int(tdy)), (int(x2), int(y2)), (0, 255, 0), 3)
    cv2.line(img, (int(tdx), int(tdy)), (int(x3), int(y3)), (255, 0, 0), 2)

    cv2.putText(img, "yaw"+str(yaw_euler), (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(img, "roll"+str(roll_euler), (int(x2), int(y2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
    cv2.putText(img, "pitch"+str(pitch_euler), (int(x3), int(y3)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)

    return img

def draw_annotate(image, bbox, yaw, pitch, roll):
    """
    input:
        image: RGB image
        bbox: np.array([x1_min,y1_min, x2_max, y2_max])
        pose: yaw, pitch, roll
    output:
        draw bbox and pose on image
    """
    x, y = bbox[:2]
    w, h = (bbox[2:] - bbox[:2])
    x, y, w, h = int(x), int(y), int(w), int(h)
    cv2.rectangle(image, (x, y, w, h), (0,255,255), 3)
    x_c, y_c = int(x + w / 2), int(y + h / 2)
    draw_axis(image, yaw, pitch, roll, x_c, y_c)
    # cv2.imwrite("test.jpg", image)
    return image

def draw_annotates(img, bboxs, pose=[0, 0, 0]):
    """
    input:
        image: RGB image
        bboxs: [[x1_min,y1_min, x2_max, y2_max]]
        pose: [[yaw, roll, pitch]]
    output:
        draw bboxs and poses on image
    """
    for bbox in bboxs:
    # print(f"[INFO] bbox: {bboxs}")
        draw_annotate(img, np.array([bbox[0], bbox[1], bbox[2], bbox[3]]), pose[0], pose[1], pose[2])  
    return img

def get_bbox_YOLO_format(label_path, width, height):
    """
    input:
        label_path: path to label with YOLO format
        width: width img
        height: height img
    output:
        bboxs in label file
    """
    bboxs_output = []
    if not os.path.exists(label_path):
        return bboxs_output
    with open(label_path) as f:
        lines = f.readlines()
        # "0 0.341095 0.475086 0.032063 0.063574\n"
        bboxs = [line[:-2].split(" ")[1:] for line in lines]
        for bbox in bboxs[:]:
            # print(bbox)
            # print(height, width)
            x1 = float(bbox[0]) * width 
            y1 = float(bbox[1]) * height 
            width_bbox = float(bbox[2]) * width 
            height_bbox = float(bbox[3]) * height 
            x1 = x1 - int(width_bbox / 2)
            y1 = y1 - int(height_bbox / 2)
            # print(x1, y1, width, height)
            bboxs_output.append([x1, y1, x1+width_bbox, y1+height_bbox])

    return bboxs_output

def read_frames(dir_imgs):
    images = [os.path.join(dir_imgs, img) for img in os.listdir(dir_imgs) 
              if img.endswith(".jpg") or
                 img.endswith(".jpeg") or
                 img.endswith("png")] 
    # path_images = sorted(images, key=lambda x: float(os.path.basename(x).split("_")[2]), reverse=False)
    # # old format
    # path_images = sorted(images, key=lambda x: float(os.path.basename(x).split("_")[2].split("T")[1]), reverse=False)
    # new_format
    path_images = sorted(images, key=lambda x: float(os.path.basename(x).split(".")[0]), reverse=False)
    
    return path_images

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
    
    print("[INFO] Drawing ...")
    for index, img_path in enumerate(tqdm.tqdm(list_imgs[9:])):
        # print(img_path)
        img = cv2.imread(img_path)
        if index >= len(list_poses):
            break
        head_poses = list_poses[index]
        # head_yaw =  camera_yaw - 
        # head_pitch = camera_pitch
        # head_roll = camera_roll + head_poses['roll']
        head_yaw = camera_yaw - head_poses['yaw']
        head_pitch = camera_pitch - head_poses['pitch']
        head_roll = camera_roll + head_poses['roll']
        # print(camera_roll, head_poses['roll'])
        height, width, channels = img.shape

        # print(height, width)
        img_name = os.path.basename(img_path)
        label_name = img_name.replace(".jpg", ".txt")
        label_path = os.path.join(label_box_imgs, label_name)
        bboxs = get_bbox_YOLO_format(label_path, width, height)
        # bboxs = np.array([[0, 0, 128, 128]])
        # print(bboxs)
        drawed_img = draw_annotates(img, bboxs, pose=[head_yaw, head_roll, head_pitch])
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

# Video Generating function 
def generate_video(imgs_path, saved_video_path):
    """
    input:
        imgs_path: Path to dir saved all drawed imgs
        saved_video_path: Saving video path
    output:
        None
    """
    print(f"[INFO] Wrting video.")
    # print(imgs_path)
    images = read_frames(imgs_path)
    
    # print(images)
    frame = cv2.imread(images[0]) 
    # print(frame.shape)
   
  
    # setting the frame width, height width 
    # the width, height of first image 
    height, width, layers = frame.shape   
  
    video = cv2.VideoWriter(os.path.join(saved_video_path, "output.avi"), 0, 5, (width, height))  
  
    # Appending the images to the video one by one 
    for image in tqdm.tqdm(images):  
        video.write(cv2.imread(os.path.join(imgs_path, image)))  
      
    # Deallocating memories taken for window creation 
    cv2.destroyAllWindows()  
    video.release()  # releasing the video generated 

    

if __name__ == "__main__":
    dir_imgs = "/home/linhnv/projects/label-studio/09"
    label_box_imgs = "/media/2tb/projects/VL's/UetHeadpose/09_labels"
    label_pose_imgs = "/home/linhnv/projects/label-studio/data/processed_log/09.txt"

    save_dir = "/home/linhnv/projects"

    # data_name = os.path.basename(dir_imgs)
    data_name = "09"
    save_path = os.path.join(save_dir, data_name)

    yaw_camera = 180 + 62.488
    pitch_camera = 8.1
    roll_camera = 32.6
    
    save_imgs_path = os.path.join(save_path, "imgs")
    save_video_path = os.path.join(save_path, "videos")
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    Path(save_imgs_path).mkdir(parents=True, exist_ok=True)
    Path(save_video_path).mkdir(parents=True, exist_ok=True)
    
    visualize(yaw_camera, pitch_camera, roll_camera, dir_imgs, label_box_imgs, label_pose_imgs=label_pose_imgs, save_imgs_path=save_imgs_path, save_video_path=save_video_path)
    

    # draw_annotate(img, bboxs[0], 0, 0, 0)

    