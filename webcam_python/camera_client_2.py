import socket
from dotenv import load_dotenv
import os
from picamera2 import Picamera2
import cv2

load_dotenv()

UDP_IP = os.getenv('UDP_IP')
UDP_PORT = int(os.getenv('UDP_PORT'))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1280, 720)}) # 640, 480   1280, 720   1920, 1080
picam2.configure(config)
picam2.start()

counter = 0
mean_byte_len = 0

try:
    while True:
        counter += 1

        # Захват кадра
        array = picam2.capture_array()

        # Кодирование с помощью OpenCV
        _, encoded = cv2.imencode(".jpg", array, [cv2.IMWRITE_JPEG_QUALITY, 80])
        data = encoded.tobytes()

        mean_byte_len += len(data)

        if counter == 100:
            print(f"Average frame size: {mean_byte_len / 100:.2f} bytes")
            mean_byte_len = 0
            counter = 0

        if len(data) < 65507:
            sock.sendto(data, (UDP_IP, UDP_PORT))

except KeyboardInterrupt:
    print("Stopping...")
finally:
    picam2.stop()
    sock.close()

