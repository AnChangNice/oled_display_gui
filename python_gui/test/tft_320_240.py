import cv2 as cv
import numpy as np

import serial

def re_sample(gray_image, width, height):
    # binary
    image_bw = (gray_image > 127) * np.uint8(1)
    # re-sample
    image_raw_bw = np.zeros((8, int(width*(height/8))), dtype='uint8')
    for col in range(0, width):
        for row_index in range(0, int(height/8)):
            row = row_index * 8
            image_raw_bw[0:, col * int(height/8) + row_index] = image_bw[row:row+8, col]
    # into byte
    num_bytes = int(width * height / 8)
    image_raw_bytes = np.zeros(num_bytes, dtype='uint8')
    for col in range(0, num_bytes):
        one_byte_array = image_raw_bw[0:8, col]
        byte_str = ''.join([str(x) for x in one_byte_array])
        # byte_str = byte_str[::-1]
        image_raw_bytes[col] = np.int(byte_str, 2)

    return image_raw_bytes


port = serial.Serial('COM9', 1000000)

if __name__ == '__main__':
    image = cv.imread('../images/5.jpg')
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = cv.resize(image, (320, 240))

    image = cv.flip(image, 1)

    cv.imshow('image', image)

    image_bw_bytes = re_sample(image, 320, 240)

    # bw_image = (image // 8) * np.uint8(1)
    # bw_image_raw_data = bw_image.reshape((1, 240*120))[0]
    col = 16
    index = 0
    out_str = ''
    for i in range(col):
        for j in range(int(320*240/8/col)):
            out_str += '%02x ' % (image_bw_bytes[index])
            index += 1
        out_str += '\n'
    print(out_str)
    port.write(image_bw_bytes)
    cv.waitKey(2000)
    cv.destroyWindow('image')

port.close()