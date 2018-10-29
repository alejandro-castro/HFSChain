'''
Created on Feb 7, 2012

@author $Author: dsuarez $
@version $Id: Correlation.py 103 2012-05-10 02:34:42Z dsuarez $
'''
from JROData import JROData, Noise
from JROHeader import RadarControllerHeader, ProcessingHeader, SystemHeader, BasicHeader

class Correlation(JROData):
    '''
    classdocs
    '''
    
    data = None
    
    nLags = None
    
    lagsList = None
    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.m_RadarControllerHeader = RadarControllerHeader()
        
        self.m_ProcessingHeader = ProcessingHeader()
    
        self.m_SystemHeader = SystemHeader()
    
        self.m_BasicHeader = BasicHeader()
        
        self.m_NoiseObj = Noise()
        
        self.type = "Correlation"
        
        self.dataType = None
        
        self.nHeights = 0
        
        self.nChannels = 0
        
        self.channelList = None
        
        self.heightList = None
        
        self.flagNoData = True
        
        self.flagResetProcessing = False
        
        
        self.data = None
        
        self.nLags = 0
        
        self.tauList = None
        
        self.pairList = None
        