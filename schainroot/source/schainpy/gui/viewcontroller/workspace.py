# -*- coding: utf-8 -*-
import os
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtCore import pyqtSignal
from PyQt4 import QtGui, QtCore
from viewer.ui_workspace import Ui_Workspace
from os.path import  expanduser

class Workspace(QDialog, Ui_Workspace):
    """
    Class documentation goes here.
    """
  
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.dirList=[]
        self.setupUi(self)
        self.setWindowTitle("ROJ-Signal Chain")
        self.setWindowIcon(QtGui.QIcon("figure/adn.jpg"))
        #*#######   DIRECTORIO DE TRABAJO  #########*#
        #self.dirCmbBox.setItemText(0, QtGui.QApplication.translate("MainWindow", "C:\WorkSpaceGui", None, QtGui.QApplication.UnicodeUTF8))
        home=expanduser("~")
        self.dir=os.path.join(home,'schain_workspace')
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        self.dirComBox.addItem(self.dir)
        self.i=0
        
                  
    @pyqtSignature("")
    def on_dirToolPath_clicked(self):
        """
        Slot documentation goes here.
        """
        self.i +=1
        self.dirBrowse = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.dirComBox.addItem(self.dirBrowse)
        self.dirComBox.setCurrentIndex(self.i)



    @pyqtSignature("")
    def on_dirOkBtn_clicked(self):
        """
        VISTA DE INTERFAZ GRÃFICA
        """
        self.accept()
        #        self.close()
#               
    @pyqtSignature("")
    def on_dirCancelBtn_clicked(self):
        """
        Cerrar
        """
        self.close()

 
    

    
    