import cv2 as cv
import numpy as np

import time

def gray2bw(imageArray):
    hight, width = imageArray.shape
    
    bw_image_array = np.zeros((hight, width), int)
    
    for i in range(hight):
        for j in range(width):
            bw_image_array[i][j] = 1 if imageArray[i][j] > 128 else 0
    return bw_image_array

def bw2bytes(bw_image):
    hight, width = bw_image.shape
    rows = hight / 8

    array_list = []

    for row_index in range(rows):
        row = row_index * 8
        for col in range(width):
            bytes_array = []
            for i in range(8):
                bytes_array.append(bw_image[row+i][col])
            array_list.append(bytes_array)

    return array_list

def bytes_array_to_byte(bytes_array):
    byte_list = []
    for nums in bytes_array:
        num_byte = 0
        index = 0
        for num in nums:
            num_byte |= num << index
            index += 1
        byte_list.append(num_byte)
    
    return byte_list

def readImageAndConvertToBytes(file_path):
    image = cv.imread(file_path)
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = cv.resize(image, (128, 64))

    bw_image = gray2bw(image)
    bw_image_bytes_list = bw2bytes(bw_image)
    byte_list = bytes_array_to_byte(bw_image_bytes_list)

    return byte_list

import serial
oled = serial.Serial('COM6', 1000000)

while True:
    try:
        time.sleep(1)
        bytes_stream = readImageAndConvertToBytes('../images/demo_icon.png')
        oled.write(bytes_stream)
        print("Send complete!")
    except:
        print("Send Error, closed!")
        oled.close()
        break