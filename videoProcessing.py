from ultralytics import YOLO
import cv2
import serial
import time
from utliites import *

# Connect to Pico serial port
portConnect = False
try:
    ser = serial.Serial('/dev/tty.usbmodem14101', 115200, timeout=1)
    portConnect = True
    print("Port Connected Successfully - Diego")
except:
    print("No Port Connected - Diego")

time.sleep(1)
model = YOLO("yolov8n.pt")
model.fuse()

cap = cv2.VideoCapture(0)

frameCenterWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) / 2)
frameCenterHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)

print("center:", frameCenterWidth, frameCenterHeight)





def showFeed():
    frame_count = 0

    currTime = 0
    prevTime = 0

    while True:
        frame_count += 1



        # skip every other frame
        if frame_count % 2 != 0:
            ret, frame = cap.read()
            if not ret:
                break
        else:
            continue

        results = model(frame, classes=[67])
        phone_found = False

        for r in results:
            for box in r.boxes:
                phone_found = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.circle(frame, ((x1 + x2)//2, (y1 + y2)//2), 10, (0, 255, 0), 2)
                # cv2.line(frame,
                #          (frameCenterWidth, frameCenterHeight),
                #          ((x1 + x2)//2, (y1 + y2)//2),
                #          (255, 0, 0), 3)

        currTime = time.perf_counter()
        showFPS(currTime, prevTime, frame)
        prevTime = currTime

        if phone_found:
            if portConnect:
                print("phone detected")
                # phoneDetected, Direction(HIGH = cw, LOW = ccw),
                direction = determineLeftRight(frameCenterWidth, frameCenterHeight, (x1 + x2)//2, (y1 + y2)//2)
                if direction == "CW":
                    ser.write(b"True,CW\n")
                if direction == "CCW":
                    ser.write(b"True,CCW\n")
                print("Serial Data Sent")
                if ser.in_waiting:
                    picoOutput = ser.readline().decode().strip()
                    if picoOutput:
                        print("Pico Output:", picoOutput)
            else:
                print("phone detected - no port found")
                print(determineLeftRight(frameCenterWidth, frameCenterHeight, (x1 + x2) // 2, (y1 + y2) // 2))
        else:
            print("no phone detected")
            try:
                ser.write(b"20\n")
            except Exception as e:
                print("No Serial Output:", e)

        cv2.imshow("YOLOv8 Phone Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if portConnect:
        ser.close()
    cap.release()
    cv2.destroyAllWindows()
