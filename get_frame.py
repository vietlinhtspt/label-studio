from utils import get_img_from_url, process_json_message
import cv2
import os
from glob import glob
#Below code will capture the video frames and will sve it a folder (in current working directory)

def get_video_start_time(username, password, ip_address, port, channel, stream, 
                        starting_year, starting_month, starting_day, 
                        starting_hour, starting_minute, starting_second, path_save_frame):
    """
    input:
    output:
    """

    uri = f"rtsp://{username}:{password}@{ip_address}:{port}/Streaming/tracks/{channel}{stream}\
        ?starttime={starting_year}{starting_month}{starting_day}\
        T{starting_hour}{starting_minute}{starting_second}z"
    # uri = "rtsp://admin:abcd1234@192.168.10.75:554/Streaming/tracks/101?starttime=20201111T111111z"
    print(uri)

    #video path
    cap = cv2.VideoCapture(uri)
    count = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        else:
            cv2.imshow('frame', frame)
            #The received "frame" will be saved. Or you can manipulate "frame" as per your needs.
            name = "rec_frame"+str(count)+".jpg"
            cv2.imwrite(os.path.join(path_save_frame,name), frame)
            count += 1
        if cv2.waitKey(20) & 0xFF == ord('q'):
         import os

def read_log_file(log_path):
    """
    input:
        log_path: path to log file
    output:
        list objects: list all sorted pose objects in lines by time. [{'time': 123, 'yaw': 0, 'pitch': 0, 'row': 0}]
    """
    # Using readlines() 
    log_file = open(log_path, 'r') 
    lines = [line.split("'")[1] for line in log_file.readlines()]
    line_objects = [process_json_message(line) for line in lines]
    line_objects.sort(key=lambda x: x['time'], reverse=False)
    print(f"[INFO] Num got frame: {len(line_objects)}")

    yaw_offset = 86.75
    pitch_offset = 64.25
    row_offset = -151.38

    return line_objects, [yaw_offset, pitch_offset, row_offset]
         
def get_frame_from_log(username, password, ip_address, port, channel, stream, 
                        starting_year, starting_month, starting_day, 
                        starting_hour, starting_minute, starting_second, timestamp,
                        path_save_frame, log_path):
    """
    input:
    output:
    """
    timestamp_frame_start = timestamp - 2
    starting_second = int(starting_second) - 2
    uri = f"rtsp://{username}:{password}@{ip_address}:{port}/Streaming/tracks/{channel}{stream}?starttime={format(int(starting_year), '04d')}{format(int(starting_month), '02d')}{format(int(starting_day), '02d')}T{format(int(starting_hour) - 7, '02d')}{format(int(starting_minute), '02d')}{str(format(int(starting_second), '02d'))}z"
    # uri = "rtsp://admin:abcd1234@192.168.10.75:554/Streaming/tracks/101?starttime=20201111T111111z"
    print(uri)

    # read all line and sort by time 
    line_object, _ = read_log_file(log_path)

    #video path
    cap = cv2.VideoCapture(uri)
    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
     
    # With webcam get(CV_CAP_PROP_FPS) does not work.
    # Let's see for ourselves.
    fps = 0
    if int(major_ver)  < 3 :
        fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        print("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
    else :
        fps = cap.get(cv2.CAP_PROP_FPS)
        print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
    count_frame = 0
    
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        else:
            # cv2.imshow('frame', frame)
            #The received "frame" will be saved. Or you can manipulate "frame" as per your needs.
            timestamp_frame = timestamp_frame_start + (count_frame * (1/fps))
            print(f"[INFO]-{timestamp_frame}-|-{line_object[0]['time']}-|-{len(line_object)}-----", end="\r") 
            
            name = f"rec_frame_{format(int(starting_year), '04d')}{format(int(starting_month), '02d')}{format(int(starting_day), '02d')}T{format(int(starting_hour), '02d')}{format(int(starting_minute), '02d')}{starting_second + count_frame * (1.0/fps)}_{timestamp_frame}.jpg"
            # 1609900972.982348 | 
            # 1609901392.553
            # 1609913255.610
            # 1609901673
            if abs(timestamp_frame * 1000 - line_object[0]['time']) < (1000 / (fps)):
                cv2.imwrite(os.path.join(path_save_frame,name), frame)
                del line_object[0]
                if len(line_object) == 0:
                    break
            count_frame += 1
        # if cv2.waitKey(20) & 0xFF == ord('q'):
        #     break
    cap.release()
    cv2.destroyAllWindows()

def get_frame_from_all_log(username, password, ip_address, port, channel, stream, 
                        path_save_frame, logs_dir):
    """
    input:
    output:
    """
    list_all_logs = glob(f"{logs_dir}/*")
    for log_path in list_all_logs:
        # print(os.path.basename(log_path))
        name_file = os.path.basename(log_path)
        list_info = name_file.split("_")
        year = list_info[0]
        month = list_info[1]
        day = list_info[2]
        hour = list_info[3]
        minute = list_info[4]
        second = list_info[5].split(".")[0]
        timestamp = float(list_info[6][:-4])
        
        get_frame_from_log(username, password, ip_address, port, channel, stream, 
                            year, month, day, hour, minute, second, timestamp,
                            path_save_frame, log_path)

if __name__ == "__main__":
    username = "admin"
    password = "abcd1234"
    ip_address = "192.168.10.75"
    port = "554"
    channel = "1"
    stream = "01"
    year = "2020"
    month = "11"
    day = "26"
    hour = "11"
    minute = "11"
    second = "11"
    path_save_frame = "imgs"
    # get_video_start_time(username, password, ip_address, port, channel, stream, year, month, day, hour, minute, second, path_save_frame)
    log_dir = "data/logs"
    frames_dir = "data/frames"
    get_frame_from_all_log(username, password, ip_address, port, channel, stream, path_save_frame, log_dir)