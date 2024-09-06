# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'inc\splash.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Splash(object):
    def setupUi(self, Splash):
        Splash.setObjectName(_fromUtf8("Splash"))
        Splash.resize(400, 220)
        Splash.setWindowOpacity(1.0)
        self.label = QtGui.QLabel(Splash)
        self.label.setGeometry(QtCore.QRect(0, 0, 400, 220))
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8("logo.png")))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(Splash)
        QtCore.QMetaObject.connectSlotsByName(Splash)

    def retranslateUi(self, Splash):
        pass

