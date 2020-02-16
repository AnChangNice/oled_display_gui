
from UI.main_ui import Ui_mainWindow
from window.imageModeWindow import ImageModeWindow
from window.videoModeWindow import VideoModeWindow
from window.screenModeWindow import ScreenModeWindow
from PyQt5.QtWidgets import QMainWindow

from serial_port import SerialPort

class MainWindow(object):
    def __init__(self):
        # setup window
        self.window = QMainWindow()
        self.main_ui = Ui_mainWindow()
        self.main_ui.setupUi(self.window)
        self.main_ui.retranslateUi(self.window)

        self.imageModeWindow = ImageModeWindow(self.window, self.main_ui)
        self.videoModeWindow = VideoModeWindow(self.window, self.main_ui)
        self.screenModeWindow = ScreenModeWindow(self.window, self.main_ui)

        # connect signal and slot
        self.main_ui.pbt_scanSerialPort.clicked.connect(self.portScan)
        self.main_ui.combox_serialPortList.activated.connect(self.portSelect)
        self.main_ui.pbt_serialOpen.clicked.connect(self.portOpen)
        self.portOpened = False

        # show window
        self.window.show()

    def portScan(self):
        portList = SerialPort.getDeviceList()
        self.main_ui.combox_serialPortList.clear()
        for portInfo, port in portList:
            self.main_ui.combox_serialPortList.addItem(portInfo, port)

    def portSelect(self):
        self.port = self.main_ui.combox_serialPortList.currentData()
        self.baudrate = self.main_ui.spinBox_baudrate.value()

    def portOpen(self):
        if self.portOpened == False:
            try:
                self.serial = SerialPort(self.port, self.baudrate)
                self.portOpened = True
                self.main_ui.pbt_serialOpen.setText('Close')
                self.imageModeWindow.addSendMethod(self.serial)
                self.videoModeWindow.addSendMethod(self.serial)
                self.screenModeWindow.addSendMethod(self.serial)
            except Exception:
                print('Serial port open false.')
        else:
            try:
                self.serial.close()
                self.serial = None
                self.portOpened = False
                self.main_ui.pbt_serialOpen.setText('Open')
                self.imageModeWindow.addSendMethod(None)
            except Exception:
                print('Serial port close false.')

    def exit(self):
        if self.portOpened:
            self.serial.close()
        self.imageModeWindow.exit()
        self.videoModeWindow.exit()
        self.screenModeWindow.exit()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec_())

    window.exit()
