import cv2
import os
#Below code will capture the video frames and will sve it a folder (in current working directory)

def get_video_start_time(username, password, ip_address, port, channel, stream, 
                        starting_year, starting_month, starting_day, 
                        starting_hour, starting_minute, starting_second, path_save_frame):

    uri = f"rtsp://{username}:{password}@{ip_address}:{port}/Streaming/tracks/{channel}{stream}\?starttime={starting_year}{starting_month}{starting_day}\T{starting_hour}{starting_minute}{starting_second}z"
    # uri = "rtsp://admin:abcd1234@192.168.10.75:554/Streaming/tracks/101\?starttime=20201130\T121111z"
    print(uri)

    #video path
    cap = cv2.VideoCapture(uri)
    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
     
    # With webcam get(CV_CAP_PROP_FPS) does not work.
    # Let's see for ourselves.
    if int(major_ver)  < 3 :
        fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        print("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
    else :
        fps = cap.get(cv2.CAP_PROP_FPS)
        print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))
        
    count = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        else:
            frame = cv2.resize(frame, (960, 540), interpolation = cv2.INTER_AREA)
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