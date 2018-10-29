import numpy

class Beam:
    def __init__(self):
        self.codeList = []
        self.azimuthList = []
        self.zenithList = [] 


class AMISR:
    def __init__(self):
        self.flagNoData = True
        self.data = None
        self.utctime = None
        self.type = "AMISR"
        
        #propiedades para compatibilidad con Voltages
        self.timeZone = 0#timezone like jroheader, difference in minutes between UTC and localtime 
        self.dstFlag = 0#self.dataIn.dstFlag
        self.errorCount = 0#self.dataIn.errorCount
        self.useLocalTime = True#self.dataIn.useLocalTime
        
        self.radarControllerHeaderObj = None#self.dataIn.radarControllerHeaderObj.copy()
        self.systemHeaderObj = None#self.dataIn.systemHeaderObj.copy()
        self.channelList = [0]#self.dataIn.channelList esto solo aplica para el caso de AMISR
        self.dtype = numpy.dtype([('real','<f4'),('imag','<f4')])
        
        self.flagTimeBlock = None#self.dataIn.flagTimeBlock
        #self.utctime = #self.firstdatatime
        self.flagDecodeData = None#self.dataIn.flagDecodeData #asumo q la data esta decodificada
        self.flagDeflipData = None#self.dataIn.flagDeflipData #asumo q la data esta sin flip

        self.nCohInt = 1#self.dataIn.nCohInt
        self.nIncohInt = 1
        self.ippSeconds = None#self.dataIn.ippSeconds, segun el filename/Setup/Tufile
        self.windowOfFilter = None#self.dataIn.windowOfFilter
        
        self.timeInterval = None#self.dataIn.timeInterval*self.dataOut.nFFTPoints*self.dataOut.nIncohInt
        self.frequency = None#self.dataIn.frequency
        self.realtime = 0#self.dataIn.realtime
        
        #actualizar en la lectura de datos
        self.heightList = None#self.dataIn.heightList
        self.nProfiles = None#Number of samples or nFFTPoints
        self.nRecords = None
        self.nBeams = None
        self.nBaud = None#self.dataIn.nBaud
        self.nCode = None#self.dataIn.nCode
        self.code = None#self.dataIn.code
        
        #consideracion para los Beams
        self.beamCodeDict = None
        self.beamRangeDict = None
        self.beamcode = None
        self.azimuth = None
        self.zenith = None
        self.gain = None
    
        self.npulseByFrame = None
        
        self.profileIndex = None
        
        self.beam = Beam()
        
    def copy(self, inputObj=None):
        
        if inputObj == None:
            return copy.deepcopy(self)

        for key in inputObj.__dict__.keys():
            self.__dict__[key] = inputObj.__dict__[key]
    
    def getNHeights(self):

        return len(self.heightList)

        
    def isEmpty(self):
        
        return self.flagNoData
    
    nHeights = property(getNHeights, "I'm the 'nHeights' property.")