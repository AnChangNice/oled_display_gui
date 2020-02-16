import cv2 as cv
import numpy as np

import serial

import time

def re_sample(gray_image, width, height):
    # binary
    image_bw = (gray_image < 127) * np.uint8(1)
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


display = serial.Serial('COM9', 1000000, write_timeout=0)

frame_index = 0

last_time_stamp = 0

average_dt = 0

if __name__ == '__main__':

    try:
        # open video
        cap = cv.VideoCapture('../video/bad_apple.mp4')

        while True:
            # read one frame image
            ret, frame = cap.read()
            image = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            image = cv.resize(image, (240, 120))

            # cv.imshow('input_image', frame)
            cv.imshow('output_image', image)

            image = cv.flip(image, 1)

            # re-sample image
            bytes_stream = re_sample(image, 240, 120)

            # wait for response
            if frame_index != 0:
                display.read_until(b'\n')
                display.read_all()

            # send one frame data
            display.write(bytes_stream)

            # update frame index
            frame_index += 1

            # break
            cv.waitKey(1)

            # update time stamp
            new_time_stamp = time.process_time()
            dt = new_time_stamp - last_time_stamp
            last_time_stamp = new_time_stamp

            average_dt = dt * 0.05 + 0.95 * average_dt

            print('index: %d, fps: %.1f' % (frame_index, 1 / average_dt))

    except 'Exception':
        display.close()
        cap.release()
        cv.destroyAllWindows()