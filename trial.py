from ultralytics import YOLO
import cv2
import serial
import time

# Connect to Pico serial port
ser = serial.Serial('/dev/cu.usbmodem14101', 115200, timeout=1)
time.sleep(2)

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, stream=True)
    #phone_found = False

    phone_found = False

    for r in results:
        for box in r.boxes:
            cls = model.names[int(box.cls[0])]
            if cls.lower() in ["cell phone", "mobile phone", "phone"]:
                phone_found = True
                # draw box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, cls, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    if phone_found:
        print("phone detected")
        ser.write(b"phone detected\n")
    else:
        ser.write(b"no phone\n")

    cv2.imshow("YOLOv8 Phone Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
ser.close()
cv2.destroyAllWindows()







