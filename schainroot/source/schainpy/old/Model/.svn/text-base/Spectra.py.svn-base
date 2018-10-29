'''
Created on Feb 7, 2012

@author $Author: dsuarez $
@version $Id: Spectra.py 110 2012-07-19 15:18:18Z dsuarez $
'''

from JROData import JROData
from JROHeader import RadarControllerHeader, ProcessingHeader, SystemHeader, BasicHeader

class Spectra(JROData):
    '''
    classdocs
    '''
    
    data_spc = None
    
    data_cspc = None
    
    data_dc = None
    
    nFFTPoints = None
    
    nPairs = None
    
    pairsList = None
    

    def __init__(self):
        '''
        Constructor
        '''
        
        self.m_RadarControllerHeader = RadarControllerHeader()
        
        self.m_ProcessingHeader = ProcessingHeader()
    
        self.m_SystemHeader = SystemHeader()
    
        self.m_BasicHeader = BasicHeader()
        
        self.type = "Spectra"
        
        self.dataType = None
        
        self.nHeights = 0
        
        self.nChannels = 0
        
        self.channelList = None
        
        self.heightList = None
        
        self.flagNoData = True
        
        self.flagResetProcessing = False
        
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
        self.data_spc = None
        
        self.data_cspc = None
        
        self.data_dc = None
        
        self.nFFTPoints = None
        
        self.nAvg = None
        
        self.nPairs = 0
        
        self.pairsList = None
        
        
        
        