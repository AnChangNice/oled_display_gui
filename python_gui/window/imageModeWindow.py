
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5.QtGui import QPixmap

from os import path
import cv2 as cv
import numpy as np
from image_processing.Qt2CV import OpenCVImage2QPixMap
from image_processing.image_to_oled import re_sample
from UI.image_export_ui import Ui_imageExportWindow

class ImageModeWindow(object):

    def __init__(self, window, main_ui):
        self.main_ui = main_ui
        self.window = window

        # init signal and slot
        self.init_signal()

        # export window
        self.export_window = QWidget()
        self.init_export_window(self.export_window)

        self.sendMethod = None

    def init_export_window(self, window):
        self.imageExport_ui = Ui_imageExportWindow()
        self.imageExport_ui.setupUi(window)
        self.imageExport_ui.retranslateUi(window)

    def init_signal(self):
        # connect signal and slot
        # Threshold value
        self.main_ui.spinBox_BWThreshold.valueChanged['int'].connect(self.main_ui.horizontalSlider_BWThreshold.setValue)
        self.main_ui.horizontalSlider_BWThreshold.valueChanged['int'].connect(self.main_ui.spinBox_BWThreshold.setValue)
        self.BWThresholdValue = 127
        self.main_ui.spinBox_BWThreshold.valueChanged.connect(self.BWThresholdValueUpdate)
        self.previewBWSize = '256*128'
        self.main_ui.checkBox_previewBW2x.clicked.connect(self.previewBWSizeUpdate)
        # import image
        self.main_ui.pbt_openImageFile.clicked.connect(self.openImage)
        self.lastFolderPath = ''
        # BM invert
        self.main_ui.checkBox_BWInvert.clicked.connect(self.BWInvertUpdate)
        self.BWInvert = False
        # preview mode
        self.main_ui.radioButton_previewRaw.clicked.connect(self.previewModeUpdate)
        self.main_ui.radioButton_previewGray.clicked.connect(self.previewModeUpdate)
        self.main_ui.radioButton_previewBW.clicked.connect(self.previewModeUpdate)
        self.previewMode = 'raw'
        # export mode
        self.main_ui.radioButton_exportHexCArray.clicked.connect(self.exportModeUpdate)
        self.main_ui.radioButton_exportHexValue.clicked.connect(self.exportModeUpdate)
        self.exportMode = 'HexCArray'
        self.main_ui.pbt_exportImage.clicked.connect(self.exportImage)
        # send to OLED
        self.main_ui.radioButton_SendImageAuto.clicked.connect(self.imageSendModeUpdate)
        self.main_ui.radioButton_sendImageManually.clicked.connect(self.imageSendModeUpdate)
        self.imageSendMode = 'Manually'
        self.main_ui.pbt_sendImage.clicked.connect(self.sendManually)

        # disable
        self.setVideoWidgetEnable(False)

    def setVideoWidgetEnable(self, enable):
        self.main_ui.radioButton_previewRaw.setEnabled(enable)
        self.main_ui.radioButton_previewGray.setEnabled(enable)
        self.main_ui.radioButton_previewBW.setEnabled(enable)

        self.main_ui.spinBox_BWThreshold.setEnabled(enable)
        self.main_ui.horizontalSlider_BWThreshold.setEnabled(enable)

        self.main_ui.checkBox_BWInvert.setEnabled(enable)
        self.main_ui.checkBox_previewBW2x.setEnabled(enable)
        self.main_ui.pbt_exportImage.setEnabled(enable)

        self.main_ui.radioButton_SendImageAuto.setEnabled(enable)
        self.main_ui.pbt_sendImage.setEnabled(enable)

    def openImage(self):
        filename, filetype = QFileDialog.getOpenFileName(self.window, 'Select a image file', self.lastFolderPath)
        if filename != '':
            self.lastFolderPath = path.dirname(filename)
            self.main_ui.lineEdit_imageFileName.setText(filename)
            self.imageRaw = cv.imread(filename)
            self.updatePreview()
            self.updateBWPreview()
            self.setVideoWidgetEnable(True)

    def imageSendModeUpdate(self):
        if self.main_ui.radioButton_sendImageManually.isChecked():
            self.imageSendMode = 'Manually'
        else:
            self.imageSendMode = 'Auto'

    def imageSend(self):
        print(self.imageSendMode)

    def BWThresholdValueUpdate(self):
        self.BWThresholdValue = self.main_ui.spinBox_BWThreshold.value()
        self.updatePreview()
        self.updateBWPreview()

    def previewBWSizeUpdate(self):
        if self.main_ui.checkBox_previewBW2x.isChecked():
            self.previewBWSize = '256*128'
        else:
            self.previewBWSize = '128*64'
        self.updateBWPreview()

    def exportModeUpdate(self):
        if self.main_ui.radioButton_exportHexCArray.isChecked():
            self.exportMode = 'HexCArray'
        else:
            self.exportMode = 'HexValue'

    def exportImage(self):
        image_raw = self.imageRaw
        image_gray = cv.cvtColor(image_raw, cv.COLOR_BGR2GRAY)
        if self.BWInvert == True:
            image_bw = (image_gray < self.BWThresholdValue) * np.uint8(255)
        else:
            image_bw = (image_gray >= self.BWThresholdValue) * np.uint8(255)
        image = cv.resize(image_bw, (128, 64))
        image_frame = re_sample(image)
        # export
        out_str = ''
        if self.exportMode == 'HexCArray':
            out_str += 'uint8_t bitmap[] = {\n'
            out_hex_nums = ['0x%02x' % x for x in image_frame]
            numbers_per_line = 32
            for i in range(int(1024 / numbers_per_line)):
                index = i * numbers_per_line
                out_str += '    %s,\n' % (', '.join(out_hex_nums[index:(index + numbers_per_line)]))
            out_str += '};\n'
        else:
            out_hex_nums = ['%02x' % x for x in image_frame]
            out_str += ' '.join(out_hex_nums)

        self.imageExport_ui.textEdit_eportEditor.setText(out_str)
        self.export_window.show()


    def BWInvertUpdate(self):
        if self.main_ui.checkBox_BWInvert.isChecked():
            self.BWInvert = True
        else:
            self.BWInvert = False
        self.updatePreview()
        self.updateBWPreview()

    def previewModeUpdate(self):
        if self.main_ui.radioButton_previewRaw.isChecked():
            self.previewMode = 'raw'
        elif self.main_ui.radioButton_previewGray.isChecked():
            self.previewMode = 'gray'
        else:
            self.previewMode = 'BW'
        self.updatePreview()
        self.updateBWPreview()

    def updatePreview(self):
        # update preview
        image_raw = self.imageRaw
        image_gray = cv.cvtColor(image_raw, cv.COLOR_BGR2GRAY)
        if self.BWInvert == True:
            image_bw = (image_gray < self.BWThresholdValue) * np.uint8(255)
        else:
            image_bw = (image_gray >= self.BWThresholdValue) * np.uint8(255)

        if self.previewMode == 'raw':
            image = image_raw
        elif self.previewMode == 'gray':
            image = image_gray
        else:
            image = image_bw
        h, w, n = self.imageRaw.shape
        k = w/h
        height = self.main_ui.label_previewWindow.height()
        width = int(k*height)-1
        image = cv.resize(image, (width, height))
        image_pix = OpenCVImage2QPixMap(image)
        self.main_ui.label_previewWindow.setPixmap(QPixmap.fromImage(image_pix))

    def updateBWPreview(self):
        image_raw = self.imageRaw
        image_gray = cv.cvtColor(image_raw, cv.COLOR_BGR2GRAY)
        if self.BWInvert == True:
            image_bw = (image_gray < self.BWThresholdValue) * np.uint8(255)
        else:
            image_bw = (image_gray >= self.BWThresholdValue) * np.uint8(255)
        # update BW preview
        if self.previewBWSize == '256*128':
            image = cv.resize(image_bw, (256, 128))
        else:
            image = cv.resize(image_bw, (128, 64))
        image_pix = OpenCVImage2QPixMap(image)
        self.main_ui.label_previewOutputBW.setPixmap(QPixmap.fromImage(image_pix))
        # send to display
        if self.imageSendMode == 'Auto':
            image = cv.resize(image_bw, (128, 64))
            image_frame = re_sample(image)
            self.send(image_frame)

    def sendManually(self):
        image_raw = self.imageRaw
        image_gray = cv.cvtColor(image_raw, cv.COLOR_BGR2GRAY)
        if self.BWInvert == True:
            image_bw = (image_gray < self.BWThresholdValue) * np.uint8(255)
        else:
            image_bw = (image_gray >= self.BWThresholdValue) * np.uint8(255)
        image = cv.resize(image_bw, (128, 64))
        image_frame = re_sample(image)
        self.send(image_frame)

    def addSendMethod(self, sendMethod):
        self.sendMethod = sendMethod

    def send(self, data):
        if self.sendMethod != None:
            self.sendMethod.send(data)

    def exit(self):
        pass