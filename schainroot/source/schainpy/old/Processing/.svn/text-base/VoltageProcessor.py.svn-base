'''
Created on Feb 7, 2012

@author $Author: murco $
@version $Id: VoltageProcessor.py 172 2012-11-20 14:53:43Z murco $
'''

import os, sys
import numpy

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.Voltage import Voltage
from IO.VoltageIO import VoltageWriter
from Graphics.VoltagePlot import Osciloscope
from Graphics.VoltagePlot import RTI

class VoltageProcessor:
    '''
    classdocs
    '''
    
    dataInObj = None
    dataOutObj = None
    
    integratorObjIndex = None
    decoderObjIndex = None
    profSelectorObjIndex = None
    writerObjIndex = None
    plotterObjIndex = None
    flipIndex = None
    
    integratorObjList = []
    decoderObjList = []
    profileSelectorObjList = []
    writerObjList = []
    plotterObjList = []
    m_Voltage= Voltage()
    
    def __init__(self):
        '''
        Constructor
        '''
            
        self.integratorObjIndex = None
        self.decoderObjIndex = None
        self.profSelectorObjIndex = None
        self.writerObjIndex = None
        self.plotterObjIndex = None
        self.flipIndex = 1
        self.integratorObjList = []
        self.decoderObjList = []
        self.profileSelectorObjList = []
        self.writerObjList = []
        self.plotterObjList = []
        
    def setup(self, dataInObj=None, dataOutObj=None):
        
        self.dataInObj = dataInObj
        
        if dataOutObj == None:
            dataOutObj = Voltage()
        
        dataOutObj.copy(dataInObj)
        
        self.dataOutObj = dataOutObj
        
        return self.dataOutObj
        
    
    def init(self):
        
        self.integratorObjIndex = 0
        self.decoderObjIndex = 0
        self.profSelectorObjIndex = 0
        self.writerObjIndex = 0
        self.plotterObjIndex = 0
        self.dataOutObj.copy(self.dataInObj)
        
        if self.profSelectorObjIndex != None:
            for profSelObj in self.profileSelectorObjList:
                profSelObj.incIndex()
                
    def addWriter(self, wrpath):
        objWriter = VoltageWriter(self.dataOutObj)
        objWriter.setup(wrpath)
        self.writerObjList.append(objWriter)
    
    def addRti(self,index=None):
        if index==None:
            index = self.plotterObjIndex
        
        plotObj = RTI(self.dataOutObj, index)
        self.plotterObjList.append(plotObj)
    
    def addPlotter(self, index=None):
        if index==None:
            index = self.plotterObjIndex
        
        plotObj = Osciloscope(self.dataOutObj, index)
        self.plotterObjList.append(plotObj)
        
    def addIntegrator(self, N,timeInterval):
        
        objCohInt = CoherentIntegrator(N,timeInterval)
        self.integratorObjList.append(objCohInt)
    
    def addDecoder(self, code, ncode, nbaud):
        
        objDecoder = Decoder(code,ncode,nbaud)
        self.decoderObjList.append(objDecoder)
    
    def addProfileSelector(self, nProfiles):
        
        objProfSelector = ProfileSelector(nProfiles)
        self.profileSelectorObjList.append(objProfSelector)
        
    def writeData(self,wrpath):
        
        if self.dataOutObj.flagNoData:
            return 0
            
        if len(self.writerObjList) <= self.writerObjIndex:
            self.addWriter(wrpath)
        
        self.writerObjList[self.writerObjIndex].putData()
        
        self.writerObjIndex += 1
        
    def addScope(self,index=None):
        if index==None:
            index = self.plotterObjIndex
        
        plotObj = Osciloscope(self.dataOutObj, index)
        self.plotterObjList.append(plotObj)
        
    def plotScope(self,
                xmin=None,
                xmax=None,
                ymin=None,
                ymax=None,
                titleList=None,
                xlabelList=None,
                ylabelList=None,
                winTitle='',
                type="power",
                index=None):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if len(self.plotterObjList) <= self.plotterObjIndex:
            self.addScope(index)
        
        self.plotterObjList[self.plotterObjIndex].plotData(xmin,
                                                           xmax,
                                                           ymin,
                                                           ymax,
                                                           titleList,
                                                           xlabelList,
                                                           ylabelList,
                                                           winTitle,
                                                           type)
        
        self.plotterObjIndex += 1

    def plotRti(self,
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
                timezone='lt',
                npoints=1000.0,
                colormap="br_green",
                showColorbar=True,
                showPowerProfile=False,
                XAxisAsTime=True,
                save=False,
                index=None):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if len(self.plotterObjList) <= self.plotterObjIndex:
            self.addRti(index)
        
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
                                                           timezone,
                                                           npoints,
                                                           colormap,
                                                           showColorbar,
                                                           showPowerProfile,
                                                           XAxisAsTime,
                                                           save)
        
        self.plotterObjIndex += 1


    def plotData(self,xmin=None, xmax=None, ymin=None, ymax=None, type='iq', winTitle='', index=None):
        if self.dataOutObj.flagNoData:
            return 0
        
        if len(self.plotterObjList) <= self.plotterObjIndex:
            self.addPlotter(index)
        
        self.plotterObjList[self.plotterObjIndex].plotData(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,type=type, winTitle=winTitle)
        
        self.plotterObjIndex += 1
    
    def integrator(self, N=None, timeInterval=None):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if len(self.integratorObjList) <= self.integratorObjIndex:
            self.addIntegrator(N,timeInterval)
        
        myCohIntObj = self.integratorObjList[self.integratorObjIndex]
        myCohIntObj.exe(data=self.dataOutObj.data,timeOfData=self.dataOutObj.m_BasicHeader.utc)
        
        if myCohIntObj.isReady:
            self.dataOutObj.data = myCohIntObj.data
            self.dataOutObj.nAvg = myCohIntObj.navg
            self.dataOutObj.m_ProcessingHeader.coherentInt *= myCohIntObj.navg
            #print "myCohIntObj.navg: ",myCohIntObj.navg
            self.dataOutObj.flagNoData = False

        else:
            self.dataOutObj.flagNoData = True
        
        self.integratorObjIndex += 1
    
    def decoder(self,code=None, mode = 0):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if code == None:
            code = self.dataOutObj.radarControllerHeaderObj.code
        ncode, nbaud = code.shape
        
        if len(self.decoderObjList) <= self.decoderObjIndex:
            self.addDecoder(code,ncode,nbaud)
        
        myDecodObj = self.decoderObjList[self.decoderObjIndex]
        data, ndata = myDecodObj.exe(data=self.dataOutObj.data,mode=mode)
        
        self.dataOutObj.data = data
        self.dataOutObj.nHeights = ndata
        self.dataOutObj.heightList = self.dataInObj.heightList[:ndata]
        self.dataOutObj.flagNoData = False
        
        self.decoderObjIndex += 1

    
    def filterByHei(self, window):
        if window == None:
            window = self.dataOutObj.radarControllerHeaderObj.txA / self.dataOutObj.m_ProcessingHeader.deltaHeight[0]
        
        newdelta = self.dataOutObj.m_ProcessingHeader.deltaHeight[0] * window
        dim1 = self.dataOutObj.data.shape[0]
        dim2 = self.dataOutObj.data.shape[1]
        r = dim2 % window
        
        buffer = self.dataOutObj.data[:,0:dim2-r] 
        buffer = buffer.reshape(dim1,dim2/window,window)
        buffer = numpy.sum(buffer,2)
        self.dataOutObj.data = buffer
        
        self.dataOutObj.m_ProcessingHeader.deltaHeight = newdelta
        self.dataOutObj.m_ProcessingHeader.numHeights = buffer.shape[1]
        
        self.dataOutObj.nHeights = self.dataOutObj.m_ProcessingHeader.numHeights
        
        #self.dataOutObj.heightList es un numpy.array
        self.dataOutObj.heightList = numpy.arange(self.dataOutObj.m_ProcessingHeader.firstHeight[0],newdelta*self.dataOutObj.nHeights,newdelta)
        
    def deFlip(self):
        self.dataOutObj.data *= self.flipIndex
        self.flipIndex *= -1.
    
    def selectChannels(self, channelList):
        pass
        
    def selectChannelsByIndex(self, channelIndexList):
        """
        Selecciona un bloque de datos en base a canales segun el channelIndexList 
        
        Input:
            channelIndexList    :    lista sencilla de canales a seleccionar por ej. [2,3,7] 
            
        Affected:
            self.dataOutObj.data
            self.dataOutObj.channelIndexList
            self.dataOutObj.nChannels
            self.dataOutObj.m_ProcessingHeader.totalSpectra
            self.dataOutObj.systemHeaderObj.numChannels
            self.dataOutObj.m_ProcessingHeader.blockSize
            
        Return:
            None
        """
        if self.dataOutObj.flagNoData:
            return 0

        for channel in channelIndexList:
            if channel not in self.dataOutObj.channelIndexList:
                raise ValueError, "The value %d in channelIndexList is not valid" %channel
        
        nChannels = len(channelIndexList)
            
        data = self.dataOutObj.data[channelIndexList,:]
        
        self.dataOutObj.data = data
        self.dataOutObj.channelIndexList = channelIndexList
        self.dataOutObj.nChannels = nChannels
        
        self.dataOutObj.m_ProcessingHeader.totalSpectra = 0
        self.dataOutObj.systemHeaderObj.numChannels = nChannels
        self.dataOutObj.m_ProcessingHeader.blockSize = data.size
        return 1

    
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
            1 si el metodo se ejecuto con exito caso contrario devuelve 0
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
        return 1

    
    def selectHeightsByIndex(self, minIndex, maxIndex):
        """
        Selecciona un bloque de datos en base a un grupo indices de alturas segun el rango
        minIndex <= index <= maxIndex
        
        Input:
            minIndex    :    valor de indice minimo de altura a considerar 
            maxIndex    :    valor de indice maximo de altura a considerar
            
        Affected:
            self.dataOutObj.data
            self.dataOutObj.heightList 
            self.dataOutObj.nHeights
            self.dataOutObj.m_ProcessingHeader.blockSize
            self.dataOutObj.m_ProcessingHeader.numHeights
            self.dataOutObj.m_ProcessingHeader.firstHeight
            self.dataOutObj.radarControllerHeaderObj
            
        Return:
            1 si el metodo se ejecuto con exito caso contrario devuelve 0
        """
        if self.dataOutObj.flagNoData:
            return 0
        
        if (minIndex < 0) or (minIndex > maxIndex):
            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        if (maxIndex >= self.dataOutObj.nHeights):
            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        nHeights = maxIndex - minIndex + 1

        #voltage
        data = self.dataOutObj.data[:,minIndex:maxIndex+1]

        firstHeight = self.dataOutObj.heightList[minIndex]

        self.dataOutObj.data = data
        self.dataOutObj.heightList = self.dataOutObj.heightList[minIndex:maxIndex+1] 
        self.dataOutObj.nHeights = nHeights
        self.dataOutObj.m_ProcessingHeader.blockSize = data.size
        self.dataOutObj.m_ProcessingHeader.numHeights = nHeights
        self.dataOutObj.m_ProcessingHeader.firstHeight = firstHeight
        self.dataOutObj.radarControllerHeaderObj.numHeights = nHeights
        return 1
    
    def selectProfilesByValue(self,indexList, nProfiles):
        if self.dataOutObj.flagNoData:
            return 0
        
        if self.profSelectorObjIndex >= len(self.profileSelectorObjList):
            self.addProfileSelector(nProfiles)
        
        profileSelectorObj = self.profileSelectorObjList[self.profSelectorObjIndex]
        
        if not(profileSelectorObj.isProfileInList(indexList)):
            self.dataOutObj.flagNoData = True
            self.profSelectorObjIndex += 1
            return 0
        
        self.dataOutObj.flagNoData = False
        self.profSelectorObjIndex += 1
        
        return 1
    
    
    def selectProfilesByIndex(self, minIndex, maxIndex, nProfiles):
        """
        Selecciona un bloque de datos en base a un grupo indices de perfiles segun el rango
        minIndex <= index <= maxIndex
        
        Input:
            minIndex    :    valor de indice minimo de perfil a considerar 
            maxIndex    :    valor de indice maximo de perfil a considerar
            nProfiles   :    numero de profiles
            
        Affected:
            self.dataOutObj.flagNoData
            self.profSelectorObjIndex
            
        Return:
            1 si el metodo se ejecuto con exito caso contrario devuelve 0
        """
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if self.profSelectorObjIndex >= len(self.profileSelectorObjList):
            self.addProfileSelector(nProfiles)
        
        profileSelectorObj = self.profileSelectorObjList[self.profSelectorObjIndex]
        
        if not(profileSelectorObj.isProfileInRange(minIndex, maxIndex)):
            self.dataOutObj.flagNoData = True
            self.profSelectorObjIndex += 1
            return 0
        
        self.dataOutObj.flagNoData = False
        self.profSelectorObjIndex += 1
        
        return 1
    
    def selectNtxs(self, ntx):
        pass


class Decoder:

    data = None
    profCounter = 1
    nCode = None 
    nBaud = None
    codeIndex = 0
    code = None
    flag = False
    
    def __init__(self,code, ncode, nbaud):
        
        self.data = None
        self.ndata = None
        self.profCounter = 1
        self.nCode = ncode 
        self.nBaud = nbaud
        self.codeIndex = 0
        self.code = code #this is a List
        self.flag = False
            
    def exe(self, data, ndata=None, mode = 0):
        
        if ndata == None: ndata = data.shape[1] 
        
        if mode == 0:
            self.convolutionInFreq(data,ndata)
            
        if mode == 1:
            self.convolutionInTime(data, ndata)
        
        self.ndata = ndata - self.nBaud + 1
        
        return self.data, self.ndata
        
    def convolutionInFreq(self,data, ndata):
        
        newcode = numpy.zeros(ndata)    
        newcode[0:self.nBaud] = self.code[self.codeIndex]
        
        self.codeIndex += 1
        
        fft_data = numpy.fft.fft(data, axis=1)
        fft_code = numpy.conj(numpy.fft.fft(newcode))
        fft_code = fft_code.reshape(1,len(fft_code))
        
        conv = fft_data.copy()
        conv.fill(0)
        
        conv = fft_data*fft_code
            
        data = numpy.fft.ifft(conv,axis=1)
        self.data = data[:,:-self.nBaud+1]
        self.flag = True
        
        if self.profCounter == self.nCode:
            self.profCounter = 0
            self.codeIndex = 0            
            
        self.profCounter += 1
        
    def convolutionInTime(self, data, ndata):

        nchannel = data.shape[1]
        newcode = self.code[self.codeIndex]
        self.codeIndex += 1
        conv = data.copy()
        for i in range(nchannel):
            conv[i,:] = numpy.correlate(data[i,:], newcode)
            
        self.data = conv
        self.flag = True
        
        if self.profCounter == self.nCode:
            self.profCounter = 0
            self.codeIndex = 0            
            
        self.profCounter += 1

            
class CoherentIntegrator:
    
    integ_counter = None
    data = None
    navg = None
    buffer = None
    nCohInt = None
    
    def __init__(self, N=None,timeInterval=None):
        
        self.data = None
        self.navg = None
        self.buffer = None
        self.timeOut = None
        self.exitCondition = False
        self.isReady = False
        self.nCohInt = N
        self.integ_counter = 0
        if timeInterval!=None:
            self.timeIntervalInSeconds = timeInterval * 60. #if (type(timeInterval)!=integer) -> change this line
        
        if ((timeInterval==None) and (N==None)):
            raise ValueError, "N = None ; timeInterval = None"
        
        if timeInterval == None:
            self.timeFlag = False
        else:
            self.timeFlag = True
        
    def exe(self, data, timeOfData):
        
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
            if self.integ_counter < self.nCohInt:
                if self.buffer == None:
                    self.buffer = data
                else:
                    self.buffer = self.buffer + data
            
                self.integ_counter += 1

            if self.integ_counter == self.nCohInt:
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
            
        

class ProfileSelector:
    
    profileIndex = None
    # Tamanho total de los perfiles
    nProfiles = None
    
    def __init__(self, nProfiles):
        
        self.profileIndex = 0
        self.nProfiles = nProfiles
    
    def incIndex(self):
        self.profileIndex += 1
        
        if self.profileIndex >= self.nProfiles:
            self.profileIndex = 0
    
    def isProfileInRange(self, minIndex, maxIndex):
        
        if self.profileIndex < minIndex:
            return False
        
        if self.profileIndex > maxIndex:
            return False
        
        return True
    
    def isProfileInList(self, profileList):
        
        if self.profileIndex not in profileList:
            return False
        
        return True
        
    
        