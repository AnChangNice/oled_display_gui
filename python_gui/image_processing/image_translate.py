import threading
import queue
import cv2 as cv
import numpy as np

from image_processing.BWImageToBytes import BWImageToBytes
from common.Singleton import Singleton

import time

from ctypes import CDLL, c_uint8, c_int

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


# bayer4 = np.array(
#    [[0, 12,  3, 15],
#     [8,  4, 11,  7],
#     [2, 14,  1, 13],
#     [10, 6,  9,  5]], dtype='uint8')
#
# bayer8 = np.array(
#     [[ 0, 32,  8, 40,  2, 34, 10, 42],
#      [48, 16, 56, 24, 50, 18, 58, 26],
#      [12, 44,  4, 36, 14, 46,  6, 38],
#      [60, 28, 52, 20, 62, 30, 54, 22],
#      [ 3, 35, 11, 43,  1, 33,  9, 41],
#      [51, 19, 59, 27, 49, 17, 57, 25],
#      [15, 47,  7, 39, 13, 45,  5, 37],
#      [63, 31, 55, 23, 61, 29, 53, 21]], dtype='uint8'
# )
#
# bayer16 = np.array(
#     [[  0, 128,  32, 160,   8, 136,  40, 168,   2, 130,  34, 162,  10, 138,  42, 170],
#      [192,  64, 224,  96, 200,  72, 232, 104, 194,  66, 226,  98, 202,  74, 234, 106],
#      [ 48, 176,  16, 144,  56, 184,  24, 152,  50, 178,  18, 146,  58, 186,  26, 154],
#      [240, 112, 208,  80, 248, 120, 216,  88, 242, 114, 210,  82, 250, 122, 218,  90],
#      [ 12, 140,  44, 172,   4, 132,  36, 164,  14, 142,  46, 174,   6, 134,  38, 166],
#      [204,  76, 236, 108, 196,  68, 228, 100, 206,  78, 238, 110, 198,  70, 230, 102],
#      [ 60, 188,  28, 156,  52, 180,  20, 148,  62, 190,  30, 158,  54, 182,  22, 150],
#      [252, 124, 220,  92, 244, 116, 212,  84, 254, 126, 222,  94, 246, 118, 214,  86],
#      [  3, 131,  35, 163,  11, 139,  43, 171,   1, 129,  33, 161,   9, 137,  41, 169],
#      [195,  67, 227,  99, 203,  75, 235, 107, 193,  65, 225,  97, 201,  73, 233, 105],
#      [ 51, 179,  19, 147,  59, 187,  27, 155,  49, 177,  17, 145,  57, 185,  25, 153],
#      [243, 115, 211,  83, 251, 123, 219,  91, 241, 113, 209,  81, 249, 121, 217,  89],
#      [ 15, 143,  47, 175,   7, 135,  39, 167,  13, 141,  45, 173,   5, 133,  37, 165],
#      [207,  79, 239, 111, 199,  71, 231, 103, 205,  77, 237, 109, 197,  69, 229, 101],
#      [ 63, 191,  31, 159,  55, 183,  23, 151,  61, 189,  29, 157,  53, 181,  21, 149],
#      [255, 127, 223,  95, 247, 119, 215,  87, 253, 125, 221,  93, 245, 117, 213,  85]], dtype='uint8'
# )
#
#
# def dither(gray_image, bayer_size):
#
#     h, w = gray_image.shape
#     gray_image = gray_image // (256 // (bayer_size ** 2))
#
#     if bayer_size == 4:
#         bayer = bayer4
#     elif bayer_size == 8:
#         bayer = bayer8
#     elif bayer_size == 16:
#         bayer = bayer16
#     else:
#         return None
#
#     for x in range(h):
#         for y in range(w):
#             if gray_image[x, y] > bayer[x % bayer_size, y % bayer_size]:
#                 gray_image[x, y] = 255
#             else:
#                 gray_image[x, y] = 0
#
#     return gray_image


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

        self.dither_size = 0
        self.dither_size_temp = 0
        self.binarization_mode = 'threshold'
        self.binarization_mode_temp = 'threshold'

        self.binarization_equalizeHist = False
        self.binarization_equalizeHist_temp = False

        # init dll
        self.dithering = None
        self.error_diffusion = None
        self.load_dll()


    def start(self):
        if self.thread_run:
            return None
        self.thread_run = True
        self.thread.start()

    def stop(self):
        self.thread_run = False
        self.thread.join()

    def load_dll(self):
        dll_lib = CDLL("./image_processing/image_processing.dll")
        self.dithering = dll_lib.dithering
        self.error_diffusion = dll_lib.error_diffusion

        # set args type
        self.dithering.argtypes = [np.ctypeslib.ndpointer(c_uint8),
                                   c_int,
                                   c_int,
                                   c_int]
        self.dithering.restype = c_int

        self.error_diffusion.argtypes = [np.ctypeslib.ndpointer(c_uint8),
                                         c_int,
                                         c_int]
        self.error_diffusion.restype = c_int

    def set_threshold(self, value):
        if value != 0:
            self.bw_threshold_temp = value

        self.update_setting = True

    def set_dither_size(self, size):
        self.dither_size_temp = size

        self.update_setting = True

    def set_binarization_mode(self, mode):
        self.binarization_mode_temp = mode

        self.update_setting = True

    def set_invert(self, enable):
        if type(enable) == bool:
            self.bw_invert_temp = enable

        self.update_setting = True

    def set_equalizrHist(self, enable):
        if type(enable) == bool:
            self.binarization_equalizeHist_temp = enable

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

        self.dither_size = self.dither_size_temp
        self.binarization_mode = self.binarization_mode_temp
        self.binarization_equalizeHist = self.binarization_equalizeHist_temp

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
        # s1 = time.perf_counter()
        w = self.preview_image_width
        h = self.preview_image_height

        image_raw = cv.resize(image, (w, h))
        image_gray = cv.cvtColor(image_raw, cv.COLOR_BGR2GRAY)

        if self.binarization_equalizeHist:
            image_gray = cv.equalizeHist(image_gray)

        image_out_gray_2x = cv.resize(image_gray, (2 * self.output_image_width, 2 * self.output_image_height))
        image_out_gray_1x = cv.resize(image_gray, (self.output_image_width, self.output_image_height))

        if self.binarization_mode == 'threshold':
            if not self.bw_invert:
                ret, image_bw = cv.threshold(image_gray, self.bw_threshold, 255, cv.THRESH_BINARY)
                ret, image_out_bw2x = cv.threshold(image_out_gray_2x, self.bw_threshold, 255, cv.THRESH_BINARY)
                ret, image_out_bw = cv.threshold(image_out_gray_1x, self.bw_threshold, 255, cv.THRESH_BINARY)
            else:
                ret, image_bw = cv.threshold(image_gray, self.bw_threshold, 255, cv.THRESH_BINARY_INV)
                ret, image_out_bw2x = cv.threshold(image_out_gray_2x, self.bw_threshold, 255, cv.THRESH_BINARY_INV)
                ret, image_out_bw = cv.threshold(image_out_gray_1x, self.bw_threshold, 255, cv.THRESH_BINARY_INV)
        elif self.binarization_mode == 'dithering':
            image_bw = image_gray.copy()
            self.dithering(image_bw, w, h, self.dither_size)

            image_out_bw2x = image_out_gray_2x
            self.dithering(image_out_bw2x, 2 * self.output_image_width, 2 * self.output_image_height, self.dither_size)

            image_out_bw = image_out_gray_1x
            self.dithering(image_out_bw, self.output_image_width, self.output_image_height, self.dither_size)
        elif self.binarization_mode == 'error_diff':
            image_bw = image_gray.copy()
            self.error_diffusion(image_bw, w, h)

            image_out_bw2x = image_out_gray_2x
            self.error_diffusion(image_out_bw2x, 2 * self.output_image_width, 2 * self.output_image_height)

            image_out_bw = image_out_gray_1x
            self.error_diffusion(image_out_bw, self.output_image_width, self.output_image_height)
        else:
            return None
        # s1 = time.perf_counter()
        image_out_bw_bytes = self.image_to_bw.convert(image_out_bw)
        # s2 = time.perf_counter()
        # dt = s2-s1
        # print('dt: %.6f, fps: %.3f' % (dt, 1/dt))

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
