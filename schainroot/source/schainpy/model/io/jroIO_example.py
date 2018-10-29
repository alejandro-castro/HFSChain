'''
Created on Jul 3, 2014

@author: roj-idl71
'''

import os

from schainpy.model.data.jrodata import Voltage
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation

class Reader(ProcessingUnit):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        ProcessingUnit.__init__(self)
        
#         self.dataIn = None
#         
#         self.isConfig = False
        
        #Is really necessary create the output object in the initializer
        self.dataOut = Voltage()
        
    def setup(self, path = None,
                    startDate = None, 
                    endDate = None, 
                    startTime = None, 
                    endTime = None, 
                    set = None, 
                    expLabel = "", 
                    ext = None, 
                    online = False,
                    delay = 60,
                    walk = True):
        '''
        In this method we should set all initial parameters.
        
        '''
        
        self.isConfig = True
        
    def run(self, **kwargs):
        '''
        This method will be called many times so here you should put all your code
        '''
        
        if not self.isConfig:
            self.setup(**kwargs)
            
class Writer(Operation):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.dataOut = None
        
        self.isConfig = False
    
    def setup(self, dataIn, path, blocksPerFile, set=0, ext=None):
        '''
        In this method we should set all initial parameters.
        
        Input:
            dataIn        :        Input data will also be outputa data
        
        '''
        self.dataOut = dataIn
        
        
        
        
        
        self.isConfig = True
        
        return
        
    def run(self, dataIn, **kwargs):
        '''
        This method will be called many times so here you should put all your code
        
        Inputs:
        
            dataIn        :        object with the data
            
        '''
        
        if not self.isConfig:
            self.setup(dataIn, **kwargs)
        