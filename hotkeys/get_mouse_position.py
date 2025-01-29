import pyautogui as gui

def main(*args, **kvargs):
    width, height = gui.size()
    x, y = gui.position()
    print(f"Mouse position: x={x}, y={y}, thats=width*{round(x/width,3)}, height*{round(y/height,3)}")