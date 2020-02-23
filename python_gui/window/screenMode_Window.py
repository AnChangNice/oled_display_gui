
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore

from image_processing.Qt2CV import OpenCVImage2QPixMap
from window.screenSample_Window import ScreenSampleWindow
from image_processing.image_translate import ImageTranslate, OutputImagesStructure


class ScreenModeWindow(object):

    def __init__(self, window, main_ui):
        self.main_ui = main_ui
        self.window = window

        # sample window
        self.sample_window = ScreenSampleWindow()
        self.sample_window.setWindowOpacity(0.01)
        self.sample_window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.sample_window.resize(800, 600)

        # init image translator
        self.image_translator = ImageTranslate()
        self.images = OutputImagesStructure()
        self.screen_image = None
        h = self.main_ui.label_screenPreviewWindow.height()
        w = self.main_ui.label_screenPreviewWindow.width()
        self.image_translator.set_preview_size(w, h)
        self.image_translator.start()

        # init signal and slot
        self.init_signal()

        # serial send method
        self.sendMethod = None

        # timer
        self.drawRectTimer = QTimer(self.window)
        self.drawRectTimer.setTimerType(0)
        self.drawRectTimer.timeout.connect(self.sampleWindowUpdate)

        self.screenShotTimer = QTimer(self.window)
        self.screenShotTimer.setTimerType(0)
        self.screenShotTimer.timeout.connect(self.screenImageGet)

    def init_signal(self):
        # connect signal and slot
        # tab widget
        self.main_ui.tabWidget.currentChanged.connect(self.tab_changed)
        # pop sample button
        self.main_ui.pbt_screenSampleWindow.clicked.connect(self.openSampleWindow)
        self.main_ui.checkBox_sampleWindowShowOnTop.clicked.connect(self.sampleWindowShowMode)
        # Threshold value
        self.main_ui.spinBox_screenBWThreshold.valueChanged['int'].connect(self.main_ui.horizontalSlider_screenBWThreshold.setValue)
        self.main_ui.horizontalSlider_screenBWThreshold.valueChanged['int'].connect(self.main_ui.spinBox_screenBWThreshold.setValue)
        self.videoBWThresholdValue = 127
        self.main_ui.spinBox_screenBWThreshold.valueChanged.connect(self.BWThresholdValueUpdate)
        self.previewBWSize = '2X'
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
        self.main_ui.pbt_screenStartSending.clicked.connect(self.sendModeUpdate)
        self.screenSending = False

        self.setScreenWidgetEnable(False)

        # init tab and install image mode callback for image translator
        self.tab_changed()

    """
        There only one image translator instance, so we must install the current callback when mode is changed.
    """
    def tab_changed(self):
        index = self.main_ui.tabWidget.currentIndex()
        tab_name = self.main_ui.tabWidget.tabText(index)
        print(tab_name)
        if tab_name == 'Screen':
            self.image_translator.output_clean()
            self.image_translator.install_complete_callback(self.image_process_complete)

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

    def openSampleWindow(self):
        if self.sample_window.isHidden():
            self.setScreenWidgetEnable(True)
            self.main_ui.checkBox_sampleWindowShowOnTop.setEnabled(False)
            self.sample_window.show()
            self.drawRectTimer.start(30)
            self.screenShotTimer.start(10)
        else:
            self.setScreenWidgetEnable(False)
            self.main_ui.checkBox_sampleWindowShowOnTop.setEnabled(True)
            if self.screenSending:
                self.sendModeUpdate()
            self.sample_window.hide()
            self.drawRectTimer.stop()
            self.screenShotTimer.stop()

    def sampleWindowShowMode(self):
        if self.main_ui.checkBox_sampleWindowShowOnTop.isChecked():
            self.sample_window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.sample_window.setWindowFlags(QtCore.Qt.Widget)

    def sampleWindowUpdate(self):
        if self.sample_window.isHidden():
            self.drawRectTimer.stop()
            return None
        self.sample_window.draw_rect()

    def screenImageGet(self):
        self.screen_image = self.sample_window.get_window_image()
        self.image_translator.input_image(self.screen_image)
        if self.screenSending:
            self.updatePreview()
            self.updateBWPreview()
            self.send(self.images.bytes)

    def BWThresholdValueUpdate(self):
        threshold = self.main_ui.spinBox_screenBWThreshold.value()
        self.image_translator.set_threshold(threshold)
        if not self.screenSending:
            self.image_translator.input_image(self.screen_image)

    def previewBWSizeUpdate(self):
        if self.main_ui.checkBox_screenPreviewBW2x.isChecked():
            self.previewBWSize = '2X'
        else:
            self.previewBWSize = '1X'

        self.updateBWPreview()

    def BWInvertUpdate(self):
        if self.main_ui.checkBox_screenBWInvert.isChecked():
            self.image_translator.set_invert(True)
        else:
            self.image_translator.set_invert(False)

        if not self.screenSending:
            self.image_translator.input_image(self.screen_image)

    def previewModeUpdate(self):
        if self.main_ui.radioButton_screenPreviewRaw.isChecked():
            self.previewMode = 'raw'
        elif self.main_ui.radioButton_screenPreviewGray.isChecked():
            self.previewMode = 'gray'
        else:
            self.previewMode = 'bw'

        self.updatePreview()

    def updatePreview(self):
        # update preview
        if self.previewMode == 'raw':
            image = self.images.raw
        elif self.previewMode == 'gray':
            image = self.images.gray
        else:
            image = self.images.bw

        image_pix = OpenCVImage2QPixMap(image)
        self.main_ui.label_screenPreviewWindow.setPixmap(QPixmap.fromImage(image_pix))

    def updateBWPreview(self):
        if self.previewBWSize == '2X':
            image = self.images.output_bw2x
        else:
            image = self.images.output_bw

        image_pix = OpenCVImage2QPixMap(image)
        self.main_ui.label_screenPreviewOutputBW.setPixmap(QPixmap.fromImage(image_pix))

    def image_process_complete(self, images_queue):
        count = images_queue.qsize()
        for i in range(count):
            self.images = images_queue.get()

        if not self.screenSending:
            self.updatePreview()
            self.updateBWPreview()

    def sendModeUpdate(self):
        if self.screenSending:
            self.screenSending = False
            self.main_ui.pbt_screenStartSending.setText('Start Sending')
            self.screenShotTimer.setInterval(10)
        else:
            self.screenSending = True
            self.main_ui.pbt_screenStartSending.setText('Stop Sending')
            fps = self.main_ui.spinBox_screenSendFramerate.value()
            self.screenShotTimer.setInterval(int(1000/fps))

    def addSendMethod(self, sendMethod):
        self.sendMethod = sendMethod

    def send(self, data):
        if self.sendMethod != None:
            self.sendMethod.send(data)

    def exit(self):
        # self.sample_window.close()
        # self.sample_window.destroy()
        self.screenShotTimer.stop()
        self.drawRectTimer.stop()