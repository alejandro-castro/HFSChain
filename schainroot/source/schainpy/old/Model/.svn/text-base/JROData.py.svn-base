'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''
import copy
import numpy

from JROHeader import RadarControllerHeader, ProcessingHeader, SystemHeader, BasicHeader

class Data:
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        raise ValueError, "This class has not been implemented"
    
    def copy(self, objIn=None):
        
        if objIn == None:
            return copy.deepcopy(self)
        
        for key in objIn.__dict__.keys():
            self.__dict__[key] = objIn.__dict__[key]
    
    def deepcopy(self):
        
        return copy.deepcopy(self)
    


class JROData(Data):
    '''
    classdocs
    '''
    
    radarControllerHeaderObj = RadarControllerHeader()
    
    m_ProcessingHeader = ProcessingHeader()
    
    systemHeaderObj = SystemHeader()
    
    m_BasicHeader = BasicHeader()
    
    noise = None
    
    type = None
    
    dataType = None
    
    nHeights = None
    
    nProfiles = None

    nChannels = None    
    
    heightList = None
    
    channelList = None
    
    channelIndexList = None
    
    pairList = None
    
    flagNoData = False
    
    flagResetProcessing = False
            
    def __init__(self):
        '''
        Constructor
        '''
        raise ValueError, "This class has not been implemented"
    
    def updateHeaderFromObj(self):
        
        xi = self.heightList[0]
        step = self.heightList[1] - self.heightList[0]
        
        self.m_ProcessingHeader.firstHeight = xi
        self.m_ProcessingHeader.deltaHeight = step
        
        self.m_ProcessingHeader.numHeights = self.nHeights
        self.systemHeaderObj.numChannels = self.nChannels
        self.systemHeaderObj.numProfiles = self.nProfiles 
   
    def updateObjFromHeader(self):
        
        xi = self.m_ProcessingHeader.firstHeight
        step = self.m_ProcessingHeader.deltaHeight
        xf = xi + self.m_ProcessingHeader.numHeights*step
        
        self.heightList = numpy.arange(xi, xf, step)        
        self.channelIndexList = numpy.arange(self.systemHeaderObj.numChannels)
        self.channelList = numpy.arange(self.systemHeaderObj.numChannels)
        
        self.nHeights = len(self.heightList)
        self.nProfiles = self.systemHeaderObj.numProfiles
        self.nChannels = len(self.channelList)
        