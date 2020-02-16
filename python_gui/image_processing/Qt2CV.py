from PyQt5.QtGui import QImage

import numpy as np

def OpenCVImage2QPixMap(cvImage):
    if len(cvImage.shape) == 3:
        height, width, channel = cvImage.shape
        bytesPerLine = 3 * width
        return QImage(cvImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
    elif len(cvImage.shape) == 2:
        height, width = cvImage.shape
        bytesPerLine = 1 * width
        return QImage(cvImage.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
    else:
        print("OpenCVImage2QPixMap: image type not covered!")
        return None

def QPixmap2OpenCVImage(qimage):
    # convert to 24bits image
    image = qimage.convertToFormat(QImage.Format_RGB888)

    # get image info
    width = image.width()
    height = image.height()
    # check if its width is fit 4 bytes aligned
    is4bytesAligned = True
    if width * 3 != image.bytesPerLine():
        is4bytesAligned = False

    # reshape to opencv image
    ptr = image.bits()
    ptr.setsize(image.byteCount())
    if not is4bytesAligned:
        arr_temp = np.array(ptr).reshape(height, image.bytesPerLine())
        arr_temp = arr_temp[:, 0:(3*width)]
        arr = np.array(arr_temp).reshape(height, width, 3)
    else:
        arr = np.array(ptr).reshape(height, width, 3)  # Copies the data
    return arr