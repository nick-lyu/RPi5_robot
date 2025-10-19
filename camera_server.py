import socket
import cv2
import numpy as np


def camera_server():
    print('Start camera server...')
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(65536)  # ждём пакет
        nparr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is not None:
            cv2.imshow("Received", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()


def camera_server_fastapi(frame_queue):
    print('Start camera server...')
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    # Увеличиваем размер буфера сокета
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536 * 10)

    while True:
        try:
            data, addr = sock.recvfrom(65536)
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                # Очищаем очередь и добавляем новый кадр
                if frame_queue.full():
                    try:
                        frame_queue.get_nowait()
                    except:
                        pass
                frame_queue.put(frame)

        except Exception as e:
            print(f"Error receiving frame: {e}")
            continue



if __name__ == '__main__':
    camera_server()
    pass



