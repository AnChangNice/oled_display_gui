
from UI.main_ui import Ui_mainWindow
from window.imageMode_Window import ImageModeWindow
from window.videoMode_Window import VideoModeWindow
from window.screenMode_Window import ScreenModeWindow
from PyQt5.QtWidgets import QMainWindow

from serial_port import SerialPort
from image_processing.BWImageToBytes import BWImageToBytes
from image_processing.image_translate import ImageTranslate


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

        # BW image to bytes instance
        self.image_to_bw = BWImageToBytes()

        # image processing
        self.image_translator = ImageTranslate()
        self.image_translator.start()

        self.connectSignal()

        # show window
        self.window.show()

    def connectSignal(self):
        # connect serial port widgets
        self.main_ui.pbt_scanSerialPort.clicked.connect(self.portScan)
        self.main_ui.combox_serialPortList.activated.connect(self.portSelect)
        self.main_ui.pbt_serialOpen.clicked.connect(self.portOpen)
        self.portOpened = False
        # connect display setting
        self.main_ui.spinBox_displayRow.valueChanged.connect(self.displayColumnRowSetting)
        self.main_ui.spinBox_displayCol.valueChanged.connect(self.displayColumnRowSetting)
        self.main_ui.checkBox_displayFlipH.clicked.connect(self.displayFlipModeSetting)
        self.main_ui.checkBox_displayFlipV.clicked.connect(self.displayFlipModeSetting)
        self.main_ui.comboBox_displayScanDirection.activated.connect(self.displayScanDirectionSetting)
        self.main_ui.comboBox_displayByteDirection.activated.connect(self.displayByteDirectionSetting)
        self.main_ui.comboBox_displaySignBit.activated.connect(self.displaySignBitSetting)
        self.displaySettingInit()
        # connect binarization setting
        self.main_ui.radioButton_binarizationThreshold.clicked.connect(self.binarizationSetting)
        self.main_ui.radioButton_binarizationDither.clicked.connect(self.binarizationSetting)
        self.main_ui.comboBox_ditherBayerSize.activated.connect(self.binarizationSetting)
        self.binarizationSetting()

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

    def binarizationSetting(self):
        if self.main_ui.radioButton_binarizationThreshold.isChecked():
            self.image_translator.set_dither_enable(False)
        else:
            self.image_translator.set_dither_enable(True)
            size_str = self.main_ui.comboBox_ditherBayerSize.currentText()
            size = int(size_str[:-1])
            self.image_translator.set_dither_size(size)

    def displaySettingInit(self):
        self.displayColumnRowSetting()
        self.displayFlipModeSetting()
        self.displayScanDirectionSetting()
        self.displayByteDirectionSetting()
        self.displaySignBitSetting()

    def displayColumnRowSetting(self):
        col = self.main_ui.spinBox_displayCol.value()
        row = self.main_ui.spinBox_displayRow.value()
        self.image_translator.set_output_size(col, row)

    def displayFlipModeSetting(self):
        flip_h = self.main_ui.checkBox_displayFlipH.isChecked()
        flip_v = self.main_ui.checkBox_displayFlipV.isChecked()
        self.image_to_bw.setHorizontalFlip(flip_h)
        self.image_to_bw.setVerticalFlip(flip_v)

    def displayScanDirectionSetting(self):
        scan_direction = self.main_ui.comboBox_displayScanDirection.currentText()
        if scan_direction == 'Horizontal':
            dir = 'H'
        else:
            dir = 'V'
        self.image_to_bw.setScanDirection(dir)

    def displayByteDirectionSetting(self):
        byte_direction = self.main_ui.comboBox_displayByteDirection.currentText()
        if byte_direction == 'Horizontal':
            dir = 'H'
        else:
            dir = 'V'
        self.image_to_bw.setByteDirection(dir)

    def displaySignBitSetting(self):
        sign_bit = self.main_ui.comboBox_displaySignBit.currentText()
        self.image_to_bw.setSignBit(sign_bit)

    def exit(self):
        if self.portOpened:
            self.serial.close()
        self.imageModeWindow.exit()
        self.videoModeWindow.exit()
        self.screenModeWindow.exit()
        self.image_translator.stop()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec_())

    window.exit()
