import os
import socket
from picamera2 import Picamera2
from dotenv import load_dotenv


load_dotenv()

UDP_IP = os.getenv('UDP_IP')
UDP_PORT = int(os.getenv('UDP_PORT'))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480)},
    # encode="mjpeg"  # Аппаратное кодирование!
)
picam2.configure(config)
picam2.start()

while True:
    # Аппаратное кодирование - почти нулевая задержка
    data = picam2.capture_array(wait=True)  # Уже в формате JPEG!
    sock.sendto(data, (UDP_IP, UDP_PORT))



