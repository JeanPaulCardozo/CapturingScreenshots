import mss
import cv2
import numpy as np
from pynput import mouse
import threading

coords = {"x1": 0, "y1": 0, "x2": 0, "y2": 0}
listener = None


def stopListerner():
    global listener
    listener.stop()


def captureScreenshot():
    x1, y1, x2, y2 = coords["x1"], coords["y1"], coords["x2"], coords["y2"]

    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)

    width, height = x2 - x1, y2 - y1

    with mss.mss() as sct:
        capture = {"top": y1, "left": x1, "width": width, "height": height}
        screenshot = sct.grab(capture)

        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        cv2.imwrite("screenshot.png", img)


def onClick(x, y, button, pressed):
    global coords

    if pressed:
        coords["x1"], coords["y1"] = x, y
    else:
        coords["x2"], coords["y2"] = x, y
        threading.Timer(1, stopListerner).start()
        captureScreenshot()


with mouse.Listener(on_click=onClick) as listener:
    print("🔲 Selecciona la región manteniendo presionado el clic izquierdo...")
    listener.join()
