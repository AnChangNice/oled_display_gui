
from PyQt5 import QtCore, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(460, 330, 93, 28))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Form)
        self.pushButton.clicked.connect(self.button_click)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "PushButton"))

    def button_click(self):
        print('Push button clicked!')


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QWidget
    import sys

    # Make a Qt Framework
    app = QApplication(sys.argv)

    # Make a from
    w = QWidget()

    # add item
    ui = Ui_Form()
    ui.setupUi(w)

    # Show a form
    w.show()

    # run Framework and wait for exit
    app.exec_()

