
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5.QtGui import QPixmap

from os import path
import cv2 as cv
import numpy as np
from image_processing.Qt2CV import OpenCVImage2QPixMap
from UI.image_export_ui import Ui_imageExportWindow
from image_processing.image_translate import ImageTranslate, OutputImagesStructure

class ImageModeWindow(object):

    def __init__(self, window, main_ui):
        self.main_ui = main_ui
        self.window = window

        # export window
        self.export_window = QWidget()
        self.init_export_window(self.export_window)

        # init image translator
        self.image_translator = ImageTranslate()
        self.image_translator.start()
        self.images = OutputImagesStructure()

        # init signal and slot
        self.init_signal()

        self.sendMethod = None

    def init_export_window(self, window):
        self.imageExport_ui = Ui_imageExportWindow()
        self.imageExport_ui.setupUi(window)
        self.imageExport_ui.retranslateUi(window)

    def init_signal(self):
        # connect signal and slot
        # tab widget
        self.main_ui.tabWidget.currentChanged.connect(self.tab_changed)
        # Threshold value
        self.main_ui.spinBox_BWThreshold.valueChanged['int'].connect(self.main_ui.horizontalSlider_BWThreshold.setValue)
        self.main_ui.horizontalSlider_BWThreshold.valueChanged['int'].connect(self.main_ui.spinBox_BWThreshold.setValue)
        self.main_ui.horizontalSlider_BWThreshold.valueChanged.connect(self.BWThresholdValueUpdate)
        self.previewBWSize = '2X'
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
        self.setImageWidgetEnable(False)

        # init tab and install image mode callback for image translator
        self.tab_changed()

    """
        There only one image translator instance, so we must install the current callback when mode is changed.
    """
    def tab_changed(self):
        index = self.main_ui.tabWidget.currentIndex()
        tab_name = self.main_ui.tabWidget.tabText(index)
        if tab_name == 'Image':
            self.image_translator.output_clean()
            self.image_translator.install_complete_callback(self.image_process_complete)

    def setImageWidgetEnable(self, enable):
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
            self.image_raw = cv.imread(filename)
            self.setImageWidgetEnable(True)
            h, w, n = self.image_raw.shape
            k = w / h
            height = self.main_ui.label_previewWindow.height()
            width = int(k * height) - 1
            self.image_translator.set_preview_size(width, height)
            self.image_translator.input_image(self.image_raw)

    def imageSendModeUpdate(self):
        if self.main_ui.radioButton_sendImageManually.isChecked():
            self.imageSendMode = 'Manually'
        else:
            self.imageSendMode = 'Auto'

    def BWThresholdValueUpdate(self):
        thresholdValue = self.main_ui.spinBox_BWThreshold.value()
        self.image_translator.set_threshold(thresholdValue)
        self.image_translator.input_image(self.image_raw)

    def previewBWSizeUpdate(self):
        if self.main_ui.checkBox_previewBW2x.isChecked():
            self.previewBWSize = '2X'
        else:
            self.previewBWSize = '1X'
        self.updateBWPreview()

    def exportModeUpdate(self):
        if self.main_ui.radioButton_exportHexCArray.isChecked():
            self.exportMode = 'HexCArray'
        else:
            self.exportMode = 'HexValue'

    def exportImage(self):
        image_bytes = self.images.bytes
        # export
        out_str = ''
        if self.exportMode == 'HexCArray':
            out_str += 'uint8_t bitmap[] = {\n'
            out_hex_nums = ['0x%02x' % x for x in image_bytes]
            numbers_per_line = 32
            for i in range(int(1024 / numbers_per_line)):
                index = i * numbers_per_line
                out_str += '    %s,\n' % (', '.join(out_hex_nums[index:(index + numbers_per_line)]))
            out_str += '};\n'
        else:
            out_hex_nums = ['%02x' % x for x in image_bytes]
            out_str += ' '.join(out_hex_nums)

        self.imageExport_ui.textEdit_eportEditor.setText(out_str)
        self.export_window.show()


    def BWInvertUpdate(self):
        if self.main_ui.checkBox_BWInvert.isChecked():
            self.BWInvert = True
        else:
            self.BWInvert = False
        self.image_translator.set_invert(self.BWInvert)
        self.image_translator.input_image(self.image_raw)

    def previewModeUpdate(self):
        if self.main_ui.radioButton_previewRaw.isChecked():
            self.previewMode = 'raw'
        elif self.main_ui.radioButton_previewGray.isChecked():
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
        self.main_ui.label_previewWindow.setPixmap(QPixmap.fromImage(image_pix))

    def updateBWPreview(self):
        # update BW preview
        if self.previewBWSize == '2X':
            image = self.images.output_bw2x
        else:
            image = self.images.output_bw

        image_pix = OpenCVImage2QPixMap(image)
        self.main_ui.label_previewOutputBW.setPixmap(QPixmap.fromImage(image_pix))

        # send to display
        if self.imageSendMode == 'Auto':
            self.send(self.images.bytes)

    def sendManually(self):
        self.send(self.images.bytes)

    def addSendMethod(self, sendMethod):
        self.sendMethod = sendMethod

    def image_process_complete(self, images_queue):
        count = images_queue.qsize()
        for i in range(count):
            self.images = images_queue.get()

        self.updatePreview()
        self.updateBWPreview()

    def send(self, data):
        if self.sendMethod != None:
            self.sendMethod.send(data)

    def exit(self):
        pass