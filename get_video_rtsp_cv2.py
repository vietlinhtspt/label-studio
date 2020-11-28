import cv2
import os
#Below code will capture the video frames and will sve it a folder (in current working directory)

def get_video_start_time(username, password, ip_address, port, channel, stream, 
                        starting_year, starting_month, starting_day, 
                        starting_hour, starting_minute, starting_second, path_save_frame):

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
            break
    cap.release()
    cv2.destroyAllWindows()

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
    get_video_start_time(username, password, ip_address, port, channel, stream, year, month, day, hour, minute, second, path_save_frame)