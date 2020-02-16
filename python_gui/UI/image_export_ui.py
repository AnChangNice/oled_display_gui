# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'image_export_ui.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_imageExportWindow(object):
    def setupUi(self, imageExportWindow):
        imageExportWindow.setObjectName("imageExportWindow")
        imageExportWindow.resize(800, 400)
        self.widget = QtWidgets.QWidget(imageExportWindow)
        self.widget.setGeometry(QtCore.QRect(0, 0, 800, 400))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textEdit_eportEditor = QtWidgets.QTextEdit(self.widget)
        self.textEdit_eportEditor.setObjectName("textEdit_eportEditor")
        self.verticalLayout.addWidget(self.textEdit_eportEditor)

        self.retranslateUi(imageExportWindow)
        QtCore.QMetaObject.connectSlotsByName(imageExportWindow)

    def retranslateUi(self, imageExportWindow):
        _translate = QtCore.QCoreApplication.translate
        imageExportWindow.setWindowTitle(_translate("imageExportWindow", "Export Window"))
