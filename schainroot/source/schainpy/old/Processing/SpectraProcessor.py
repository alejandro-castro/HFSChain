'''
Created on Feb 7, 2012

@author $Author: murco $
@version $Id: SpectraProcessor.py 172 2012-11-20 14:53:43Z murco $
'''
import os, sys
import numpy
import time

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.Spectra import Spectra
from IO.SpectraIO import SpectraWriter
from Graphics.SpectraPlot import Spectrum
from JRONoise import Noise

class SpectraProcessor:
    '''
    classdocs
    '''
    
    dataInObj = None        
    
    dataOutObj = None
        
    noiseObj = None
    
    integratorObjList = []
    
    decoderObjList = []
    
    writerObjList = []
    
    plotterObjList = []
    
    integratorObjIndex = None
    
    decoderObjIndex = None
    
    writerObjIndex = None
    
    plotterObjIndex = None
    
    buffer = None
    
    profIndex = 0
    
    nFFTPoints = None
    
    nChannels = None
    
    nHeights = None
    
    nPairs = None
    
    pairList = None

    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.integratorObjIndex = None
        self.decoderObjIndex = None
        self.writerObjIndex = None
        self.plotterObjIndex = None
        
        self.integratorObjList = []
        self.decoderObjList = []
        self.writerObjList = []
        self.plotterObjList = []
        
        self.noiseObj = None
        self.buffer = None
        self.profIndex = 0
        
    def setup(self, dataInObj=None, dataOutObj=None, nFFTPoints=None, pairList=None):
        
        if dataInObj == None:
            raise ValueError, ""
        
        if nFFTPoints == None:
            raise ValueError, ""
            
        self.dataInObj = dataInObj        
        
        if dataOutObj == None:
            dataOutObj = Spectra()
            
        self.dataOutObj = dataOutObj
        self.noiseObj = Noise()
        
        ##########################################
        self.nFFTPoints = nFFTPoints
        self.nChannels = self.dataInObj.nChannels
        self.nHeights = self.dataInObj.nHeights
        self.pairList = pairList
        if pairList != None:
            self.nPairs = len(pairList)
        else:
            self.nPairs = 0
        
        self.dataOutObj.heightList = self.dataInObj.heightList
        self.dataOutObj.channelIndexList = self.dataInObj.channelIndexList
        self.dataOutObj.m_BasicHeader = self.dataInObj.m_BasicHeader.copy()
        self.dataOutObj.m_ProcessingHeader = self.dataInObj.m_ProcessingHeader.copy()
        self.dataOutObj.radarControllerHeaderObj = self.dataInObj.radarControllerHeaderObj.copy()
        self.dataOutObj.systemHeaderObj = self.dataInObj.systemHeaderObj.copy()
        
        self.dataOutObj.dataType = self.dataInObj.dataType
        self.dataOutObj.nPairs = self.nPairs
        self.dataOutObj.nChannels = self.nChannels
        self.dataOutObj.nProfiles = self.nFFTPoints
        self.dataOutObj.nHeights = self.nHeights
        self.dataOutObj.nFFTPoints = self.nFFTPoints
        #self.dataOutObj.data = None
        
        self.dataOutObj.systemHeaderObj.numChannels = self.nChannels
        self.dataOutObj.systemHeaderObj.nProfiles = self.nFFTPoints
        
        self.dataOutObj.m_ProcessingHeader.totalSpectra = self.nChannels + self.nPairs 
        self.dataOutObj.m_ProcessingHeader.profilesPerBlock = self.nFFTPoints
        self.dataOutObj.m_ProcessingHeader.numHeights = self.nHeights
        self.dataOutObj.m_ProcessingHeader.shif_fft = True
        
        spectraComb = numpy.zeros( (self.nChannels+self.nPairs)*2,numpy.dtype('u1'))
        k = 0
        for i in range( 0,self.nChannels*2,2 ):
            spectraComb[i]   = k 
            spectraComb[i+1] = k
            k += 1
        
        k *= 2

        if self.pairList != None:
            
            for pair in self.pairList:
                spectraComb[k]   = pair[0] 
                spectraComb[k+1] = pair[1]
                k += 2    
            
        self.dataOutObj.m_ProcessingHeader.spectraComb = spectraComb
        
        return self.dataOutObj
    
    def init(self):
        
        self.nHeights = self.dataInObj.nHeights
        self.dataOutObj.nHeights = self.nHeights
        self.dataOutObj.heightList = self.dataInObj.heightList
        
        self.integratorObjIndex = 0
        self.decoderObjIndex = 0
        self.writerObjIndex = 0
        self.plotterObjIndex = 0
        
        if self.dataInObj.type == "Voltage":
            
            if self.buffer == None:
                self.buffer = numpy.zeros((self.nChannels,
                                           self.nFFTPoints,
                                           self.dataInObj.nHeights), 
                                          dtype='complex')
            
            self.buffer[:,self.profIndex,:] = self.dataInObj.data
            self.profIndex += 1
            
            if self.profIndex == self.nFFTPoints:
                self.__getFft()
                self.dataOutObj.flagNoData = False
                
                self.buffer = None
                self.profIndex = 0
                return
            
            self.dataOutObj.flagNoData = True
            
            return
        
        #Other kind of data
        if self.dataInObj.type == "Spectra":
            self.dataOutObj.copy(self.dataInObj)
            self.dataOutObj.flagNoData = False
            return
        
        raise ValueError, "The datatype is not valid"

    def __getFft(self):
        """
        Convierte valores de Voltaje a Spectra
        
        Affected:
            self.dataOutObj.data_spc
            self.dataOutObj.data_cspc
            self.dataOutObj.data_dc
            self.dataOutObj.heightList
            self.dataOutObj.m_BasicHeader
            self.dataOutObj.m_ProcessingHeader
            self.dataOutObj.radarControllerHeaderObj
            self.dataOutObj.systemHeaderObj
            self.profIndex  
            self.buffer
            self.dataOutObj.flagNoData
            self.dataOutObj.dataType
            self.dataOutObj.nPairs
            self.dataOutObj.nChannels
            self.dataOutObj.nProfiles
            self.dataOutObj.systemHeaderObj.numChannels
            self.dataOutObj.m_ProcessingHeader.totalSpectra 
            self.dataOutObj.m_ProcessingHeader.profilesPerBlock
            self.dataOutObj.m_ProcessingHeader.numHeights
            self.dataOutObj.m_ProcessingHeader.spectraComb
            self.dataOutObj.m_ProcessingHeader.shif_fft
        """
        
        if self.dataInObj.flagNoData:
            return 0
            
        fft_volt = numpy.fft.fft(self.buffer,axis=1)
        dc = fft_volt[:,0,:]
        
        #calculo de self-spectra
        fft_volt = numpy.fft.fftshift(fft_volt,axes=(1,))
        spc = fft_volt * numpy.conjugate(fft_volt)
        spc = spc.real
        
        blocksize = 0
        blocksize += dc.size
        blocksize += spc.size
        
        cspc = None
        pairIndex = 0
        if self.pairList != None:
            #calculo de cross-spectra
            cspc = numpy.zeros((self.nPairs, self.nFFTPoints, self.nHeights), dtype='complex')
            for pair in self.pairList:
                cspc[pairIndex,:,:] = numpy.abs(fft_volt[pair[0],:,:] * numpy.conjugate(fft_volt[pair[1],:,:]))
                pairIndex += 1
            blocksize += cspc.size
        
        self.dataOutObj.data_spc = spc
        self.dataOutObj.data_cspc = cspc
        self.dataOutObj.data_dc = dc
        self.dataOutObj.m_ProcessingHeader.blockSize = blocksize
        self.dataOutObj.m_BasicHeader.utc = self.dataInObj.m_BasicHeader.utc
        
#        self.getNoise()
        
    def addWriter(self,wrpath):
        objWriter = SpectraWriter(self.dataOutObj)
        objWriter.setup(wrpath)
        self.writerObjList.append(objWriter)
        
    def addPlotter(self,index=None):
        if index==None:
            index = self.plotterObjIndex
        
        plotObj = Spectrum(self.dataOutObj, index)
        self.plotterObjList.append(plotObj)
    
    def addIntegrator(self,N,timeInterval):
        
        objIncohInt = IncoherentIntegration(N,timeInterval)
        self.integratorObjList.append(objIncohInt)
    
    def writeData(self, wrpath):
        if self.dataOutObj.flagNoData:
                return 0
            
        if len(self.writerObjList) <= self.writerObjIndex:
            self.addWriter(wrpath)
        
        self.writerObjList[self.writerObjIndex].putData()
        
        self.writerObjIndex += 1
        
    def plotData(self,
                 xmin=None,
                 xmax=None,
                 ymin=None,
                 ymax=None,
                 zmin=None,
                 zmax=None,
                 titleList=None,
                 xlabelList=None,
                 ylabelList=None,
                 winTitle='',
                 colormap="br_green",
                 showColorbar=False,
                 showPowerProfile=False,
                 XAxisAsTime=False,
                 save=False,
                 index=None,
                 channelList=[]):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if len(self.plotterObjList) <= self.plotterObjIndex:
            self.addPlotter(index)
        
        self.plotterObjList[self.plotterObjIndex].plotData(xmin,
                                                           xmax,
                                                           ymin,
                                                           ymax,
                                                           zmin,
                                                           zmax,
                                                           titleList,
                                                           xlabelList,
                                                           ylabelList,
                                                           winTitle,
                                                           colormap,
                                                           showColorbar,
                                                           showPowerProfile,
                                                           XAxisAsTime,
                                                           save,
                                                           channelList)
        
        self.plotterObjIndex += 1
        
    def integrator(self, N=None, timeInterval=None):
        
        if self.dataOutObj.flagNoData:
                return 0
        
        if len(self.integratorObjList) <= self.integratorObjIndex:
            self.addIntegrator(N,timeInterval)
        
        myIncohIntObj = self.integratorObjList[self.integratorObjIndex]
        myIncohIntObj.exe(data=self.dataOutObj.data_spc,timeOfData=self.dataOutObj.m_BasicHeader.utc)
        
        if myIncohIntObj.isReady:
            self.dataOutObj.data_spc = myIncohIntObj.data
            self.dataOutObj.nAvg = myIncohIntObj.navg
            self.dataOutObj.m_ProcessingHeader.incoherentInt = self.dataInObj.m_ProcessingHeader.incoherentInt*myIncohIntObj.navg
            #print "myIncohIntObj.navg: ",myIncohIntObj.navg
            self.dataOutObj.flagNoData = False
            
            """Calcular el ruido"""
            self.getNoise()
        else:
            self.dataOutObj.flagNoData = True
        
        self.integratorObjIndex += 1
        
        
        
    def removeDC(self, type):
        
        if self.dataOutObj.flagNoData:
            return 0
    
    def removeInterference(self):
        
        if self.dataOutObj.flagNoData:
            return 0
    
    def removeSatellites(self):
        
        if self.dataOutObj.flagNoData:
            return 0
    
    def getNoise(self, type="hildebrand", parm=None):
        
        if parm == None:
            parm =self.dataOutObj.m_ProcessingHeader.incoherentInt
            
        self.noiseObj.setNoise(self.dataOutObj.data_spc)
        
        if type == "hildebrand":
            noise = self.noiseObj.byHildebrand(parm)
        
        if type == "window":
            noise = self.noiseObj.byWindow(parm)
        
        if type == "sort":
            noise = self.noiseObj.bySort(parm)
            
        self.dataOutObj.noise = noise
#        print 10*numpy.log10(noise)
    
    def selectChannels(self, channelList, pairList=[]):
        
        channelIndexList = []
        
        for channel in channelList:
            if channel in self.dataOutObj.channelList:
                index = self.dataOutObj.channelList.index(channel)
                channelIndexList.append(index)
                
        pairIndexList = []
        
        for pair in pairList:
            if pair in self.dataOutObj.pairList:
                index = self.dataOutObj.pairList.index(pair)
                pairIndexList.append(index)
        
        self.selectChannelsByIndex(channelIndexList, pairIndexList)
    
    def selectChannelsByIndex(self, channelIndexList, pairIndexList=[]):
        """
        Selecciona un bloque de datos en base a canales y pares segun el
        channelIndexList y el pairIndexList
        
        Input:
            channelIndexList :    lista de indices de los canales a seleccionar por ej.
                                 
                                     Si tenemos los canales
                                     
                                             self.channelList = (2,3,5,7)
                                    
                                    y deseamos escoger los canales (3,7) 
                                    entonces colocaremos el parametro
                                    
                                            channelndexList = (1,3)
                                  
            pairIndexList   :    tupla de indice depares que se desea selecionar por ej.
            
                                    Si tenemos los pares :
                                    
                                            ( (0,1), (0,2), (1,3), (2,5) )
                                    
                                    y deseamos seleccionar los pares ((0,2), (2,5))
                                    entonces colocaremos el parametro
                                    
                                            pairIndexList = (1,3)
            
        Affected:
            self.dataOutObj.data_spc
            self.dataOutObj.data_cspc
            self.dataOutObj.data_dc
            self.dataOutObj.nChannels
            self.dataOutObj.nPairs
            self.dataOutObj.m_ProcessingHeader.spectraComb
            self.dataOutObj.systemHeaderObj.numChannels
            
            self.dataOutObj.noise
        Return:
            None
        """
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if pairIndexList == []:
            pairIndexList = numpy.arange(len(self.dataOutObj.pairList))
               
        nChannels = len(channelIndexList)
        nPairs = len(pairIndexList)
        
        blocksize = 0
        #self spectra
        spc = self.dataOutObj.data_spc[channelIndexList,:,:]
        blocksize += spc.size
        
        cspc = None
        if pairIndexList != []:
            cspc = self.dataOutObj.data_cspc[pairIndexList,:,:]
            blocksize += cspc.size
            
        #DC channel
        dc = None
        if self.dataOutObj.m_ProcessingHeader.flag_dc:
            dc = self.dataOutObj.data_dc[channelIndexList,:]
            blocksize += dc.size
        
        #Almacenar las combinaciones de canales y cros espectros
        
        spectraComb = numpy.zeros( (nChannels+nPairs)*2,numpy.dtype('u1'))
        i = 0
        for spcChannel in channelIndexList:
            spectraComb[i]   = spcChannel 
            spectraComb[i+1] = spcChannel
            i += 2
        
        if pairList != None:
            for pair in pairList:
                spectraComb[i]   = pair[0] 
                spectraComb[i+1] = pair[1]
                i += 2
        
        #######
        
        self.dataOutObj.data_spc = spc
        self.dataOutObj.data_cspc = cspc
        self.dataOutObj.data_dc = dc
        self.dataOutObj.nChannels = nChannels 
        self.dataOutObj.nPairs = nPairs    

        self.dataOutObj.channelIndexList = channelIndexList

        self.dataOutObj.m_ProcessingHeader.spectraComb = spectraComb
        self.dataOutObj.m_ProcessingHeader.totalSpectra = nChannels + nPairs
        self.dataOutObj.systemHeaderObj.numChannels = nChannels
        self.dataOutObj.nChannels = nChannels
        self.dataOutObj.m_ProcessingHeader.blockSize = blocksize
        
        if cspc == None:
            self.dataOutObj.m_ProcessingHeader.flag_dc = False
        if dc == None:
            self.dataOutObj.m_ProcessingHeader.flag_cpsc = False
        
    def selectHeightsByValue(self, minHei, maxHei):
        """
        Selecciona un bloque de datos en base a un grupo de valores de alturas segun el rango
        minHei <= height <= maxHei
        
        Input:
            minHei    :    valor minimo de altura a considerar 
            maxHei    :    valor maximo de altura a considerar
            
        Affected:
            Indirectamente son cambiados varios valores a travez del metodo selectHeightsByIndex
            
        Return:
            None
        """
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if (minHei < self.dataOutObj.heightList[0]) or (minHei > maxHei):
            raise ValueError, "some value in (%d,%d) is not valid" % (minHei, maxHei)
        
        if (maxHei > self.dataOutObj.heightList[-1]):
            raise ValueError, "some value in (%d,%d) is not valid" % (minHei, maxHei)

        minIndex = 0
        maxIndex = 0
        data = self.dataOutObj.heightList
        
        for i,val in enumerate(data): 
            if val < minHei:
                continue
            else:
                minIndex = i;
                break
        
        for i,val in enumerate(data): 
            if val <= maxHei:
                maxIndex = i;
            else:
                break

        self.selectHeightsByIndex(minIndex, maxIndex)        
        
    def selectHeightsByIndex(self, minIndex, maxIndex):
        """
        Selecciona un bloque de datos en base a un grupo indices de alturas segun el rango
        minIndex <= index <= maxIndex
        
        Input:
            minIndex    :    valor minimo de altura a considerar 
            maxIndex    :    valor maximo de altura a considerar
            
        Affected:
            self.dataOutObj.data_spc
            self.dataOutObj.data_cspc
            self.dataOutObj.data_dc
            self.dataOutObj.heightList
            self.dataOutObj.nHeights
            self.dataOutObj.m_ProcessingHeader.numHeights
            self.dataOutObj.m_ProcessingHeader.blockSize
            self.dataOutObj.m_ProcessingHeader.firstHeight
            self.dataOutObj.radarControllerHeaderObj.numHeights
            
        Return:
            None
        """
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if (minIndex < 0) or (minIndex > maxIndex):
            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        if (maxIndex >= self.dataOutObj.nHeights):
            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        nChannels = self.dataOutObj.nChannels
        nPairs = self.dataOutObj.nPairs
        nProfiles = self.dataOutObj.nProfiles
        dataType = self.dataOutObj.dataType
        nHeights = maxIndex - minIndex + 1
        blockSize = 0

        #self spectra
        spc = self.dataOutObj.data_spc[:,:,minIndex:maxIndex+1]
        blockSize += spc.size

        #cross spectra
        cspc = None
        if self.dataOutObj.data_cspc != None:
            cspc = self.dataOutObj.data_cspc[:,:,minIndex:maxIndex+1]
            blockSize += cspc.size

        #DC channel
        dc = self.dataOutObj.data_dc[:,minIndex:maxIndex+1]
        blockSize += dc.size

        self.dataOutObj.data_spc = spc
        if cspc != None: 
            self.dataOutObj.data_cspc = cspc
        self.dataOutObj.data_dc = dc

        firstHeight = self.dataOutObj.heightList[minIndex]
        
        self.dataOutObj.nHeights = nHeights
        self.dataOutObj.m_ProcessingHeader.blockSize = blockSize
        self.dataOutObj.m_ProcessingHeader.numHeights = nHeights
        self.dataOutObj.m_ProcessingHeader.firstHeight = firstHeight
        self.dataOutObj.radarControllerHeaderObj.numHeights = nHeights
        
        self.dataOutObj.heightList = self.dataOutObj.heightList[minIndex:maxIndex+1] 


class IncoherentIntegration:

    integ_counter = None
    data = None
    navg = None
    buffer = None
    nIncohInt = None
    
    def __init__(self, N = None, timeInterval = None):
        """
        N 
        timeInterval - interval time [min], integer value
        """
        
        self.data = None
        self.navg = None
        self.buffer = None
        self.timeOut = None
        self.exitCondition = False
        self.isReady = False
        self.nIncohInt = N
        self.integ_counter = 0
        if timeInterval!=None:
            self.timeIntervalInSeconds = timeInterval * 60. #if (type(timeInterval)!=integer) -> change this line
        
        if ((timeInterval==None) and (N==None)):
             print 'N = None ; timeInterval = None'
             sys.exit(0)
        elif timeInterval == None:
            self.timeFlag = False
        else:
            self.timeFlag = True
            
            
    def exe(self,data,timeOfData):
        """
        data
        
        timeOfData [seconds]
        """

        if self.timeFlag:
            if self.timeOut == None:
                self.timeOut = timeOfData + self.timeIntervalInSeconds
            
            if timeOfData < self.timeOut:
                if self.buffer == None:
                    self.buffer = data
                else:
                    self.buffer = self.buffer + data
                self.integ_counter += 1
            else:
                self.exitCondition = True
                
        else:
            if self.integ_counter < self.nIncohInt:
                if self.buffer == None:
                    self.buffer = data
                else:
                    self.buffer = self.buffer + data
            
                self.integ_counter += 1

            if self.integ_counter == self.nIncohInt:
                self.exitCondition = True
                
        if self.exitCondition:
            self.data = self.buffer
            self.navg = self.integ_counter
            self.isReady = True
            self.buffer = None
            self.timeOut = None
            self.integ_counter = 0
            self.exitCondition = False
            
            if self.timeFlag:
                self.buffer = data
                self.timeOut = timeOfData + self.timeIntervalInSeconds
        else:
            self.isReady = False
            