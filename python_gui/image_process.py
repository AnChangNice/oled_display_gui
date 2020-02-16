import threading
import queue
import cv2 as cv
import numpy as np

from image_processing.image_to_oled import re_sample

class ImageStreamProcess(object):

    def __init__(self):
        self.imageThread = threading.Thread(target=self.videoThreading)
        self.imageThread_run = False

        self.readFrameQueue = queue.Queue()
        self.readFrameCompleteQueue = queue.Queue()
        self.frameQueue = queue.Queue()
        self.image_processing = False

        self.frameRate = 0
        self.frameCount = 0
        self.frameWidth = 0
        self.frameHeight = 0

        self.image_preview_width = 128
        self.image_preview_height = 64

        self.image_preview_out_width = 128
        self.image_preview_out_height = 64
        self.image_preview_out2x_width = 256
        self.image_preview_out2x_height = 128

        self.image_raw = None
        self.image_gray = None
        self.image_bw = None

        self.imageBW_thresholdValue = 127
        self.imageBW_invert = False

        self.image_out_bw = None
        self.image_out_bw2x = None

        self.image_data_frame = None

    def start(self):
        self.imageThread_run = True
        self.imageThread.start()

    def stop(self):
        self.imageThread_run = False
        self.imageThread.join()

    def setBWThreshold(self, value=0, invert=None):
        if value != 0:
            self.imageBW_thresholdValue = value
        if invert is not None:
            self.imageBW_invert = invert

    def setPreviewSize(self, width, height):
        self.image_preview_width = width
        self.image_preview_height = height

    def requestFrame(self, image):
        self.readFrameQueue.put(image)

    def clearFrames(self):
        while self.frameQueue.qsize() > 0:
            self.frameQueue.get()

    def readFrames(self):
        try:
            return self.frameQueue.get(timeout=0.1)
        except:
            return None

    def readVideoFrame(self, frame):
        self.image_raw = cv.resize(frame, (self.image_preview_width, self.image_preview_height))
        self.image_gray = cv.cvtColor(self.image_raw, cv.COLOR_BGR2GRAY)
        if not self.imageBW_invert:
            self.image_bw = (self.image_gray > self.imageBW_thresholdValue) * np.uint8(255)
        else:
            self.image_bw = (self.image_gray <= self.imageBW_thresholdValue) * np.uint8(255)
        self.image_out_bw2x = cv.resize(self.image_bw, (256, 128))
        self.image_out_bw = cv.resize(self.image_bw, (128, 64))
        self.image_data_frame = re_sample(self.image_out_bw)

    def putFrameIntoQueue(self):
        self.frameQueue.put((self.image_raw, self.image_gray, self.image_bw, self.image_out_bw, self.image_out_bw2x,
                             self.image_data_frame))

    def videoThreading(self):
        while self.imageThread_run:
            try:
                image = self.readFrameQueue.get(timeout=0.1)
                self.readVideoFrame(image)
                self.putFrameIntoQueue()
            except Exception:
                pass