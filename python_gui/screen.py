import win32gui
import win32con
import win32api

from PyQt5.QtWidgets import QApplication
import sys
import threading
import queue
import time

class ScreenDraw(object):

    def __init__(self):
        self.hwnd = 0  # 窗口的编号，0号表示当前活跃窗口
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)

    def drawRect(self, x, y, w, h):
        win32gui.FlashWindow(self.hwnd, 0)
        self.prebrush = win32gui.SelectObject(self.hwndDC, self.hbrush)
        win32gui.Rectangle(self.hwndDC, x - 1, y - 1, x + w + 2, y + h + 2)  # 左上到右下的坐标

    def setPenColor(self, r, g, b):
        self.hbrush = win32gui.GetStockObject(win32con.NULL_BRUSH)  # 定义透明画刷，这个很重要！！
        self.hPen = win32gui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(r, g, b))  # 定义框颜色
        win32gui.SelectObject(self.hwndDC, self.hPen)
        self.prebrush = win32gui.SelectObject(self.hwndDC, self.hbrush)
        win32gui.SelectObject(self.hwndDC, self.prebrush)

    def close(self):
        win32gui.DeleteObject(self.hPen)
        win32gui.DeleteObject(self.hbrush)
        win32gui.DeleteObject(self.prebrush)
        win32gui.ReleaseDC(self.hwnd, self.hwndDC)

class ScreenGet(object):

    def __init__(self):
        self.hwnd = 0
        self.app = QApplication(sys.argv)
        self.screen = self.app.primaryScreen()

        self.thread = threading.Thread(target=self.thread)
        self.running = False

        self.image = None
        self.image_out_q = queue.Queue(2)

        self.image_x = 0
        self.image_y = 0
        self.image_w = 480
        self.image_h = 320
        self.image_x_temp = 0
        self.image_y_temp = 0
        self.image_w_temp = 480
        self.image_h_temp = 320

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def getScreen(self, x, y, w, h):
        if self.image_out_q.qsize() > 0:
            image = self.image_out_q.get()
            self.setScreenArea(x, y, w, h)
            return image
        else:
            # screen = self.app.primaryScreen()
            image = self.screen.grabWindow(self.hwnd, x, y, w, h)
            return image

    def setScreenArea(self, x, y, w, h):
        self.image_x_temp = x
        self.image_y_temp = y
        self.image_w_temp = w
        self.image_h_temp = h

    def screenAreaParamUpdate(self):
        self.image_x = self.image_x_temp
        self.image_y = self.image_y_temp
        self.image_w = self.image_w_temp
        self.image_h = self.image_h_temp

    def thread(self):
        while self.running:
            if self.image_out_q.qsize() < 2:
                self.screenAreaParamUpdate()
                image = self.screen.grabWindow(self.hwnd, self.image_x, self.image_y,self.image_w, self.image_h)
                self.image_out_q.put(image)
            else:
                time.sleep(0.01)
