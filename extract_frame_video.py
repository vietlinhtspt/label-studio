import numpy as np
import cv2
import os

cap = cv2.VideoCapture("/home/linhnv/Downloads/Demo_headpose_inlab.mp4")
path_save = "/media/2tb/projects/VL's/headpose_data/AILab_mask_nomask/raw_frames"

# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")

# Read until video is completed
count_frame = 0
while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:
    count_frame += 1
    # Display the resulting frame
    frame_name = "{:04d}.jpg".format(count_frame)
    # print(frame_name)
    cv2.imwrite(os.path.join(path_save, frame_name), frame) 


  # Break the loop
  else: 
    break

# When everything done, release the video capture object
cap.release()
