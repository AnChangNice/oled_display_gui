
import numpy as np
from common.Singleton import Singleton

from ctypes import CDLL, c_uint8, c_int, Structure

@Singleton
class BWImageToBytes(object):
    """
    image_flip_h: True, False
    image_flip_v: True, False
    scan_dir: H, V
    byte_dir: H, V
    sign_bit: LSB, MSB
    """
    def __init__(self, image_flip_h=False, image_flip_v=False, scan_dir='H', byte_dir='H', sign_bit='LSB'):
        self.image_flip_h = image_flip_h
        self.image_flip_v = image_flip_v
        self.scan_dir = scan_dir
        self.byte_dir = byte_dir
        self.sign_bit = sign_bit

        # init dll
        self.bw2bytes_config = self.BW2BYTES_CONFIG()
        self.update_bw_config()
        self.bw2bytes_func = None
        self.load_dll()

    class BW2BYTES_CONFIG(Structure):
        _fields_ = [
            ("flip_h", c_int),
            ("flip_v", c_int),
            ("scan_dir", c_int),
            ("byte_dir", c_int),
            ("sign_bit", c_int)]

    def load_dll(self):
        dll_lib = CDLL("./image_processing/image_processing.dll")
        self.bw2bytes_func = dll_lib.bw2Bytes

        # set args type
        self.bw2bytes_func.argtypes = [np.ctypeslib.ndpointer(c_uint8),
                                        np.ctypeslib.ndpointer(c_uint8, 1),
                                        c_int,
                                        c_int,
                                        self.BW2BYTES_CONFIG]
        self.bw2bytes_func.restype = c_int

    def update_bw_config(self):
        if self.image_flip_h == True:
            self.bw2bytes_config.flip_h = 1
        else:
            self.bw2bytes_config.flip_h = 0

        if self.image_flip_v == True:
            self.bw2bytes_config.flip_v = 1
        else:
            self.bw2bytes_config.flip_v = 0

        if self.scan_dir == 'H':
            self.bw2bytes_config.scan_dir = 0
        else:
            self.bw2bytes_config.scan_dir = 1

        if self.byte_dir == 'H':
            self.bw2bytes_config.byte_dir = 0
        else:
            self.bw2bytes_config.byte_dir = 1

        if self.sign_bit == 'MSB':
            self.bw2bytes_config.sign_bit = 0
        else:
            self.bw2bytes_config.sign_bit = 1

    def setHorizontalFlip(self, enable):
        if type(enable) is bool:
            self.image_flip_h = enable
        else:
            raise Exception('param: should be True/False !')

    def setVerticalFlip(self, enable):
        if type(enable) is bool:
            self.image_flip_v = enable
        else:
            raise Exception('param: should be True/False !')

    def setScanDirection(self, direction):
        if direction == 'H' or direction == 'h':
            self.scan_dir = 'H'
        elif direction == 'V' or direction == 'v':
            self.scan_dir = 'V'
        else:
            raise Exception('direction: should be H/v !')

    def setByteDirection(self, direction):
        if direction == 'H' or direction == 'h':
            self.byte_dir = 'H'
        elif direction == 'V' or direction == 'v':
            self.byte_dir = 'V'
        else:
            raise Exception('direction: should be H/v !')

    def setSignBit(self, sign_bit):
        if sign_bit == 'LSB':
            self.sign_bit = 'LSB'
        elif sign_bit == 'MSB':
            self.sign_bit = 'MSB'
        else:
            raise Exception('sign_bit: should be LSB/MSB !')

    def convert(self, image):
        """
        :param image: numpy 2D BW image array 0-black, 1-light
        :return: numpy 1D array
        """
        h, w = image.shape
        # update config
        self.update_bw_config()
        # malloc a new array
        data_bytes = np.zeros(h * w // 8, dtype='uint8')

        if self.bw2bytes_func(image.copy(), data_bytes, w, h, self.bw2bytes_config) != 0:
            return None
        else:
            return data_bytes

        # # force image data to 0 and 1
        # if image.max() > 1:
        #     image = (image > 1) * np.uint8(1)
        #
        # if (self.byte_dir == 'H') and (w % 8 != 0):
        #     raise Exception("Error: byte_dir not fit or image width not aligned with 8\n")
        # if (self.byte_dir == 'V') and (h % 8 != 0):
        #     raise Exception("Error: byte_dir not fit or image height not aligned with 8\n")
        #
        # # step 1, flip
        # if self.image_flip_h:
        #     image = image[:, ::-1]
        #
        # if self.image_flip_v:
        #     image = image[::-1, :]
        #
        # # step 2, scan_dir and byte_dir
        # output_bytes = w * h // 8
        # new_image_array = np.zeros((output_bytes, 8), dtype='uint8')
        #
        # i = 0
        # if self.scan_dir == 'H':
        #     if self.byte_dir == 'H':
        #         for row in range(h):
        #             for col in range(0, w, 8):
        #                 new_image_array[i, :] = image[row, col:col+8]
        #                 i += 1
        #     else:
        #         for row in range(0, h, 8):
        #             for col in range(w):
        #                 new_image_array[i, :] = image[row:row+8, col]
        #                 i += 1
        # else:
        #     if self.byte_dir == 'H':
        #         for col in range(0, w, 8):
        #             for row in range(h):
        #                 new_image_array[i, :] = image[row, col:col+8]
        #                 i += 1
        #     else:
        #         for col in range(w):
        #             for row in range(0, h, 8):
        #                 new_image_array[i, :] = image[row:row+8, col]
        #                 i += 1
        # if i != output_bytes:
        #     print('Error: sample bytes length error!\n')
        #
        # # step 3, sign_bit
        # if self.sign_bit == 'MSB':
        #     new_image_array = new_image_array[:, ::-1]
        # elif self.sign_bit == 'LSB':
        #     pass
        # else:
        #     raise Exception('sign_bit setting must be LSB/MSB\n')
        #
        # # step 4, output to bytes 1D array
        # data_bytes = np.zeros(output_bytes, dtype='uint8')
        # for i in range(output_bytes):
        #     bits = new_image_array[i, :]
        #     bits_str = ''.join([str(x) for x in bits])
        #     data_bytes[i] = np.int(bits_str, 2)
        #
        # return data_bytes


if __name__ == '__main__':
    image = np.zeros((64, 128), dtype='uint8')

    image[0, 0:8] = np.array([1, 1, 1, 1, 0, 0, 0, 0])

    image_processor = BWImageToBytes(sign_bit='MSB', scan_dir='V', byte_dir='V')
    image_processor.set_sign_bit('1')
    image_processor.set_scan_dir('v')
    image_processor.set_byte_direction('v')

    result = image_processor.convert(image)

    print(result[0:2])

