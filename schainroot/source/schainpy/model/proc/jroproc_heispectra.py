import numpy

from jroproc_base import ProcessingUnit, Operation
from model.data.jrodata import SpectraHeis

class SpectraHeisProc(ProcessingUnit):
    
    def __init__(self):
        
        ProcessingUnit.__init__(self)
        
#        self.buffer = None
#        self.firstdatatime = None
#        self.profIndex = 0
        self.dataOut = SpectraHeis()

    def __updateObjFromInput(self):
        
        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.dstFlag = self.dataIn.dstFlag
        self.dataOut.errorCount = self.dataIn.errorCount
        self.dataOut.useLocalTime = self.dataIn.useLocalTime
        
        self.dataOut.radarControllerHeaderObj = self.dataIn.radarControllerHeaderObj.copy()#
        self.dataOut.systemHeaderObj = self.dataIn.systemHeaderObj.copy()#
        self.dataOut.channelList = self.dataIn.channelList
        self.dataOut.heightList = self.dataIn.heightList
#        self.dataOut.dtype = self.dataIn.dtype
        self.dataOut.dtype = numpy.dtype([('real','<f4'),('imag','<f4')])
#        self.dataOut.nHeights = self.dataIn.nHeights
#        self.dataOut.nChannels = self.dataIn.nChannels
        self.dataOut.nBaud = self.dataIn.nBaud
        self.dataOut.nCode = self.dataIn.nCode
        self.dataOut.code = self.dataIn.code
#        self.dataOut.nProfiles = 1
#        self.dataOut.nProfiles = self.dataOut.nFFTPoints
        self.dataOut.nFFTPoints = self.dataIn.nHeights
#        self.dataOut.channelIndexList = self.dataIn.channelIndexList
#        self.dataOut.flagNoData = self.dataIn.flagNoData
        self.dataOut.flagTimeBlock = self.dataIn.flagTimeBlock
        self.dataOut.utctime = self.dataIn.utctime
#        self.dataOut.utctime = self.firstdatatime
        self.dataOut.flagDecodeData = self.dataIn.flagDecodeData #asumo q la data esta decodificada
        self.dataOut.flagDeflipData = self.dataIn.flagDeflipData #asumo q la data esta sin flip
#        self.dataOut.flagShiftFFT = self.dataIn.flagShiftFFT
        self.dataOut.nCohInt = self.dataIn.nCohInt
        self.dataOut.nIncohInt = 1
#         self.dataOut.ippSeconds= self.dataIn.ippSeconds
        self.dataOut.windowOfFilter = self.dataIn.windowOfFilter
        
        self.dataOut.timeInterval = self.dataIn.timeInterval*self.dataOut.nIncohInt
#        self.dataOut.set=self.dataIn.set
#        self.dataOut.deltaHeight=self.dataIn.deltaHeight


    def __updateObjFromFits(self):
        self.dataOut.utctime = self.dataIn.utctime
        self.dataOut.channelIndexList = self.dataIn.channelIndexList
        
        self.dataOut.channelList = self.dataIn.channelList
        self.dataOut.heightList = self.dataIn.heightList
        self.dataOut.data_spc = self.dataIn.data
        self.dataOut.timeInterval = self.dataIn.timeInterval
        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.useLocalTime = True
#         self.dataOut.
#         self.dataOut.

    def __getFft(self):
           
        fft_volt = numpy.fft.fft(self.dataIn.data, axis=1)
        fft_volt = numpy.fft.fftshift(fft_volt,axes=(1,))
        spc = numpy.abs(fft_volt * numpy.conjugate(fft_volt))/(self.dataOut.nFFTPoints)
        self.dataOut.data_spc = spc

    def run(self):

        self.dataOut.flagNoData = True
        
        if self.dataIn.type == "Fits":
            self.__updateObjFromFits()
            self.dataOut.flagNoData = False
            return
        
        if self.dataIn.type == "SpectraHeis":
            self.dataOut.copy(self.dataIn)
            return
        
        if self.dataIn.type == "Voltage":
            self.__updateObjFromInput()
            self.__getFft()
            self.dataOut.flagNoData = False
                            
            return
        
        raise ValueError, "The type object %s is not valid"%(self.dataIn.type)
    
    
    def selectChannels(self, channelList):
        
        channelIndexList = []
        
        for channel in channelList:
            index = self.dataOut.channelList.index(channel)
            channelIndexList.append(index)
        
        self.selectChannelsByIndex(channelIndexList)
        
    def selectChannelsByIndex(self, channelIndexList):
        """
        Selecciona un bloque de datos en base a canales segun el channelIndexList 
        
        Input:
            channelIndexList    :    lista sencilla de canales a seleccionar por ej. [2,3,7] 
            
        Affected:
            self.dataOut.data
            self.dataOut.channelIndexList
            self.dataOut.nChannels
            self.dataOut.m_ProcessingHeader.totalSpectra
            self.dataOut.systemHeaderObj.numChannels
            self.dataOut.m_ProcessingHeader.blockSize
            
        Return:
            None
        """
    
        for channelIndex in channelIndexList:
            if channelIndex not in self.dataOut.channelIndexList:
                print channelIndexList
                raise ValueError, "The value %d in channelIndexList is not valid" %channelIndex
        
#         nChannels = len(channelIndexList)
            
        data_spc = self.dataOut.data_spc[channelIndexList,:]
        
        self.dataOut.data_spc = data_spc
        self.dataOut.channelList = [self.dataOut.channelList[i] for i in channelIndexList]
        
        return 1

class IncohInt4SpectraHeis(Operation):
    
    isConfig = False
    
    __profIndex = 0
    __withOverapping  = False
    
    __byTime = False
    __initime = None
    __lastdatatime = None
    __integrationtime = None
    
    __buffer = None
    
    __dataReady = False
    
    n = None
    
    
    def __init__(self):
        
        Operation.__init__(self)
#         self.isConfig = False
    
    def setup(self, n=None, timeInterval=None, overlapping=False):
        """
        Set the parameters of the integration class.
        
        Inputs:
        
            n        :    Number of coherent integrations
            timeInterval   :    Time of integration. If the parameter "n" is selected this one does not work
            overlapping    :    
            
        """
        
        self.__initime = None
        self.__lastdatatime = 0
        self.__buffer = None
        self.__dataReady = False
        
        
        if n == None and timeInterval == None:
            raise ValueError, "n or timeInterval should be specified ..." 
        
        if n != None:
            self.n = n
            self.__byTime = False
        else:
            self.__integrationtime = timeInterval #* 60. #if (type(timeInterval)!=integer) -> change this line
            self.n = 9999
            self.__byTime = True
        
        if overlapping:
            self.__withOverapping = True
            self.__buffer = None
        else:
            self.__withOverapping = False
            self.__buffer = 0
        
        self.__profIndex = 0
    
    def putData(self, data):
        
        """
        Add a profile to the __buffer and increase in one the __profileIndex
        
        """
            
        if not self.__withOverapping:
            self.__buffer += data.copy()
            self.__profIndex += 1            
            return
        
        #Overlapping data
        nChannels, nHeis = data.shape
        data = numpy.reshape(data, (1, nChannels, nHeis))
        
        #If the buffer is empty then it takes the data value
        if self.__buffer == None:
            self.__buffer = data
            self.__profIndex += 1
            return
        
        #If the buffer length is lower than n then stakcing the data value
        if self.__profIndex < self.n:
            self.__buffer = numpy.vstack((self.__buffer, data))
            self.__profIndex += 1
            return
        
        #If the buffer length is equal to n then replacing the last buffer value with the data value 
        self.__buffer = numpy.roll(self.__buffer, -1, axis=0)
        self.__buffer[self.n-1] = data
        self.__profIndex = self.n
        return
        
        
    def pushData(self):
        """
        Return the sum of the last profiles and the profiles used in the sum.
        
        Affected:
        
        self.__profileIndex
        
        """
        
        if not self.__withOverapping:
            data = self.__buffer
            n = self.__profIndex
        
            self.__buffer = 0
            self.__profIndex = 0
            
            return data, n
        
        #Integration with Overlapping
        data = numpy.sum(self.__buffer, axis=0)
        n = self.__profIndex
        
        return data, n
    
    def byProfiles(self, data):
        
        self.__dataReady = False
        avgdata = None
#         n = None
            
        self.putData(data)
        
        if self.__profIndex == self.n:
            
            avgdata, n = self.pushData()
            self.__dataReady = True
        
        return avgdata
    
    def byTime(self, data, datatime):
        
        self.__dataReady = False
        avgdata = None
        n = None
        
        self.putData(data)
        
        if (datatime - self.__initime) >= self.__integrationtime:
            avgdata, n = self.pushData()
            self.n = n
            self.__dataReady = True
        
        return avgdata
        
    def integrate(self, data, datatime=None):
        
        if self.__initime == None:
            self.__initime = datatime
        
        if self.__byTime:
            avgdata = self.byTime(data, datatime)
        else:
            avgdata = self.byProfiles(data)
        
        
        self.__lastdatatime = datatime
        
        if avgdata == None:
            return None, None
        
        avgdatatime = self.__initime
        
        deltatime = datatime -self.__lastdatatime
        
        if not self.__withOverapping:
            self.__initime = datatime
        else:
            self.__initime += deltatime
            
        return avgdata, avgdatatime
        
    def run(self, dataOut, **kwargs):
        
        if not self.isConfig:
            self.setup(**kwargs)
            self.isConfig = True
                    
        avgdata, avgdatatime = self.integrate(dataOut.data_spc, dataOut.utctime)
        
#        dataOut.timeInterval *= n
        dataOut.flagNoData = True
        
        if self.__dataReady:
            dataOut.data_spc = avgdata
            dataOut.nIncohInt *= self.n
#            dataOut.nCohInt *= self.n
            dataOut.utctime = avgdatatime
#             dataOut.timeInterval = dataOut.ippSeconds * dataOut.nIncohInt
#            dataOut.timeInterval = self.__timeInterval*self.n
            dataOut.flagNoData = False