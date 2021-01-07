from utils import get_img_from_url, process_json_message
import cv2
import os
from glob import glob

def get_frame_from_log(path_save_frame, log_path, timestamp, video_path):
    """
    input:
    output:
    """
    timestamp_frame_start = timestamp
    starting_second = timestamp
    
    # Using readlines() 
    log_file = open(log_path, 'r') 
    lines = [line.split("'")[1] for line in log_file.readlines()]
    line_object = [process_json_message(line) for line in lines]
    line_object.sort(key=lambda x: x['time'], reverse=False)
    print(f"Num got frame: {len(line_object)}")

    #video path
    cap = cv2.VideoCapture(video_path)
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
            
            name = f"rec_frame_{starting_second + count_frame * (1.0/fps)}_{timestamp_frame}.jpg"
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

def get_frame_from_all_log(path_save_frame, logs_dir, video_path):
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
        timestamp = 1609922440
        
        get_frame_from_log(path_save_frame, log_path, timestamp, video_path)


if __name__ == "__main__":
    
    path_save_frame = "imgs"
    # get_video_start_time(username, password, ip_address, port, channel, stream, year, month, day, hour, minute, second, path_save_frame)
    log_dir = "data/logs"
    frames_dir = "data/frames"
    video_path = "2021-01-06 15-40-39.mkv"
    get_frame_from_all_log(path_save_frame, log_dir, video_path)