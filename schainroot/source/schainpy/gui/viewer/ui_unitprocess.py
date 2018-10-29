# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\alex\ericworkspace\UIDOS\unitProcess.ui'
#
# Created: Tue Dec 18 15:34:51 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_UnitProcess(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(212, 181)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.comboInputBox = QtGui.QComboBox(self.centralWidget)
        self.comboInputBox.setGeometry(QtCore.QRect(80, 50, 121, 22))
        self.comboInputBox.setObjectName(_fromUtf8("comboInputBox"))
        self.comboTypeBox = QtGui.QComboBox(self.centralWidget)
        self.comboTypeBox.setGeometry(QtCore.QRect(80, 90, 121, 22))
        self.comboTypeBox.setObjectName(_fromUtf8("comboTypeBox"))
        self.comboTypeBox.addItem(_fromUtf8(""))
        self.comboTypeBox.addItem(_fromUtf8(""))
        self.comboTypeBox.addItem(_fromUtf8(""))
        self.nameUP = QtGui.QLabel(self.centralWidget)
        self.nameUP.setGeometry(QtCore.QRect(50, 20, 111, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.nameUP.setFont(font)
        self.nameUP.setObjectName(_fromUtf8("nameUP"))
        self.inputLabel = QtGui.QLabel(self.centralWidget)
        self.inputLabel.setGeometry(QtCore.QRect(20, 50, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.inputLabel.setFont(font)
        self.inputLabel.setObjectName(_fromUtf8("inputLabel"))
        self.typeLabel = QtGui.QLabel(self.centralWidget)
        self.typeLabel.setGeometry(QtCore.QRect(20, 90, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.typeLabel.setFont(font)
        self.typeLabel.setObjectName(_fromUtf8("typeLabel"))
        self.unitPokbut = QtGui.QPushButton(self.centralWidget)
        self.unitPokbut.setGeometry(QtCore.QRect(10, 130, 91, 23))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.unitPokbut.setFont(font)
        self.unitPokbut.setObjectName(_fromUtf8("unitPokbut"))
        self.unitPcancelbut = QtGui.QPushButton(self.centralWidget)
        self.unitPcancelbut.setGeometry(QtCore.QRect(110, 130, 91, 23))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.unitPcancelbut.setFont(font)
        self.unitPcancelbut.setObjectName(_fromUtf8("unitPcancelbut"))
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.comboTypeBox.setItemText(0, QtGui.QApplication.translate("MainWindow", "Voltage", None, QtGui.QApplication.UnicodeUTF8))
        self.comboTypeBox.setItemText(1, QtGui.QApplication.translate("MainWindow", "Spectra", None, QtGui.QApplication.UnicodeUTF8))
        self.comboTypeBox.setItemText(2, QtGui.QApplication.translate("MainWindow", "Correlation", None, QtGui.QApplication.UnicodeUTF8))
        self.nameUP.setText(QtGui.QApplication.translate("MainWindow", "PROCESSING UNIT", None, QtGui.QApplication.UnicodeUTF8))
        self.inputLabel.setText(QtGui.QApplication.translate("MainWindow", "Input:", None, QtGui.QApplication.UnicodeUTF8))
        self.typeLabel.setText(QtGui.QApplication.translate("MainWindow", "Type:", None, QtGui.QApplication.UnicodeUTF8))
        self.unitPokbut.setText(QtGui.QApplication.translate("MainWindow", "Ok", None, QtGui.QApplication.UnicodeUTF8))
        self.unitPcancelbut.setText(QtGui.QApplication.translate("MainWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_UnitProcess()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

