# -*- coding: utf-8 -*-

"""
Module implementing InitWindow.
"""

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature
from PyQt4                 import QtCore
from PyQt4                 import QtGui

from viewer.ui_initwindow import Ui_InitWindow

class InitWindow(QDialog, Ui_InitWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle("ROJ-Signal Chain")
        self.setWindowIcon(QtGui.QIcon("figure/adn.jpg"))
    
    @pyqtSignature("")
    def on_ExitBtn_clicked(self):
        """
        Exit cierra la ventana de Bienvenida
        """
        self.close()
        
    @pyqtSignature("")
    def on_ContinueBtn_clicked(self):
        """
       Continue cierra la ventana de Bienvenida, a este evento se le complementa con la accion
       conectar con la ventana de configuracion de Workspace
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        self.accept()
