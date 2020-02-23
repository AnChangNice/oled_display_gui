import threading
import queue
import cv2 as cv
import numpy as np

from image_processing.BWImageToBytes import BWImageToBytes
from common.Singleton import Singleton


class OutputImagesStructure(object):
    def __init__(self):
        # images for preview
        self.raw = None
        self.gray = None
        self.bw = None
        # images for output
        self.output_bw = None
        self.output_bw2x = None
        # output bw image bytes
        self.bytes = None


@Singleton
class ImageTranslate(object):

    def __init__(self):
        self.thread = threading.Thread(target=self.process_threading)
        self.thread_run = False

        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        self.output_images = OutputImagesStructure()

        self.complete_callback = None

        self.image_to_bw = BWImageToBytes()

        self.update_setting = False

        self.preview_image_width = 128
        self.preview_image_height = 64

        self.preview_image_width_temp = 128
        self.preview_image_height_temp = 64

        self.output_image_width = 128
        self.output_image_height = 64

        self.output_image_width_temp = 128
        self.output_image_height_temp = 64

        self.bw_threshold = 127
        self.bw_threshold_temp = 127
        self.bw_invert = False
        self.bw_invert_temp = False

    def start(self):
        if self.thread_run:
            return None
        self.thread_run = True
        self.thread.start()

    def stop(self):
        self.thread_run = False
        self.thread.join()

    def set_threshold(self, value):
        if value != 0:
            self.bw_threshold_temp = value

        self.update_setting = True

    def set_invert(self, enable):
        if type(enable) == bool:
            self.bw_invert_temp = enable

        self.update_setting = True

    def set_preview_size(self, width, height):
        self.preview_image_width_temp = width
        self.preview_image_height_temp = height

        self.update_setting = True

    def set_output_size(self, width, height):
        self.output_image_width_temp = width
        self.output_image_height_temp = height

        self.update_setting = True

    def update_parameters(self):
        if not self.update_setting:
            return None
        self.update_setting = False

        self.bw_threshold = self.bw_threshold_temp
        self.bw_invert = self.bw_invert_temp

        self.preview_image_width = self.preview_image_width_temp
        self.preview_image_height = self.preview_image_height_temp

        self.output_image_width = self.output_image_width_temp
        self.output_image_height = self.output_image_height_temp

    def input_image(self, image):
        self.input_queue.put(image, timeout=0.1)

    def output_clean(self):
        while self.output_queue.qsize() > 0:
            self.output_queue.get()

    def read_images(self):
        try:
            return self.output_queue.get(timeout=0.1)
        except:
            return None

    def install_complete_callback(self, callback):
        if callback != None:
            self.complete_callback = callback

    def remove_complete_callback(self):
        self.complete_callback = None

    def image_translate(self, image):
        image_raw = cv.resize(image, (self.preview_image_width, self.preview_image_height))
        image_gray = cv.cvtColor(image_raw, cv.COLOR_BGR2GRAY)
        if not self.bw_invert:
            image_bw = (image_gray > self.bw_threshold) * np.uint8(255)
        else:
            image_bw = (image_gray <= self.bw_threshold) * np.uint8(255)
        image_out_bw2x = cv.resize(image_bw, (2 * self.output_image_width, 2 * self.output_image_height))
        image_out_bw = cv.resize(image_bw, (self.output_image_width, self.output_image_height))
        image_out_bw_bytes = self.image_to_bw.convert(image_out_bw)

        self.output_images.raw = image_raw
        self.output_images.gray = image_gray
        self.output_images.bw = image_bw
        self.output_images.output_bw = image_out_bw
        self.output_images.output_bw2x = image_out_bw2x
        self.output_images.bytes = image_out_bw_bytes

    def output_images_to_queue(self):
        self.output_queue.put(self.output_images, timeout=0.1)

    def process_threading(self):
        while self.thread_run:
            try:
                image = self.input_queue.get(timeout=0.1)
                self.update_parameters()
                self.image_translate(image)
                self.output_images_to_queue()
                if self.complete_callback != None:
                    self.complete_callback(self.output_queue)
            except:
                pass
