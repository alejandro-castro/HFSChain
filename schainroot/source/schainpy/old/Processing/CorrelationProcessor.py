'''
Created on Feb 7, 2012

@author $Author: dsuarez $
@version $Id: CorrelationProcessor.py 103 2012-05-10 02:34:42Z dsuarez $
'''

import os, sys
import numpy

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.Correlation import Correlation
from IO.CorrelationIO import CorrelationWriter
#from Graphics.CorrelationPlot import Correlator


from Model.Voltage import Voltage
from Model.Spectra import Spectra

class CorrelationProcessor:
    '''
    classdocs
    '''
    
    integratorIndex = None
    writerIndex = None
    plotterIndex = None
    
    lagsList = None
    
    nLags = None
    tauList = None
    pairList = None
    indexTau = None
    
    
    def __init__(self,dataInObj, dataOutObj=None):
        '''
        Constructor
        '''
        self.dataInObj = dataInObj
        
        if dataOutObj == None:
            self.dataOutObj = Correlation()
        else:
            self.dataOutObj = dataOutObj
        
        self.indexTau = 0
        self.buffer = None
        
    def init(self,pairList=None,tauList=None):
        
        self.integratorIndex = 0
        self.writerIndex = 0
        self.plotterIndex = 0
        
        self.pairList = pairList
        self.tauList = tauList
        
        if ( isinstance(self.dataInObj, Voltage) ):
            self.__getCorrelation()
        
        if ( isinstance(self.dataInObj, Spectra) ):
            sys.exit(0)
            
        if ( isinstance(self.dataInObj, Correlation) ):
            sel.__getCopy()
            
    def __getCorrelation(self):
        if self.dataInObj.flagNoData:
            return 0
        
        if self.tauList == None:   # se lee el tauList desde el archivo
            flip = None         
            if self.dataInObj.m_RadarControllerHeader.flip1 != None:
                flip = self.dataInObj.m_RadarControllerHeader.flip1
            
            if self.dataInObj.m_RadarControllerHeader.flip2 != None:
                flip = self.dataInObj.m_RadarControllerHeader.flip2
            
            if flip == None:
                flip = 2
                print 'flip is None --> flip = %d '%flip
                
            ntaus = self.dataInObj.m_RadarControllerHeader.numTaus
            taus = self.dataInObj.m_RadarControllerHeader.Taus.reshape(ntaus/flip,flip)
            
            index = 0
            self.tauList = taus[:,index]
            print 'tauList is None --> tauList = obj.m_RadarControllerHeader.Taus[:,%d]'%index
            
            self.nLags = len(self.tauList)

        if self.pairList == None:
            self.pairList = [(0,0)] # por defecto calcula la AutoCorrelacion de una canal
        
        self.dataOutObj.tauList = self.tauList
        self.dataOutObj.nLags = self.nLags
        self.dataOutObj.pairList = self.pairList
         
        if self.buffer == None:
            nhei = self.dataInObj.nHeights
            npairList = len(self.pairList)
            self.buffer = numpy.zeros((self.nLags,nhei,npairList),dtype='complex')
        
        bufferZ = numpy.zeros((npairList,self.dataInObj.nHeights),dtype='complex')
            
        indexHeight = self.tauList[self.indexTau] / self.dataInObj.m_ProcessingHeader.deltaHeight
        
        countPair = 0
    
        # make (signalA*signalB'), where signalA: channel without delay, signalB: channel with delay,  
        for pair in self.pairList:
            bufferZ[countPair,0:self.dataInObj.nHeights-indexHeight] = self.dataInObj.data[pair[1],indexHeight:self.dataInObj.nHeights]
            signalA = self.dataInObj.data[pair[0],:]
            signalB = bufferZ[countPair,:]
            data = signalA * numpy.conjugate(signalB)
            self.buffer[self.indexTau,:,countPair] = data
            countPair += 1
            
        # change index Tau and lagCounter
        self.indexTau += 1
        if self.indexTau >= self.nLags:
            self.indexTau = 0
            self.dataOutObj.data = self.buffer
            self.buffer = None
            self.dataOutObj.flagNoData = False
        else:
            self.dataOutObj.flagNoData = True    
    

    def addIntegrator(self):
        pass
    
    def addWriter(self):
        pass
    
    def addPlotter(self):
        pass
    
class Integrator():
    def __init__(self):
        pass

