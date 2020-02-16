import cv2 as cv
import numpy as np

import serial
import time

def gray2bw(imageArray):
    return (imageArray > 127) * np.uint8(1)

def bw2bytes(bw_image):
    hight, width = bw_image.shape
    rows = hight / 8

    image_raw_bw = np.zeros((8, 128*(64/8)), dtype='uint8')
    for row_index in range(0,8):
        row = row_index * 8
        for col in range(0, 128):
            image_raw_bw[0:, row_index * 128 + col] = bw_image[row:row+8, col]

    return image_raw_bw

def bytes_array_to_byte(bytes_array):
    # into byte
    image_raw_bytes = np.zeros((1024), dtype='uint8')
    for col in range(0, 1024):
        one_byte_array = bytes_array[0:8, col]
        byte_str = ''.join([str(x) for x in one_byte_array])
        byte_str = byte_str[::-1]
        image_raw_bytes[col] = np.int(byte_str, 2)
    
    return image_raw_bytes

def readImageAndConvertToBytes(file_path):
    image = cv.imread(file_path)
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = cv.resize(image, (128, 64))

    bw_image = gray2bw(image)
    cv.imwrite('bw_image.png', bw_image)
    bw_image_bytes_list = bw2bytes(bw_image)
    cv.imwrite('bw_image_bytes_list.png', bw_image_bytes_list)
    byte_list = bytes_array_to_byte(bw_image_bytes_list)

    return byte_list

display = serial.Serial('COM6', 1000000)

rx_buffer = ''

send_flag = False


s1 = time.clock()
image_name = "images/demo_icon.png"
bytes_stream = readImageAndConvertToBytes(image_name)
s2 = time.clock()
if send_flag == True:
    # wait for ack
    rx_buffer = display.read_until('\n')
    print(rx_buffer)
    print(s2-s1)
send_flag = True
display.write(bytes_stream)


display.close()