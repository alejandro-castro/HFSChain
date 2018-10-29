import numpy

from jroproc_base import ProcessingUnit, Operation
from model.data.jrodata import Correlation

class CorrelationProc(ProcessingUnit):
    
    def __init__(self):
        
        ProcessingUnit.__init__(self)
        
        self.objectDict = {}
        self.buffer = None
        self.firstdatatime = None
        self.profIndex = 0
        self.dataOut = Correlation()
    
    def __updateObjFromInput(self):
        
        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.dstFlag = self.dataIn.dstFlag
        self.dataOut.errorCount = self.dataIn.errorCount
        self.dataOut.useLocalTime = self.dataIn.useLocalTime
        
        self.dataOut.radarControllerHeaderObj = self.dataIn.radarControllerHeaderObj.copy()
        self.dataOut.systemHeaderObj = self.dataIn.systemHeaderObj.copy()
        self.dataOut.channelList = self.dataIn.channelList
        self.dataOut.heightList = self.dataIn.heightList
        self.dataOut.dtype = numpy.dtype([('real','<f4'),('imag','<f4')])
#         self.dataOut.nHeights = self.dataIn.nHeights
#         self.dataOut.nChannels = self.dataIn.nChannels
        self.dataOut.nBaud = self.dataIn.nBaud
        self.dataOut.nCode = self.dataIn.nCode
        self.dataOut.code = self.dataIn.code
#        self.dataOut.nProfiles = self.dataOut.nFFTPoints
        self.dataOut.flagTimeBlock = self.dataIn.flagTimeBlock
        self.dataOut.utctime = self.firstdatatime
        self.dataOut.flagDecodeData = self.dataIn.flagDecodeData #asumo q la data esta decodificada
        self.dataOut.flagDeflipData = self.dataIn.flagDeflipData #asumo q la data esta sin flip
#        self.dataOut.nCohInt = self.dataIn.nCohInt
#        self.dataOut.nIncohInt = 1
        self.dataOut.ippSeconds = self.dataIn.ippSeconds
#        self.dataOut.windowOfFilter = self.dataIn.windowOfFilter
        
        self.dataOut.timeInterval = self.dataIn.timeInterval*self.dataOut.nPoints
        
        
    def removeDC(self, jspectra):
        
        nChannel = jspectra.shape[0]
        
        for i in range(nChannel):
            jspectra_tmp = jspectra[i,:,:]
            jspectra_DC = numpy.mean(jspectra_tmp,axis = 0)
            
            jspectra_tmp = jspectra_tmp - jspectra_DC
            jspectra[i,:,:] = jspectra_tmp
           
        return jspectra
    
    
    def removeNoise(self, mode = 2):
        indR = numpy.where(self.dataOut.lagR == 0)[0][0]
        indT = numpy.where(self.dataOut.lagT == 0)[0][0]
        
        jspectra = self.dataOut.data_corr[:,:,indR,:]
        
        num_chan = jspectra.shape[0]
        num_hei = jspectra.shape[2]
             
        freq_dc = indT
        ind_vel = numpy.array([-2,-1,1,2]) + freq_dc
             
        NPot = self.dataOut.getNoise(mode)
        jspectra[:,freq_dc,:] = jspectra[:,freq_dc,:] - NPot 
        SPot = jspectra[:,freq_dc,:]
        pairsAutoCorr = self.dataOut.getPairsAutoCorr()
#         self.dataOut.signalPotency = SPot
        self.dataOut.noise = NPot
        self.dataOut.SNR = (SPot/NPot)[pairsAutoCorr]
        self.dataOut.data_corr[:,:,indR,:] = jspectra                
                        
        return 1
    

    def calculateNormFactor(self):

        pairsList = self.dataOut.pairsList
        pairsAutoCorr = self.dataOut.pairsAutoCorr
        nHeights = self.dataOut.nHeights
        nPairs = len(pairsList)
        normFactor = numpy.zeros((nPairs,nHeights))

        indR = numpy.where(self.dataOut.lagR == 0)[0][0]
        indT = numpy.where(self.dataOut.lagT == 0)[0][0]
        
        for l in range(len(pairsList)):    
            firstChannel = pairsList[l][0]
            secondChannel = pairsList[l][1]
            
            AC1 = pairsAutoCorr[firstChannel]
            AC2 = pairsAutoCorr[secondChannel]
            
            if (AC1 >= 0 and AC2 >= 0):

                data1 = numpy.abs(self.dataOut.data_corr[AC1,:,indR,:])    
                data2 = numpy.abs(self.dataOut.data_corr[AC2,:,indR,:])
                maxim1 = data1.max(axis = 0)
                maxim2 = data1.max(axis = 0)
                maxim = numpy.sqrt(maxim1*maxim2)
            else:
                #In case there is no autocorrelation for the pair
                data = numpy.abs(self.dataOut.data_corr[l,:,indR,:]) 
                maxim = numpy.max(data, axis = 0)
                
            normFactor[l,:] = maxim    
                    
        self.dataOut.normFactor = normFactor
        
        return 1
    
    def run(self, lagT=None, lagR=None, pairsList=None, 
             nPoints=None, nAvg=None, bufferSize=None,
             fullT = False, fullR = False, removeDC = False):
        
        self.dataOut.flagNoData = True
        
        if self.dataIn.type == "Correlation":
            
            self.dataOut.copy(self.dataIn)
            
            return
        
        if self.dataIn.type == "Voltage":
            
            if pairsList == None:
                pairsList = [numpy.array([0,0])]
  
            if nPoints == None:
                nPoints = 128          
            #------------------------------------------------------------
            #Condicionales para calcular Correlaciones en Tiempo y Rango
            if fullT:
                lagT = numpy.arange(nPoints*2 - 1) - nPoints + 1
            elif lagT == None:
                lagT = numpy.array([0])
            else:
                lagT = numpy.array(lagT)
               
            if fullR:
                lagR = numpy.arange(self.dataOut.nHeights)
            elif lagR == None:
                lagR = numpy.array([0])
            #-------------------------------------------------------------

            if nAvg == None:
                nAvg = 1
            
            if bufferSize == None:
                bufferSize = 0
            
            deltaH = self.dataIn.heightList[1] - self.dataIn.heightList[0]
            self.dataOut.lagR = numpy.round(numpy.array(lagR)/deltaH)
            self.dataOut.pairsList = pairsList
            self.dataOut.nPoints = nPoints 
#             channels = numpy.sort(list(set(list(itertools.chain.from_iterable(pairsList)))))
            
            if self.buffer == None:
                
                self.buffer = numpy.zeros((self.dataIn.nChannels,self.dataIn.nProfiles,self.dataIn.nHeights),dtype='complex')
            
            
            self.buffer[:,self.profIndex,:] = self.dataIn.data.copy()[:,:]
            
            self.profIndex += 1
            
            if self.firstdatatime == None:
                
                self.firstdatatime = self.dataIn.utctime
            
            if self.profIndex == nPoints:
                     
                tmp = self.buffer[:,0:nPoints,:]
                self.buffer = None
                self.buffer = tmp
              
                #---------------    Remover DC    ------------
                if removeDC:
                    self.buffer = self.removeDC(self.buffer)
                #---------------------------------------------
                self.dataOut.data_volts = self.buffer  
                self.__updateObjFromInput()
                self.dataOut.data_corr = numpy.zeros((len(pairsList),                                                
                                                 len(lagT),len(lagR),
                                                 self.dataIn.nHeights),
                                                dtype='complex')
         
                for l in range(len(pairsList)):
                    
                    firstChannel = pairsList[l][0]
                    secondChannel = pairsList[l][1]
                    
                    tmp = None
                    tmp = numpy.zeros((len(lagT),len(lagR),self.dataIn.nHeights),dtype='complex')
                    
                    for t in range(len(lagT)):
                        
                        for r in range(len(lagR)):
                            
                            idxT = lagT[t]
                            idxR = lagR[r]                       
                            
                            if idxT >= 0:
                                vStacked = numpy.vstack((self.buffer[secondChannel,idxT:,:],
                                                         numpy.zeros((idxT,self.dataIn.nHeights),dtype='complex')))
                            else:
                                vStacked = numpy.vstack((numpy.zeros((-idxT,self.dataIn.nHeights),dtype='complex'),
                                                         self.buffer[secondChannel,:(nPoints + idxT),:]))
                                 
                            if idxR >= 0:
                                hStacked = numpy.hstack((vStacked[:,idxR:],numpy.zeros((nPoints,idxR),dtype='complex')))
                            else:
                                hStacked = numpy.hstack((numpy.zeros((nPoints,-idxR),dtype='complex'),vStacked[:,(self.dataOut.nHeights + idxR)]))
                                                    
                                     
                            tmp[t,r,:] = numpy.sum((numpy.conjugate(self.buffer[firstChannel,:,:])*hStacked),axis=0)
                             
  
                            hStacked = None
                            vStacked = None
                    
                    self.dataOut.data_corr[l,:,:,:] = tmp[:,:,:]
                
                #Se Calcula los factores de Normalizacion
                self.dataOut.pairsAutoCorr = self.dataOut.getPairsAutoCorr()
                self.dataOut.lagT = lagT*self.dataIn.ippSeconds*self.dataIn.nCohInt
                self.dataOut.lagR = lagR
                  
                self.calculateNormFactor()   
                
                self.dataOut.flagNoData = False
                self.buffer = None
                self.firstdatatime = None
                self.profIndex = 0
                
                return