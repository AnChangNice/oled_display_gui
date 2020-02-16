import win32gui
import win32con
import win32api

from PyQt5.QtWidgets import QApplication
import sys

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

    def getScreen(self, x, y, w, h):
        screen = QApplication.primaryScreen()
        image = screen.grabWindow(self.hwnd, x, y, w, h)
        return image