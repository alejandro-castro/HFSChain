# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/roj-idl71/SignalChain/initwindowv2.ui'
#
# Created: Wed Mar  6 15:32:39 2013
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_InitWindow(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(652, 496)
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_3 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Cambria"))
        font.setPointSize(22)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Signal Chain - Ver. 1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_4.addWidget(self.label_3)
        self.line_2 = QtGui.QFrame(Dialog)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout_4.addWidget(self.line_2)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setText(_fromUtf8(""))
        self.label_4.setPixmap(QtGui.QPixmap(_fromUtf8("figure/w.jpg")))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_4.addWidget(self.label_4)
        self.verticalLayout_3.addLayout(self.verticalLayout_4)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.ExitBtn = QtGui.QPushButton(Dialog)
        self.ExitBtn.setText(QtGui.QApplication.translate("Dialog", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.ExitBtn.setObjectName(_fromUtf8("ExitBtn"))
        self.horizontalLayout_4.addWidget(self.ExitBtn)
        self.ContinueBtn = QtGui.QPushButton(Dialog)
        self.ContinueBtn.setText(QtGui.QApplication.translate("Dialog", "Continue", None, QtGui.QApplication.UnicodeUTF8))
        self.ContinueBtn.setObjectName(_fromUtf8("ContinueBtn"))
        self.horizontalLayout_4.addWidget(self.ContinueBtn)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_4)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        pass


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_InitWindow()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

    
    

