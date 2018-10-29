'''
Created on Feb 7, 2012

@author $Author: dsuarez $
@version $Id: Voltage.py 110 2012-07-19 15:18:18Z dsuarez $
'''

from JROData import JROData
from JROHeader import RadarControllerHeader, ProcessingHeader, SystemHeader, BasicHeader

class Voltage(JROData):
    '''
    classdocs
    '''
    
    data = None
    
    nProfiles = None
    
    profileIndex = None
    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.m_RadarControllerHeader = RadarControllerHeader()
        
        self.m_ProcessingHeader = ProcessingHeader()
    
        self.m_SystemHeader = SystemHeader()
    
        self.m_BasicHeader = BasicHeader()
        
        self.type = "Voltage"
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
        self.data = None
        
        self.dataType = None
        
        self.nHeights = 0
        
        self.nChannels = 0
        
        self.channelList = None
        
        self.heightList = None
        
        self.flagNoData = True
        
        self.flagResetProcessing = False
        
        self.nAvg = None
        
        self.profileIndex = None
        
        self.nProfiles = None
        
        
        