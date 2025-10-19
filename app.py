from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form, Response
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import cv2
import asyncio
from gpiozero import Servo
from time import sleep
import threading
from queue import Queue

from camera_server import camera_server_fastapi


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ----- VERY SIMPLE IN-MEM AUTH (demo only) -----
USER = "admin"
PASSWORD = "strongpassword"

sessions = set()  # set of session ids

# Очередь для хранения кадров
frame_queue = Queue(maxsize=1)

# Запускаем сервер камеры в отдельном потоке
camera_thread = threading.Thread(target=camera_server_fastapi, daemon=True, args=(frame_queue,))
camera_thread.start()


def check_auth(request: Request):
    sid = request.cookies.get("sid")
    return sid in sessions


def mjpeg_generator_old():
    # ----- Camera capture -----
    # Открываем камеру (0). На Raspberry Pi может быть другой источник.
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            continue
        _, img = cv2.imencode('.jpg', frame)
        frame_bytes = img.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        # небольшая пауза
        sleep(0.03)


def mjpeg_generator():
    while True:
        try:
            # Получаем кадр из очереди с таймаутом
            frame = frame_queue.get(timeout=1.0)

            # Кодируем кадр в JPEG
            success, img = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if success:
                frame_bytes = img.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            # Небольшая пауза для контроля FPS
            sleep(0.03)

        except:
            # Если нет кадров, отправляем черный экран или ждем
            continue


@app.get("/")
def root(request: Request):
    if not check_auth(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
def login_post(response: Response, username: str = Form(...), password: str = Form(...)):
    if username == USER and password == PASSWORD:
        sid = "sess-" + str(len(sessions) + 1)
        sessions.add(sid)
        response = RedirectResponse("/", status_code=302)
        response.set_cookie("sid", sid, httponly=True, samesite="lax")
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": {}, "error": "Неправильные данные"})


@app.get("/stream")
def stream(request: Request):
    if not check_auth(request):
        return RedirectResponse("/login")
    return StreamingResponse(mjpeg_generator(), media_type='multipart/x-mixed-replace; boundary=frame')



'''
# ----- WebSocket for WASD -----
servo = Servo(17)  # BCM pin 17; настрой в соответствии с подключением
# начальное положение
servo.value = 0.0

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # ожидается одна буква: W/A/S/D
            key = data.upper()
            if key == "W":
                # поднять
                servo.value = min(1.0, (servo.value or 0) + 0.1)
            elif key == "S":
                servo.value = max(-1.0, (servo.value or 0) - 0.1)
            elif key == "A":
                # пример: поворот влево (если второй сервопривод — аналогично)
                pass
            elif key == "D":
                pass
            # можно отправлять ответ клиенту
            await websocket.send_text(f"OK:{key}")
    except WebSocketDisconnect:
        pass
'''