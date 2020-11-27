import cv2
import time
from datetime import datetime, date
username = "admin"
password = "abcd1234"
ip_address = "192.168.10.75"
port = 554
channel = 1
stream = "01"
year = "2020"
month = "11"
day = "26"
hour = "11"
minute = "11"
second = "11"
endhour = "11"
endminute = "12"
endsecond = "12"

uri = f"rtsp://{username}:{password}@{ip_address}:{port}/Streaming/tracks/{channel}{stream}?starttime={year}{month}{day}T{hour}{minute}{second}z"
uri = "rtsp://admin:abcd1234@192.168.10.75:554/Streaming/tracks/101?starttime=20201111T111111z"
print(uri)

# # cap = cv2.VideoCapture("rtsp://admin:abcd1234@192.168.10.75:554/Streaming/channels/101")
# cap = cv2.VideoCapture(uri)

# while(cap.isOpened()):
#     ret, frame = cap.read()
#     cv2.imshow('frame', frame)
#     if cv2.waitKey(20) & 0xFF == ord('q'):
#         break
# cap.release()
# cv2.destroyAllWindows()

import vlc
player=vlc.MediaPlayer("hero_1.mp4")
player.play()