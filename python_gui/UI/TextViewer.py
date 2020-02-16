# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TextViewer.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_TextViewer(object):
    def setupUi(self, Dialog_TextViewer):
        Dialog_TextViewer.setObjectName("Dialog_TextViewer")
        Dialog_TextViewer.resize(554, 699)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog_TextViewer)
        self.buttonBox.setGeometry(QtCore.QRect(20, 630, 521, 41))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.textBrowser_OutputCArray = QtWidgets.QTextBrowser(Dialog_TextViewer)
        self.textBrowser_OutputCArray.setGeometry(QtCore.QRect(10, 10, 531, 611))
        self.textBrowser_OutputCArray.setObjectName("textBrowser_OutputCArray")

        self.retranslateUi(Dialog_TextViewer)
        self.buttonBox.accepted.connect(Dialog_TextViewer.accept)
        self.buttonBox.rejected.connect(Dialog_TextViewer.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_TextViewer)

    def retranslateUi(self, Dialog_TextViewer):
        _translate = QtCore.QCoreApplication.translate
        Dialog_TextViewer.setWindowTitle(_translate("Dialog_TextViewer", "Text Viewer"))
