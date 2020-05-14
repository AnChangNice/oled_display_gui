import sys

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

from PyQt5.QtWidgets import QApplication

from window.main_Window import MainWindow

if __name__ == '__main__':

    app = QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec_())

    window.exit()