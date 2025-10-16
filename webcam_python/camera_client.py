import socket
import cv2
from dotenv import load_dotenv
import os


load_dotenv()


UDP_IP = os.getenv('UDP_IP')
UDP_PORT = os.getenv('UDP_PORT')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap = cv2.VideoCapture(0)

counter = 0
mean_byte_len = 0

while True:
    counter += 1
    ret, frame = cap.read()
    if not ret:
        break

    _, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    data = encoded.tobytes()
    mean_byte_len += len(data)

    if counter == 100:
        print(mean_byte_len / 100)
        mean_byte_len = 0
        counter = 0

    if len(data) < 65507:
        sock.sendto(data, (UDP_IP, UDP_PORT))

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()



