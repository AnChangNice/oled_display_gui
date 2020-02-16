import numpy as np
import cv2 as cv

import serial
import time


# re-sample image
def re_sample(gray_image):
    # binary
    image_bw = (gray_image > 127) * np.uint8(1)
    # re-sample
    image_raw_bw = np.zeros((8, int(128*(64/8))), dtype='uint8')
    for row_index in range(0,8):
        row = row_index * 8
        for col in range(0, 128):
            image_raw_bw[0:, row_index * 128 + col] = image_bw[row:row+8, col]

    # into byte
    image_raw_bytes = np.zeros(1024, dtype='uint8')
    for col in range(0, 1024):
        one_byte_array = image_raw_bw[0:8, col]
        byte_str = ''.join([str(x) for x in one_byte_array])
        byte_str = byte_str[::-1]
        image_raw_bytes[col] = np.int(byte_str, 2)

    return image_raw_bytes


display = serial.Serial('COM6', 1000000, write_timeout=0)

frame_index = 0

last_time_stamp = 0

average_dt = 0

if __name__ == '__main__':
    
    try:
        # open video
        cap = cv.VideoCapture('video/bad_apple.mp4')

        while True:
            # read one frame image
            ret, frame = cap.read()
            image = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            image = cv.resize(image, (128, 64))
            
            # cv.imshow('input_image', frame)
            cv.imshow('output_image', image)

            # re-sample image
            bytes_stream = re_sample(image)

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

            print('index: %d, fps: %.1f' % (frame_index, 1/average_dt))
        
    except 'Exception':
        display.close()
        cap.release()
        cv.destroyAllWindows()
