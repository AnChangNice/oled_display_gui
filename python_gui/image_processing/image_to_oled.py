import numpy as np

def re_sample(gray_image):
    # binary
    image_bw = (gray_image > 127) * np.uint8(1)
    # re-sample
    image_raw_bw = np.zeros((8, int(128*(64/8))), dtype='uint8')
    for row_index in range(0, 8):
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