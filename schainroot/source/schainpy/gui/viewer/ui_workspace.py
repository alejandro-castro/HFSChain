# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/roj-idl71/SignalChain/workspacev4.ui'
#
# Created: Wed Mar  6 14:59:06 2013
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Workspace(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(801, 309)
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.dirLabel = QtGui.QTextEdit(Dialog)
        self.dirLabel.setMaximumSize(QtCore.QSize(16777215, 75))
        self.dirLabel.setReadOnly(True)
        self.dirLabel.setHtml(QtGui.QApplication.translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\"> Select a workspace</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt; font-weight:600;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">  Signal Chain stores your projects in a folder called a workspace.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">  Choose a workspace folder to use for this session.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.dirLabel.setObjectName(_fromUtf8("dirLabel"))
        self.gridLayout.addWidget(self.dirLabel, 0, 0, 1, 2)
        self.line = QtGui.QFrame(Dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.dirWork = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.dirWork.setFont(font)
        self.dirWork.setText(QtGui.QApplication.translate("Dialog", "Workspace :", None, QtGui.QApplication.UnicodeUTF8))
        self.dirWork.setObjectName(_fromUtf8("dirWork"))
        self.gridLayout.addWidget(self.dirWork, 2, 0, 1, 1)
        self.dirComBox = QtGui.QComboBox(Dialog)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.dirComBox.setPalette(palette)
        self.dirComBox.setObjectName(_fromUtf8("dirComBox"))
        self.gridLayout.addWidget(self.dirComBox, 3, 0, 1, 1)
        self.dirToolPath = QtGui.QToolButton(Dialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.dirToolPath.setFont(font)
        self.dirToolPath.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.dirToolPath.setObjectName(_fromUtf8("dirToolPath"))
        self.gridLayout.addWidget(self.dirToolPath, 3, 1, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem2)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem3)
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.gridLayout.addLayout(self.horizontalLayout_3, 4, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem5 = QtGui.QSpacerItem(438, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.dirOkBtn = QtGui.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.dirOkBtn.setFont(font)
        self.dirOkBtn.setText(QtGui.QApplication.translate("Dialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.dirOkBtn.setObjectName(_fromUtf8("dirOkBtn"))
        self.horizontalLayout.addWidget(self.dirOkBtn)
        self.dirCancelBtn = QtGui.QPushButton(Dialog)
        self.dirCancelBtn.setText(QtGui.QApplication.translate("Dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.dirCancelBtn.setObjectName(_fromUtf8("dirCancelBtn"))
        self.horizontalLayout.addWidget(self.dirCancelBtn)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        pass


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Workspace()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

