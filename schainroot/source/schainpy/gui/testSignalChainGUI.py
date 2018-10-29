#!/usr/bin/python
# -*- coding: utf-8 -*-'
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication
#from PyQt4.QtCore import pyqtSignature

from viewcontroller.initwindow import InitWindow
from viewcontroller.basicwindow import BasicWindow
from viewcontroller.workspace import Workspace

def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    
    Welcome=InitWindow()
    if not Welcome.exec_(): 
        sys.exit(-1) 

    WorkPathspace=Workspace()
    if not WorkPathspace.exec_(): 
          sys.exit(-1)

    MainGUI=BasicWindow()
    MainGUI.setWorkSpaceGUI(WorkPathspace.dirComBox.currentText())  
    MainGUI.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()