from ultralytics import YOLO
import cv2
import serial
import time
from utliites import *
import threading

portConnect = False
try:
    ser = serial.Serial('/dev/tty.usbmodem14101', 115200, timeout=1)
    portConnect = True
    print("Port Connected Successfully - Diego")
except:
    ser = None
    print("No Port Connected - Diego")

time.sleep(1)
model = YOLO("yolov8n.pt")
model.fuse()


frameCenterWidth = 0
frameCenterHeight = 0

latestFrame = None
running = True
lock = threading.Lock()

def cameraThread():
    global latestFrame, running, frameCenterWidth, frameCenterHeight

    cap = cv2.VideoCapture(0)

    frameCenterWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) / 2)
    frameCenterHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)

    while running:
        ret, frame = cap.read()
        if ret:
            with lock:
                latestFrame = frame

    cap.release()


thread = threading.Thread(target=cameraThread)
thread.daemon = True
thread.start()


objectFound = False
prevTime = 0
currTime = 0
while running:
    with lock:
        if latestFrame is None:
            continue
        frame = latestFrame.copy()

    results = model(frame, classes=[67], imgsz=320, verbose=False)
    objectFound = False

    x1, x2, y1, y2 = 0, 0, 0, 0
    for r in results:
        for box in r.boxes:
            objectFound = True
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cv2.circle(frame, ((x1 + x2) // 2, (y1 + y2) // 2), 5, (0, 255, 0), 2)


    currTime = time.perf_counter()

    showFPS(currTime, prevTime, frame)
    prevTime = currTime

    # sendSerialData(objectFound, portConnect, ser, frameCenterWidth, frameCenterHeight, x1, x2, y1, y2)

    cv2.imshow("YOLOv8 Phone Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False
        break

cv2.destroyAllWindows()
