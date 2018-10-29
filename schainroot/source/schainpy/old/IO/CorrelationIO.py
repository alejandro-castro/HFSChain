'''
Created on 23/01/2012

@author $Author: dsuarez $
@version $Id: CorrelationIO.py 103 2012-05-10 02:34:42Z dsuarez $
'''

import os, sys
import numpy
import glob
import fnmatch
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.JROHeader import *
from Model.Voltage import Voltage

from IO.JRODataIO import JRODataReader
from IO.JRODataIO import JRODataWriter


class CorrelationReader(JRODataReader):#JRODataReader para lectura de correlaciones en archivos HDF5
    
    def __init__(self):
        
        pass
    
class CorrelationWriter(JRODataWriter):#JRODataWriter para escritura de correlaciones en archivos HDF5
    
    def __init__(self):
        
        pass
    
    def puData(self):
        pass
    
    def writeBlock(self):
        pass