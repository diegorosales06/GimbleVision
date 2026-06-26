from ultralytics import YOLO
import cv2
import serial
import time
from utliites import *

def getDistancefromCenter(centerX, centerY, objectX, objectY):
    xDistance = objectX - centerX
    yDistance = objectY - centerY
    return xDistance, yDistance

def determineLeftRight(centerX, centerY, objectX, objectY):
    x, y = getDistancefromCenter(centerX, centerY, objectX, objectY)

    if x >= 0:  # object is to the RIGHT
        print("Right of center")
        return "CW"
    else:       # object is to the LEFT
        print("Left of center")
        return "CCW"


def showFPS(currTime, prevTime, img):
    timeDifference = currTime - prevTime
    FPS = 1/timeDifference
    cv2.putText(
        img,
        f"FPS: {round(FPS, 2)}",
        (20, 20),  # x, y position
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,  # font scale
        (0, 255, 0),  # color in BGR
        2,  # thickness
        cv2.LINE_AA
    )



def sendSerialData(objectFound, portConnect, ser, frameWidth, frameHeight, x1, x2, y1, y2):
    if objectFound:
        if portConnect:
            print("phone detected")
            # phoneDetected, Direction(HIGH = cw, LOW = ccw)
            direction = determineLeftRight(frameWidth, frameHeight, (x1 + x2) // 2, (y1 + y2) // 2)
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
            print(determineLeftRight(frameWidth, frameHeight, (x1 + x2) // 2, (y1 + y2) // 2))
    else:
        print("no phone detected")
        try:
            ser.write(b"20\n")
        except Exception as e:
            print("No Serial Output:", e)
