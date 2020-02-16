
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer

from os import path
import time
from image_processing.Qt2CV import OpenCVImage2QPixMap
from video_process import VideoProcess

class VideoModeWindow(object):

    def __init__(self, window, main_ui):
        self.main_ui = main_ui
        self.window = window

        # init signal and slot
        self.init_signal()

        self.sendMethod = None
        self.video = VideoProcess()

        # timer
        self.timer = QTimer(self.window)
        self.timer.timeout.connect(self.videoSend)

        self.lastTimeStamp = time.time()

    def init_signal(self):
        # connect signal and slot
        # Threshold value
        self.main_ui.spinBox_videoBWThreshold.valueChanged['int'].connect(self.main_ui.horizontalSlider_videoBWThreshold.setValue)
        self.main_ui.horizontalSlider_videoBWThreshold.valueChanged['int'].connect(self.main_ui.spinBox_videoBWThreshold.setValue)
        self.videoBWThresholdValue = 127
        self.main_ui.spinBox_videoBWThreshold.valueChanged.connect(self.videoBWThresholdValueUpdate)
        self.videoPreviewBWSize = '256*128'
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

        self.currentFrameIndex = 0
        # send to OLED
        self.main_ui.pbt_videoStartSending.clicked.connect(self.videoSendStateUpdate)
        self.videoSendFramerate = 1
        self.videoSending = False

        # disable widget before import video file
        self.setPreviewSliderAndSpinboxEnable(False)
        self.setVideoWidgetEnable(False)

    def setPreviewSliderAndSpinboxEnable(self, enable):
        self.main_ui.horizontalSlider_videoPreviewFrameOffset.setEnabled(enable)
        self.main_ui.spinBox_videoFrameOffset.setEnabled(enable)

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
            self.video.open(filename)
            w = self.video.frameWidth
            h = self.video.frameHeight
            k = w / h
            height = self.main_ui.label_videoPreviewWindow.height()
            width = int(k * height) - 1
            self.video.setPreviewSize(width, height)
            self.video.requestFrame()
            self.main_ui.lineEdit_videoInfoFramerate.setText('%d' % (int(self.video.frameRate)))
            self.main_ui.lineEdit_videoInfoDuration.setText('%d|%.1f' % (int(self.video.frameCount), self.video.frameCount / self.video.frameRate))
            self.main_ui.horizontalSlider_videoPreviewFrameOffset.setMinimum(0)
            self.main_ui.horizontalSlider_videoPreviewFrameOffset.setMaximum(int(self.video.frameCount)-1)
            self.main_ui.spinBox_videoFrameOffset.setMinimum(0)
            self.main_ui.spinBox_videoFrameOffset.setMaximum(int(self.video.frameCount)-1)
            self.main_ui.horizontalSlider_videoPreviewFrameOffset.setSliderPosition(0)

            self.setPreviewSliderAndSpinboxEnable(True)
            self.setVideoWidgetEnable(True)

            self.video.requestFrame()
            self.timer.setSingleShot(True)
            self.timer.start(100)

    def videoBWThresholdValueUpdate(self):
        self.videoBWThresholdValue = self.main_ui.spinBox_videoBWThreshold.value()

        if not self.timer.isActive():
            self.video.setBWThreshold(value=self.videoBWThresholdValue)
            self.video.setIndex(self.currentFrameIndex)
            self.video.requestFrame()
            self.timer.setSingleShot(True)
            self.timer.start(50)

    def previewBWSizeUpdate(self):
        if self.main_ui.checkBox_videoPreviewBW2x.isChecked():
            self.videoPreviewBWSize = '256*128'
        else:
            self.videoPreviewBWSize = '128*64'

        if not self.timer.isActive():
            self.video.setIndex(self.currentFrameIndex)
            self.video.requestFrame()
            self.timer.setSingleShot(True)
            self.timer.start(50)

    def BWInvertUpdate(self):
        if self.main_ui.checkBox_videoBWInvert.isChecked():
            self.video.setBWThreshold(invert=True)
        else:
            self.video.setBWThreshold(invert=False)

        if not self.timer.isActive():
            self.video.setIndex(self.currentFrameIndex)
            self.video.requestFrame()
            self.timer.setSingleShot(True)
            self.timer.start(50)

    def previewModeUpdate(self):
        if self.main_ui.radioButton_videoPreviewRaw.isChecked():
            self.previewMode = 'raw'
        elif self.main_ui.radioButton_videoPreviewGray.isChecked():
            self.previewMode = 'gray'
        else:
            self.previewMode = 'BW'

        if not self.timer.isActive():
            self.video.setIndex(self.currentFrameIndex)
            self.video.requestFrame()
            self.timer.setSingleShot(True)
            self.timer.start(50)

    def previewSilderUpdate(self):
        self.currentFrameIndex = self.main_ui.horizontalSlider_videoPreviewFrameOffset.value()

        if not self.timer.isActive():
            self.video.setIndex(self.currentFrameIndex)
            self.video.requestFrame()
            self.timer.setSingleShot(True)
            self.timer.start(50)

    def updatePreview(self):
        # update preview
        if self.previewMode == 'raw':
            image = self.image_raw
        elif self.previewMode == 'gray':
            image = self.image_gray
        else:
            image = self.image_bw
        image_pix = OpenCVImage2QPixMap(image)
        self.main_ui.label_videoPreviewWindow.setPixmap(QPixmap.fromImage(image_pix))

    def updateBWPreview(self):
        if self.videoPreviewBWSize == '256*128':
            image = self.image_out_bw2x
        else:
            image = self.image_out_bw
        image_pix = OpenCVImage2QPixMap(image)
        self.main_ui.label_videoPreviewOutputBW.setPixmap(QPixmap.fromImage(image_pix))

    def videoSendStateUpdate(self):
        if self.videoSending:
            self.videoSending = False
            self.setPreviewSliderAndSpinboxEnable(True)
            self.main_ui.pbt_videoStartSending.setText('Start Sending')
            self.timer.stop()
            self.video.clearFrames()
        else:
            self.videoSending = True
            self.setPreviewSliderAndSpinboxEnable(False)
            self.video.clearFrames()
            self.video.setIndex(self.currentFrameIndex)
            self.video.requestFrame()
            self.main_ui.pbt_videoStartSending.setText('Stop Sending')
            timeout = int(1000 / self.main_ui.spinBox_videoSendFramerate.value())
            self.timer.setInterval(timeout)
            self.timer.setTimerType(0)
            self.timer.setSingleShot(False)
            self.timer.start()
            self.lastTimeStamp = time.time()

    def readAllImages(self):
        result = self.video.readFrames()
        if result != None:
            self.image_raw, self.image_gray, self.image_bw, self.image_out_bw, self.image_out_bw2x, self.image_data_frame = result
            return True
        else:
            return False

    def videoSend(self):
        if self.readAllImages():
            self.updatePreview()
            self.updateBWPreview()
            if self.videoSending:
                self.video.requestFrame()
                self.currentFrameIndex += 1
                self.send(self.image_data_frame)

        self.lastTimeStamp = time.time()

        self.main_ui.horizontalSlider_videoPreviewFrameOffset.setSliderPosition(self.currentFrameIndex)
        self.main_ui.spinBox_videoFrameOffset.setValue(self.currentFrameIndex)

        if self.currentFrameIndex + 1 >= int(self.video.frameCount):
            self.videoSendStateUpdate()


    def addSendMethod(self, sendMethod):
        self.sendMethod = sendMethod

    def send(self, data):
        if self.sendMethod != None:
            self.sendMethod.send(data)

    def exit(self):
        if self.video != None:
            self.video.stop()