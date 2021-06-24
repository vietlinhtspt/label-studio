import tqdm
import glob, os
import h5py
import os
import numpy as np
from PIL import Image
import cv2
import tqdm
import albumentations as albu
from math import cos, sin

seed = 2020
np.random.seed(seed)

def draw_axis(img, yaw, pitch, roll, tdx=None, tdy=None, size = 80, radian=False):
    if not radian:
       
        pitch = pitch * np.pi / 180
        yaw = -(yaw * np.pi / 180)
        roll = roll * np.pi / 180
        # print(pitch)

    if tdx != None and tdy != None:
        tdx = tdx
        tdy = tdy
    else:
        height, width = img.shape[:2]
        tdx = width / 2
        tdy = height / 2

    # X-Axis pointing to right. drawn in red
    x1 = size * (cos(yaw) * cos(roll)) + tdx
    y1 = size * (cos(pitch) * sin(roll) + cos(roll) * sin(pitch) * sin(yaw)) + tdy

    # Y-Axis | drawn in green
    #        v
    x2 = size * (-cos(yaw) * sin(roll)) + tdx
    y2 = size * (cos(pitch) * cos(roll) - sin(pitch) * sin(yaw) * sin(roll)) + tdy

    # Z-Axis (out of the screen) drawn in blue
    x3 = size * (sin(yaw)) + tdx
    y3 = size * (-cos(yaw) * sin(pitch)) + tdy

    cv2.line(img, (int(tdx), int(tdy)), (int(x1),int(y1)),(0,0,255),3)
    cv2.line(img, (int(tdx), int(tdy)), (int(x2),int(y2)),(0,255,0),3)
    cv2.line(img, (int(tdx), int(tdy)), (int(x3),int(y3)),(255,0,0),2)

    return img

class HDF5DatasetWriter:
    def __init__(self, dims, outputPath, dataKey="images", bufSize=1000):
        # check to see if the output path exists, and if so, raise
        # an exception
        if os.path.exists(outputPath):
            raise ValueError("The supplied ‘outputPath‘ already exists and cannot be overwritten. Manually delete the file before continuing.", outputPath)

        # open the HDF5 database for writing and create two datasets:
        # one to store the images/features and another to store the
        # class labels
        self.db = h5py.File(outputPath, "w")
        self.data = self.db.create_dataset(dataKey, dims, dtype=np.uint8)
        # self.size_imgs = self.db.create_dataset("raw_size_data", (dims[0], 3) , dtype=np.uint8)
        self.labels = self.db.create_dataset("labels", (dims[0], 3), dtype="float")
        self.size_data = (dims[1], dims[2], dims[3])

        print(f"[Wranning] If input data is larger size {self.size_data}, auto resizer is called to target size: {self.size_data}.")


        target_size = max(dims[1], dims[2])

        self.resizer = albu.Compose([albu.SmallestMaxSize(target_size + 1, p=1.), albu.CenterCrop(target_size, target_size, p=1.)])
        # self.resizer = albu.Compose([albu.SmallestMaxSize(target_size, p=1.)])
        # self.centerCrop = albu.Compose([albu.CenterCrop(target_size, target_size, p=1.)])
        # store the buffer size, then initialize the buffer itself
        # along with the index into the datasets
        self.bufSize = bufSize
        self.buffer = {"data": [], "raw_size_data": [], "labels": []}
        self.idx = 0

    def add(self, rows, label):
        # add the rows and labels to the buffer
        if rows.shape[0] < 64 or rows.shape[1] < 64:
          return

        # print(rows.shape)
        resized = self.resizer(image=rows)
        rows = resized['image']
        # print("New shape: ", rows.shape)
        # resized = self.resizer(image=rows)
        # rows = resized['image']
        # print("New shape: ", rows.shape)
        padded_data = np.zeros(self.size_data)
        padded_data[:rows.shape[0],:rows.shape[1]] = rows
        size_raw_data = np.array(rows.shape)
        # print("Size label: ", label)
        # print("Size img: ", size_raw_data)
        
        self.buffer["data"].extend([padded_data])
        self.buffer["raw_size_data"].extend([size_raw_data])
        self.buffer["labels"].extend([label])
        
        # check to see if the buffer needs to be flushed to disk
        if len(self.buffer["data"]) >= self.bufSize:
            self.flush()
    
    def flush(self):
        # write the buffers to disk then reset the buffer
        i = self.idx + len(self.buffer["data"])
        self.data[self.idx:i] = self.buffer["data"]
        # self.size_imgs[self.idx:i] = self.buffer["raw_size_data"]
        self.labels[self.idx:i] = self.buffer["labels"]
        self.idx = i
        self.buffer = {"data": [], "raw_size_data": [], "labels": []}

    def close(self):
        # check to see if there are any other entries in the buffer
        # that need to be flushed to disk
        if len(self.buffer["data"]) > 0:
            self.flush()

        # close the dataset
        self.db.close()

def create_HDF5_file(dir_path, line_file_txt, outputPath):

    writer = HDF5DatasetWriter((len(line_file_txt), 64, 64, 3), outputPath)

    min_yaw, max_yaw, min_pitch, max_pitch, min_roll, max_roll = 0, 0, 0, 0, 0, 0

    # img_error = 0
    for i, line_txt in tqdm.tqdm(enumerate(line_file_txt[:])):
        # print(f"{i}_{line_txt}")
        img_path = dir_path + "/" + line_txt.split(",")[0]
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
        # Image.fromarray(draw_axis(np.copy(img), yaw, pitch, roll)).save("visualized_imgs/"f'Uet_val_img_{i}.jpg')

       

        label = np.array([yaw, pitch, roll])

        # yaw = float(angles[5])
        # pitch = float(angles[7])
        # roll = float(angles[6])


        # if yaw < min_yaw: min_yaw = yaw
        # if yaw > max_yaw: max_yaw = yaw
    
        # if pitch < min_pitch: min_pitch = pitch
        # if pitch > max_pitch: max_pitch = pitch

        # if roll < min_roll: min_roll = roll
        # if roll > max_roll: max_roll = roll

        # print(line_txt)
        # print(label)
        # print(label)

        writer.add(img,label)


        # if img.shape not in img_shapes:
        #   img_shapes.append(img.shape)

        # print(img_shapes)
    print(min_yaw, max_yaw, min_pitch, max_pitch, min_roll, max_roll)
    # print(img_error)
    writer.close()
        
def preprocess_data(path_data):
    
    path_txt_files = [file_path for file_path in glob.glob(path_data + "/*/*") if file_path.endswith(".txt")]
    print(len(path_txt_files))

    new_paths = []

    for path_txt_file in tqdm.tqdm(path_txt_files[:]):
        txt_file = open(path_txt_file, "r")
        # print(os.path.dirname(path_txt_file))
        dir_name = os.path.basename(str(os.path.dirname(path_txt_file)))
        txt_lines = txt_file.readlines()
        for txt_line in txt_lines[:]:
            
            new_paths.append(os.path.join(dir_name, txt_line))

    print(len(new_paths[:]))

    indexs = np.arange(len(new_paths))

    indexs_val = np.random.choice(len(new_paths), 2000, replace=False)
    indexs_train = np.delete(indexs, indexs_val, None)

    print(len(indexs_val))
    print(len(indexs_train))

    paths_val = [new_paths[index] for index in indexs_val]
    paths_train = [new_paths[index] for index in indexs_train] 

    # Size 64x64 for FSA-Net, 224x224 for Rankpose

    outputPath_1 = f"{path_data}/UETHeadpose_val_64x64_0_{len(paths_val)}.hdf5"
    create_HDF5_file(path_data, paths_val, outputPath_1)

    outputPath_2 = f"{path_data}/UETHeadpose_train_64x64_0_{len(paths_train)}.hdf5"
    create_HDF5_file(path_data, paths_train, outputPath_2)
    
    

if "__main__":
    path_data = "/media/2tb/projects/VL's/UetHeadpose/pre_processed"
    # preprocess_data(path_data)