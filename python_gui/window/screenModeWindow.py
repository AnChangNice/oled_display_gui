
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore

import time
from image_processing.Qt2CV import OpenCVImage2QPixMap
from screen import ScreenDraw, ScreenGet
from image_process import ImageStreamProcess

from window.screenSampleWindow import ScreenSampleWindow

class ScreenModeWindow(object):

    def __init__(self, window, main_ui):
        self.main_ui = main_ui
        self.window = window

        # init signal and slot
        self.init_signal()

        self.sendMethod = None

        # sample window
        self.sample_window = ScreenSampleWindow()

        self.sample_window.setWindowOpacity(0.01)
        self.sample_window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.sample_window.resize(800, 600)

        self.screen = ScreenDraw()
        self.screen.setPenColor(255, 0, 0)
        self.screenShot = ScreenGet()

        # image process
        self.imageProcess = ImageStreamProcess()
        h = self.main_ui.label_screenPreviewWindow.height()
        w = self.main_ui.label_screenPreviewWindow.width()
        self.imageProcess.setPreviewSize(w, h)
        self.imageProcess.start()

        # timer
        self.drawRectTimer = QTimer(self.window)
        self.drawRectTimer.timeout.connect(self.sampleWindowUpdate)

        self.previewTimer = QTimer(self.window)
        self.previewTimer.timeout.connect(self.updateAllPreview)

        self.lastTimeStamp = time.time()

    def init_signal(self):
        # connect signal and slot
        # pop sample button
        self.main_ui.pbt_screenSampleWindow.clicked.connect(self.popSampleWindowUpdate)
        self.main_ui.checkBox_sampleWindowShowOnTop.clicked.connect(self.sampleWindowShowMode)

        # Threshold value
        self.main_ui.spinBox_screenBWThreshold.valueChanged['int'].connect(self.main_ui.horizontalSlider_screenBWThreshold.setValue)
        self.main_ui.horizontalSlider_screenBWThreshold.valueChanged['int'].connect(self.main_ui.spinBox_screenBWThreshold.setValue)
        self.videoBWThresholdValue = 127
        self.main_ui.spinBox_screenBWThreshold.valueChanged.connect(self.screenBWThresholdValueUpdate)
        self.screenPreviewBWSize = '256*128'
        self.main_ui.checkBox_screenPreviewBW2x.clicked.connect(self.previewBWSizeUpdate)

        # BM invert
        self.main_ui.checkBox_screenBWInvert.clicked.connect(self.BWInvertUpdate)
        self.screenBWInvert = False

        # preview mode
        self.main_ui.radioButton_screenPreviewRaw.clicked.connect(self.previewModeUpdate)
        self.main_ui.radioButton_screenPreviewGray.clicked.connect(self.previewModeUpdate)
        self.main_ui.radioButton_screenPreviewBW.clicked.connect(self.previewModeUpdate)
        self.previewMode = 'raw'

        # send frame signal
        self.main_ui.pbt_screenStartSending.clicked.connect(self.screenSendUpdate)
        self.screenSending = False

        self.setScreenWidgetEnable(False)

    def setScreenWidgetEnable(self, enable):
        self.main_ui.spinBox_screenBWThreshold.setEnabled(enable)
        self.main_ui.horizontalSlider_screenBWThreshold.setEnabled(enable)
        self.main_ui.checkBox_screenBWInvert.setEnabled(enable)
        self.main_ui.checkBox_screenPreviewBW2x.setEnabled(enable)

        self.main_ui.radioButton_screenPreviewRaw.setEnabled(enable)
        self.main_ui.radioButton_screenPreviewGray.setEnabled(enable)
        self.main_ui.radioButton_screenPreviewBW.setEnabled(enable)

        self.main_ui.pbt_screenStartSending.setEnabled(enable)

        if enable == True:
            self.main_ui.pbt_screenSampleWindow.setText('Close Sample Window')
        else:
            self.main_ui.pbt_screenSampleWindow.setText('Open Sample Window')

    def popSampleWindowUpdate(self):
        if self.sample_window.isHidden():
            self.setScreenWidgetEnable(True)
            self.main_ui.checkBox_sampleWindowShowOnTop.setEnabled(False)
            self.sample_window.show()
            framerate_timeout = int(1000 / self.main_ui.spinBox_screenSendFramerate.value())
            self.previewTimer.start(framerate_timeout)
            self.drawRectTimer.start(30)
        else:
            self.setScreenWidgetEnable(False)
            self.main_ui.checkBox_sampleWindowShowOnTop.setEnabled(True)
            if self.screenSending:
                self.screenSendUpdate()
            self.sample_window.hide()
            self.drawRectTimer.stop()
            self.previewTimer.stop()

    def sampleWindowShowMode(self):
        if self.main_ui.checkBox_sampleWindowShowOnTop.isChecked():
            self.sample_window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.sample_window.setWindowFlags(QtCore.Qt.Widget)

    def sampleWindowUpdate(self):
        if self.sample_window.isHidden():
            self.drawRectTimer.stop()
            self.previewTimer.stop()
            return None
        self.sample_window.draw_rect()

    def screenBWThresholdValueUpdate(self):
        self.screenBWThresholdValue = self.main_ui.spinBox_screenBWThreshold.value()
        self.imageProcess.setBWThreshold(value=self.screenBWThresholdValue)

        if not self.previewTimer.isActive():
            self.imageProcess.requestFrame(self.image)
            self.previewTimer.setSingleShot(True)
            self.previewTimer.start(50)

    def previewBWSizeUpdate(self):
        if self.main_ui.checkBox_screenPreviewBW2x.isChecked():
            self.screenPreviewBWSize = '256*128'
        else:
            self.screenPreviewBWSize = '128*64'

        if not self.previewTimer.isActive():
            self.imageProcess.requestFrame(self.image)
            self.previewTimer.setSingleShot(True)
            self.previewTimer.start(50)

    def BWInvertUpdate(self):
        if self.main_ui.checkBox_screenBWInvert.isChecked():
            self.imageProcess.setBWThreshold(invert=True)
        else:
            self.imageProcess.setBWThreshold(invert=False)

        if not self.previewTimer.isActive():
            self.imageProcess.requestFrame(self.image)
            self.previewTimer.setSingleShot(True)
            self.previewTimer.start(50)

    def previewModeUpdate(self):
        if self.main_ui.radioButton_screenPreviewRaw.isChecked():
            self.previewMode = 'raw'
        elif self.main_ui.radioButton_screenPreviewGray.isChecked():
            self.previewMode = 'gray'
        else:
            self.previewMode = 'BW'

        if not self.previewTimer.isActive():
            self.imageProcess.requestFrame(self.image)
            self.previewTimer.setSingleShot(True)
            self.previewTimer.start(50)

    def updatePreview(self):
        # update preview
        if self.previewMode == 'raw':
            image = self.image_raw
        elif self.previewMode == 'gray':
            image = self.image_gray
        else:
            image = self.image_bw
        image_pix = OpenCVImage2QPixMap(image)
        self.main_ui.label_screenPreviewWindow.setPixmap(QPixmap.fromImage(image_pix))

    def updateBWPreview(self):
        if self.screenPreviewBWSize == '256*128':
            image = self.image_out_bw2x
        else:
            image = self.image_out_bw
        image_pix = OpenCVImage2QPixMap(image)
        self.main_ui.label_screenPreviewOutputBW.setPixmap(QPixmap.fromImage(image_pix))

    def updateAllPreview(self):
        if self.readAllImages():
            self.updatePreview()
            self.updateBWPreview()
            if self.screenSending:
                self.send(self.image_data_frame)
            self.image = self.sample_window.get_window_image()
            self.imageProcess.requestFrame(self.image)
        else:
            self.image = self.sample_window.get_window_image()
            self.imageProcess.requestFrame(self.image)

    def readAllImages(self):
        result = self.imageProcess.readFrames()
        if result != None:
            self.image_raw, self.image_gray, self.image_bw, self.image_out_bw, self.image_out_bw2x, self.image_data_frame = result
            return True
        else:
            return False

    def screenSendUpdate(self):
        if self.screenSending:
            self.screenSending = False
            self.main_ui.pbt_screenStartSending.setText('Start Sending')
        else:
            self.screenSending = True
            self.main_ui.pbt_screenStartSending.setText('Stop Sending')

    def addSendMethod(self, sendMethod):
        self.sendMethod = sendMethod

    def send(self, data):
        if self.sendMethod != None:
            self.sendMethod.send(data)

    def exit(self):
        self.imageProcess.stop()