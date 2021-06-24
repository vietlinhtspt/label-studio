import os
import cv2
import tqdm
import numpy as np

from pathlib import Path
from PIL import Image
from visualize import read_frames, read_log_file, get_bbox_YOLO_format

def crop_and_save(img, bboxs, pose, save_path, seq_name, img_name):
    """
    input:
        image: RGB image
        bboxs: [[x1_min,y1_min, x2_max, y2_max]]
        pose: [[yaw, roll, pitch]]
    output:
        draw bboxs and poses on image
    """
    anno_path = os.path.join(save_path, f"{seq_name}_annotation_crop_imgs.txt")
    cropped_img_dir_path = os.path.join(save_path, f"cropped_imgs")
    cropped_img_path = os.path.join(cropped_img_dir_path, img_name)
    Path(cropped_img_dir_path).mkdir(parents=True, exist_ok=True)
    cropped_img_relative_path = os.path.join(f"cropped_imgs", img_name)
    with open(anno_path, "a") as f:
        for bbox in bboxs:
        # print(f"[INFO] bbox: {bboxs}")
            # convert BRG to RGB
            img = img[:,:,::-1]
            frame = Image.fromarray(img)
            cropped_width = bbox[3] - bbox[1]
            cropped_height = bbox[2] - bbox[0]

            x_min = bbox[0] - cropped_height/3
            x_max = bbox[2] + cropped_height/3
            y_min = bbox[1] - cropped_width/5
            y_max = bbox[3] + cropped_width/5
            img = frame.crop(np.array([x_min, y_min, x_max, y_max]))
            img.save(cropped_img_path)
            
            yaw, pitch, roll = pose[0], pose[1], pose[2]
            line = cropped_img_relative_path + ','+str(int(cropped_height/3))+ ',' +str(int(cropped_width/5))+ ',' +str(int(cropped_height * (4/3)))+ ',' +str(int(cropped_height * (6/5))) + ','+str(int(yaw))+','+str(int(pitch))+','+str(int(roll))+'\n'
            f.write(line)

    return img
    

def prepare_data(camera_yaw, camera_pitch, camera_roll, dir_imgs, label_box_imgs, label_pose_imgs, save_imgs_path, seq_name):
    print("Start preparing data.")
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
    for index, img_path in enumerate(tqdm.tqdm(list_imgs[:])):
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

        crop_and_save(img, bboxs, [head_yaw, head_roll, head_pitch], save_imgs_path, seq_name, img_name)
        




if __name__ == "__main__":
    dir_imgs = "/home/linhnv/projects/label-studio/09"
    label_box_imgs = "/media/2tb/projects/VL's/UetHeadpose/09_labels"
    label_pose_imgs = "/home/linhnv/projects/label-studio/data/processed_log/09.txt"

    save_dir = "/media/2tb/projects/VL's/UetHeadpose/pre_processed"

    # data_name = os.path.basename(dir_imgs)
    data_name = "09"
    save_path = os.path.join(save_dir, data_name)

    yaw_camera = 180 + 62.488
    pitch_camera = 8.1
    roll_camera = 32.6
    
    Path(save_path).mkdir(parents=True, exist_ok=True)
    

    prepare_data(yaw_camera, pitch_camera, roll_camera, dir_imgs, label_box_imgs, label_pose_imgs=label_pose_imgs, save_imgs_path=save_path, seq_name=data_name)