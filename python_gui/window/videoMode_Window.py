
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer

from os import path
import time
from image_processing.Qt2CV import OpenCVImage2QPixMap
import cv2 as cv
from image_processing.image_translate import ImageTranslate, OutputImagesStructure

class VideoModeWindow(object):

    def __init__(self, window, main_ui):
        self.main_ui = main_ui
        self.window = window

        # init image translator
        self.image_translator = ImageTranslate()
        self.image_translator.start()
        self.images = OutputImagesStructure()
        self.video = None
        self.video_frame = None
        self.video_frame_index = 0
        self.video_frames = 0

        # init signal and slot
        self.init_signal()

        # send method
        self.sendMethod = None

        # timer
        self.timer = QTimer(self.window)
        self.timer.setTimerType(0)  # Precise timers try to keep millisecond accuracy
        self.timer.timeout.connect(self.videoSendProcess)

    def init_signal(self):
        # connect signal and slot
        # tab widget
        self.main_ui.tabWidget.currentChanged.connect(self.tab_changed)
        # Threshold value
        self.main_ui.spinBox_videoBWThreshold.valueChanged['int'].connect(self.main_ui.horizontalSlider_videoBWThreshold.setValue)
        self.main_ui.horizontalSlider_videoBWThreshold.valueChanged['int'].connect(self.main_ui.spinBox_videoBWThreshold.setValue)
        self.videoBWThresholdValue = 127
        self.main_ui.spinBox_videoBWThreshold.valueChanged.connect(self.videoBWThresholdValueUpdate)
        self.videoPreviewBWSize = '2X'
        self.main_ui.checkBox_videoPreviewBW2x.clicked.connect(self.previewBWSizeUpdate)
        # import image
        self.main_ui.pbt_videoOpenFile.clicked.connect(self.openVideo)
        self.lastFolderPath = ''
        # BM invert
        self.main_ui.checkBox_videoBWInvert.clicked.connect(self.BWInvertUpdate)
        self.videoBWInvert = False
        # preview mode
        self.main_ui.radioButton_videoPreviewRaw.clicked.connect(self.previewModeUpdate)
        self.main_ui.radioButton_videoPreviewGray.clicked.connect(self.previewModeUpdate)
        self.main_ui.radioButton_videoPreviewBW.clicked.connect(self.previewModeUpdate)
        self.previewMode = 'raw'
        self.main_ui.horizontalSlider_videoPreviewFrameOffset.valueChanged.connect(self.previewSilderUpdate)
        self.main_ui.horizontalSlider_videoPreviewFrameOffset.valueChanged['int'].connect(self.main_ui.spinBox_videoFrameOffset.setValue)
        self.main_ui.spinBox_videoFrameOffset.valueChanged['int'].connect(self.main_ui.horizontalSlider_videoPreviewFrameOffset.setValue)

        # send to OLED
        self.main_ui.pbt_videoStartSending.clicked.connect(self.videoSendStateUpdate)
        self.videoSendFramerate = 1
        self.videoSending = False

        # disable widget before import video file
        self.setPreviewSliderAndSpinboxEnable(False)
        self.setVideoWidgetEnable(False)

        # init tab and install image mode callback for image translator
        self.tab_changed()

    """
        There only one image translator instance, so we must install the current callback when mode is changed.
    """
    def tab_changed(self):
        index = self.main_ui.tabWidget.currentIndex()
        tab_name = self.main_ui.tabWidget.tabText(index)
        print(tab_name)
        if tab_name == 'Video':
            self.image_translator.output_clean()
            self.image_translator.install_complete_callback(self.image_translate_complete)

    def setPreviewSliderAndSpinboxEnable(self, enable):
        self.main_ui.horizontalSlider_videoPreviewFrameOffset.setEnabled(enable)
        self.main_ui.spinBox_videoFrameOffset.setEnabled(enable)
        self.main_ui.spinBox_videoSendFramerate.setEnabled(enable)

    def setVideoWidgetEnable(self, enable):
        self.main_ui.spinBox_videoBWThreshold.setEnabled(enable)
        self.main_ui.horizontalSlider_videoBWThreshold.setEnabled(enable)
        self.main_ui.checkBox_videoBWInvert.setEnabled(enable)
        self.main_ui.checkBox_videoPreviewBW2x.setEnabled(enable)

        self.main_ui.radioButton_videoPreviewRaw.setEnabled(enable)
        self.main_ui.radioButton_videoPreviewGray.setEnabled(enable)
        self.main_ui.radioButton_videoPreviewBW.setEnabled(enable)

        self.main_ui.pbt_videoStartSending.setEnabled(enable)

    def openVideo(self):
        filename, filetype = QFileDialog.getOpenFileName(self.window, 'Select a video file', self.lastFolderPath)
        if filename != '':
            self.lastFolderPath = path.dirname(filename)
            self.main_ui.lineEdit_videoFileName.setText(filename)
            # self.video.open(filename)
            self.video = cv.VideoCapture(filename)

            # get video info
            fps = int(self.video.get(cv.CAP_PROP_FPS))
            self.video_frames = int(self.video.get(cv.CAP_PROP_FRAME_COUNT))
            # update ui
            self.main_ui.lineEdit_videoInfoFramerate.setText('%d' % fps)
            self.main_ui.lineEdit_videoInfoDuration.setText('%d|%.1f' % (self.video_frames, self.video_frames / fps))
            self.main_ui.horizontalSlider_videoPreviewFrameOffset.setMinimum(0)
            self.main_ui.horizontalSlider_videoPreviewFrameOffset.setMaximum(self.video_frames-1)
            self.main_ui.spinBox_videoFrameOffset.setMinimum(0)
            self.main_ui.spinBox_videoFrameOffset.setMaximum(self.video_frames-1)
            self.main_ui.horizontalSlider_videoPreviewFrameOffset.setSliderPosition(0)

            self.setPreviewSliderAndSpinboxEnable(True)
            self.setVideoWidgetEnable(True)

            # translate first frame
            ret, self.video_frame = self.video.read()
            h, w, n = self.video_frame.shape
            k = w / h
            height = self.main_ui.label_videoPreviewWindow.height()
            width = int(k * height) - 1
            self.image_translator.set_preview_size(width, height)
            self.image_translator.input_image(self.video_frame)

    def videoBWThresholdValueUpdate(self):
        threshold = self.main_ui.spinBox_videoBWThreshold.value()

        self.image_translator.set_threshold(threshold)
        if not self.videoSending:
            self.image_translator.input_image(self.video_frame)

    def previewBWSizeUpdate(self):
        if self.main_ui.checkBox_videoPreviewBW2x.isChecked():
            self.videoPreviewBWSize = '2X'
        else:
            self.videoPreviewBWSize = '1X'

        self.updateBWPreview()

    def BWInvertUpdate(self):
        if self.main_ui.checkBox_videoBWInvert.isChecked():
            self.image_translator.set_invert(True)
        else:
            self.image_translator.set_invert(False)

        if not self.videoSending:
            self.image_translator.input_image(self.video_frame)

    def previewModeUpdate(self):
        if self.main_ui.radioButton_videoPreviewRaw.isChecked():
            self.previewMode = 'raw'
        elif self.main_ui.radioButton_videoPreviewGray.isChecked():
            self.previewMode = 'gray'
        else:
            self.previewMode = 'BW'

        self.updatePreview()

    def previewSilderUpdate(self):
        if self.videoSending:
            return None
        # get current slider value
        index = self.main_ui.horizontalSlider_videoPreviewFrameOffset.value()
        # read frame specified
        self.video.set(cv.CAP_PROP_POS_FRAMES, index)
        ret, self.video_frame = self.video.read()
        self.image_translator.input_image(self.video_frame)

    def updatePreview(self):
        # update preview
        if self.previewMode == 'raw':
            image = self.images.raw
        elif self.previewMode == 'gray':
            image = self.images.gray
        else:
            image = self.images.bw
        image_pix = OpenCVImage2QPixMap(image)
        self.main_ui.label_videoPreviewWindow.setPixmap(QPixmap.fromImage(image_pix))

    def updateBWPreview(self):
        if self.videoPreviewBWSize == '2X':
            image = self.images.output_bw2x
        else:
            image = self.images.output_bw
        image_pix = OpenCVImage2QPixMap(image)
        self.main_ui.label_videoPreviewOutputBW.setPixmap(QPixmap.fromImage(image_pix))

    def videoSendStateUpdate(self):
        if self.videoSending:
            self.videoSending = False
            self.setPreviewSliderAndSpinboxEnable(True)
            self.main_ui.pbt_videoStartSending.setText('Start Sending')
            self.timer.stop()
            self.image_translator.output_clean()

        else:
            self.videoSending = True
            self.setPreviewSliderAndSpinboxEnable(False)
            self.main_ui.pbt_videoStartSending.setText('Stop Sending')
            fps = self.main_ui.spinBox_videoSendFramerate.value()
            self.timer.start(int(1000/fps))

    def videoSendProcess(self):
        # read next frame
        ret, self.video_frame = self.video.read()
        self.image_translator.input_image(self.video_frame)
        # update last frame
        self.updatePreview()
        self.updateBWPreview()
        # send to serial
        self.send(self.images.bytes)
        # update frame index ui
        index = int(self.video.get(cv.CAP_PROP_POS_FRAMES))
        self.main_ui.spinBox_videoFrameOffset.setValue(index)
        # check if video reach the end
        if index >= self.video_frames-1:
            self.videoSendStateUpdate()

    def image_translate_complete(self, images_queue):
        count = images_queue.qsize()
        for i in range(count):
            self.images = images_queue.get()
        # self.images = images_queue.get()

        if not self.videoSending:
            self.updatePreview()
            self.updateBWPreview()

    def addSendMethod(self, sendMethod):
        self.sendMethod = sendMethod

    def send(self, data):
        if self.sendMethod != None:
            self.sendMethod.send(data)

    def exit(self):
        pass