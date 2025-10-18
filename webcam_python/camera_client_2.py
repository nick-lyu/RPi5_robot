import socket
from dotenv import load_dotenv
import os
from picamera2 import Picamera2
from PIL import Image # Кодирование в JPEG

load_dotenv()

UDP_IP = os.getenv('UDP_IP')
UDP_PORT = int(os.getenv('UDP_PORT'))  # Важно преобразовать в int

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Инициализация камеры
picam2 = Picamera2()

# Настройка конфигурации для захвата
config = picam2.create_still_configuration(main={"size": (640, 480)})  # Можно изменить размер
picam2.configure(config)

picam2.start()

counter = 0
mean_byte_len = 0

try:
    while True:
        counter += 1

        # Захват кадра
        array = picam2.capture_array()

        # Конвертация BGR в RGB (если нужно)
        # array = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)  # раскомментировать если нужен BGR

        image = Image.fromarray(array)

        # Альтернативный вариант с OpenCV (если он всё же установлен)
        # import cv2
        # _, encoded = cv2.imencode(".jpg", array, [cv2.IMWRITE_JPEG_QUALITY, 80])
        # data = encoded.tobytes()

        # Используем PIL для кодирования
        from io import BytesIO

        with BytesIO() as output:
            image.save(output, format="JPEG", quality=80)
            data = output.getvalue()

        mean_byte_len += len(data)

        if counter == 100:
            print(f"Average frame size: {mean_byte_len / 100:.2f} bytes")
            mean_byte_len = 0
            counter = 0

        if len(data) < 65507:  # Максимальный размер для UDP
            sock.sendto(data, (UDP_IP, UDP_PORT))
        else:
            print(f"Frame too large: {len(data)} bytes")

except KeyboardInterrupt:
    print("Stopping...")
finally:
    picam2.stop()
    sock.close()