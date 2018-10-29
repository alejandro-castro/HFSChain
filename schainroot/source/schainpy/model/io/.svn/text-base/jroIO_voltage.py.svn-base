'''

'''
import numpy

from jroIO_base import LOCALTIME, JRODataReader, JRODataWriter
from model.proc.jroproc_base import ProcessingUnit, Operation
from model.data.jroheaderIO import PROCFLAG, BasicHeader, SystemHeader, RadarControllerHeader, ProcessingHeader
from model.data.jrodata import Voltage

class VoltageReader(JRODataReader, ProcessingUnit):
    """
    Esta clase permite leer datos de voltage desde archivos en formato rawdata (.r). La lectura
    de los datos siempre se realiza por bloques. Los datos leidos (array de 3 dimensiones: 
    perfiles*alturas*canales) son almacenados en la variable "buffer".
     
                             perfiles * alturas * canales  

    Esta clase contiene instancias (objetos) de las clases BasicHeader, SystemHeader, 
    RadarControllerHeader y Voltage. Los tres primeros se usan para almacenar informacion de la
    cabecera de datos (metadata), y el cuarto (Voltage) para obtener y almacenar un perfil de
    datos desde el "buffer" cada vez que se ejecute el metodo "getData".
    
    Example:
    
        dpath = "/home/myuser/data"
        
        startTime = datetime.datetime(2010,1,20,0,0,0,0,0,0)
        
        endTime = datetime.datetime(2010,1,21,23,59,59,0,0,0)
        
        readerObj = VoltageReader()
        
        readerObj.setup(dpath, startTime, endTime)
        
        while(True):
            
            #to get one profile 
            profile =  readerObj.getData()
             
            #print the profile
            print profile
            
            #If you want to see all datablock
            print readerObj.datablock
            
            if readerObj.flagNoMoreFiles:
                break
            
    """

    ext = ".r"
    
    optchar = "D"
    dataOut = None
    
    
    def __init__(self):
        """
        Inicializador de la clase VoltageReader para la lectura de datos de voltage.
        
        Input:
            dataOut    :    Objeto de la clase Voltage. Este objeto sera utilizado para
                              almacenar un perfil de datos cada vez que se haga un requerimiento
                              (getData). El perfil sera obtenido a partir del buffer de datos,
                              si el buffer esta vacio se hara un nuevo proceso de lectura de un
                              bloque de datos.
                              Si este parametro no es pasado se creara uno internamente.
        
        Variables afectadas:
            self.dataOut
        
        Return:
            None
        """
        
        ProcessingUnit.__init__(self)
        
        self.isConfig = False
        
        self.datablock = None
        
        self.utc = 0
    
        self.ext = ".r"
        
        self.optchar = "D"

        self.basicHeaderObj = BasicHeader(LOCALTIME)
        
        self.systemHeaderObj = SystemHeader()
        
        self.radarControllerHeaderObj = RadarControllerHeader()
        
        self.processingHeaderObj = ProcessingHeader()
        
        self.online = 0
        
        self.fp = None
        
        self.idFile = None
        
        self.dtype = None
        
        self.fileSizeByHeader = None
        
        self.filenameList = []
        
        self.filename = None
        
        self.fileSize = None
        
        self.firstHeaderSize = 0
        
        self.basicHeaderSize = 24
        
        self.pathList = []
        
        self.filenameList = []
        
        self.lastUTTime = 0
        
        self.maxTimeStep = 30
            
        self.flagNoMoreFiles = 0
        
        self.set = 0
        
        self.path = None
        
        self.profileIndex = 2**32-1

        self.delay  = 3   #seconds
        
        self.nTries  = 3  #quantity tries
        
        self.nFiles = 3   #number of files for searching
        
        self.nReadBlocks = 0
        
        self.flagIsNewFile = 1
        
        self.__isFirstTimeOnline = 1
    
#         self.ippSeconds = 0
    
        self.flagTimeBlock = 0    
    
        self.flagIsNewBlock = 0
        
        self.nTotalBlocks = 0
    
        self.blocksize = 0
        
        self.dataOut = self.createObjByDefault()
        
        self.nTxs = 1
        
        self.txIndex = 0
    
    def createObjByDefault(self):
        
        dataObj = Voltage()
        
        return dataObj
    
    def __hasNotDataInBuffer(self):
        
        if self.profileIndex >= self.processingHeaderObj.profilesPerBlock:
            return 1
        
        return 0


    def getBlockDimension(self):
        """
        Obtiene la cantidad de puntos a leer por cada bloque de datos
        
        Affected:
            self.blocksize

        Return:
            None
        """
        pts2read = self.processingHeaderObj.profilesPerBlock * self.processingHeaderObj.nHeights * self.systemHeaderObj.nChannels
        self.blocksize = pts2read

            
    def readBlock(self):
        """
        readBlock lee el bloque de datos desde la posicion actual del puntero del archivo
        (self.fp) y actualiza todos los parametros relacionados al bloque de datos
        (metadata + data). La data leida es almacenada en el buffer y el contador del buffer
        es seteado a 0
        
        Inputs:
            None
            
        Return:
            None
        
        Affected:
            self.profileIndex
            self.datablock
            self.flagIsNewFile
            self.flagIsNewBlock
            self.nTotalBlocks
            
        Exceptions: 
            Si un bloque leido no es un bloque valido
        """
        current_pointer_location = self.fp.tell()
        junk = numpy.fromfile( self.fp, self.dtype, self.blocksize )
        
        try:
            junk = junk.reshape( (self.processingHeaderObj.profilesPerBlock, self.processingHeaderObj.nHeights, self.systemHeaderObj.nChannels) )
        except:
            #print "The read block (%3d) has not enough data" %self.nReadBlocks
            
            if self.waitDataBlock(pointer_location=current_pointer_location):
                junk = numpy.fromfile( self.fp, self.dtype, self.blocksize )
                junk = junk.reshape( (self.processingHeaderObj.profilesPerBlock, self.processingHeaderObj.nHeights, self.systemHeaderObj.nChannels) )
#             return 0
        
        junk = numpy.transpose(junk, (2,0,1))
        self.datablock = junk['real'] + junk['imag']*1j
        
        self.profileIndex = 0
        
        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1

        self.nTotalBlocks += 1
        self.nReadBlocks += 1
          
        return 1

    def getFirstHeader(self):
        
        self.dataOut.systemHeaderObj = self.systemHeaderObj.copy()
        
        self.dataOut.radarControllerHeaderObj = self.radarControllerHeaderObj.copy()
        
        if self.nTxs > 1:
            self.dataOut.radarControllerHeaderObj.ippSeconds /= self.nTxs

#         self.dataOut.timeInterval = self.radarControllerHeaderObj.ippSeconds * self.processingHeaderObj.nCohInt

        if self.radarControllerHeaderObj.code != None:
            
            self.dataOut.nCode = self.radarControllerHeaderObj.nCode
            
            self.dataOut.nBaud = self.radarControllerHeaderObj.nBaud
            
            self.dataOut.code = self.radarControllerHeaderObj.code
            
        self.dataOut.dtype = self.dtype
            
        self.dataOut.nProfiles = self.processingHeaderObj.profilesPerBlock*self.nTxs
        
        if self.processingHeaderObj.nHeights % self.nTxs != 0:
            raise ValueError, "nTxs (%d) should be a multiple of nHeights (%d)" %(self.nTxs, self.processingHeaderObj.nHeights)
        
        xf = self.processingHeaderObj.firstHeight + int(self.processingHeaderObj.nHeights/self.nTxs)*self.processingHeaderObj.deltaHeight

        self.dataOut.heightList = numpy.arange(self.processingHeaderObj.firstHeight, xf, self.processingHeaderObj.deltaHeight) 
        
        self.dataOut.channelList = range(self.systemHeaderObj.nChannels)
                
        self.dataOut.nCohInt = self.processingHeaderObj.nCohInt
        
        self.dataOut.flagShiftFFT = False
        
        self.dataOut.flagDecodeData = False #asumo q la data no esta decodificada

        self.dataOut.flagDeflipData = False #asumo q la data no esta sin flip
        
        self.dataOut.flagShiftFFT = False
    
    def getData(self):
        """
        getData obtiene una unidad de datos del buffer de lectura, un perfil,  y la copia al objeto self.dataOut
        del tipo "Voltage" con todos los parametros asociados a este (metadata). cuando no hay datos
        en el buffer de lectura es necesario hacer una nueva lectura de los bloques de datos usando
        "readNextBlock"
        
        Ademas incrementa el contador del buffer "self.profileIndex" en 1.
        
        Return:
        
            Si el flag self.getByBlock ha sido seteado el bloque completo es copiado a self.dataOut y el self.profileIndex
            es igual al total de perfiles leidos desde el archivo.
        
            Si self.getByBlock == False:
            
                self.dataOut.data = buffer[:, thisProfile, :]
                
                shape = [nChannels, nHeis]
                    
            Si self.getByBlock == True:
            
                self.dataOut.data = buffer[:, :, :]
                
                shape = [nChannels, nProfiles, nHeis]
            
        Variables afectadas:
            self.dataOut
            self.profileIndex
            
        Affected:
            self.dataOut
            self.profileIndex
            self.flagTimeBlock
            self.flagIsNewBlock
        """
        
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            print 'Process finished'
            return 0
        
        self.flagTimeBlock = 0
        self.flagIsNewBlock = 0
        
        if self.__hasNotDataInBuffer():

            if not( self.readNextBlock() ):
                return 0
        
            self.getFirstHeader()
        
        if self.datablock == None:
            self.dataOut.flagNoData = True
            return 0
        
        if not self.getByBlock:

            """
            Return profile by profile
            
            If nTxs > 1 then one profile is divided by nTxs and number of total
            blocks is increased by nTxs (nProfiles *= nTxs)
            """
            if self.nTxs == 1:
                self.dataOut.flagDataAsBlock = False
                self.dataOut.data = self.datablock[:,self.profileIndex,:]
                self.dataOut.profileIndex = self.profileIndex
                
                self.profileIndex += 1
                
            else:
                self.dataOut.flagDataAsBlock = False
                
                iniHei_ForThisTx = (self.txIndex)*int(self.processingHeaderObj.nHeights/self.nTxs)
                endHei_ForThisTx = (self.txIndex+1)*int(self.processingHeaderObj.nHeights/self.nTxs)
                
#                 print iniHei_ForThisTx, endHei_ForThisTx
                
                self.dataOut.data = self.datablock[:, self.profileIndex, iniHei_ForThisTx:endHei_ForThisTx]
                self.dataOut.profileIndex = self.profileIndex*self.nTxs + self.txIndex
                
                self.txIndex += 1
                
                if self.txIndex == self.nTxs:
                    self.txIndex = 0
                    self.profileIndex += 1
                
        else:
            """
            Return all block
            """
            self.dataOut.flagDataAsBlock = True
            self.dataOut.data = self.datablock
            self.dataOut.profileIndex = self.processingHeaderObj.profilesPerBlock - 1
            
            self.profileIndex = self.processingHeaderObj.profilesPerBlock - 1
        
        self.dataOut.flagNoData = False
        
        self.getBasicHeader()
        
        self.dataOut.realtime = self.online
        
        return self.dataOut.data

class VoltageWriter(JRODataWriter, Operation):
    """ 
    Esta clase permite escribir datos de voltajes a archivos procesados (.r). La escritura
    de los datos siempre se realiza por bloques. 
    """
    
    ext = ".r"
    
    optchar = "D"
    
    shapeBuffer = None
    

    def __init__(self):
        """ 
        Inicializador de la clase VoltageWriter para la escritura de datos de espectros.
         
        Affected: 
            self.dataOut

        Return: None
        """
        Operation.__init__(self)
        
        self.nTotalBlocks = 0

        self.profileIndex = 0
        
        self.isConfig = False
        
        self.fp = None

        self.flagIsNewFile = 1
        
        self.nTotalBlocks = 0 
        
        self.flagIsNewBlock = 0

        self.setFile = None
        
        self.dtype = None
        
        self.path = None
        
        self.filename = None
        
        self.basicHeaderObj = BasicHeader(LOCALTIME)
    
        self.systemHeaderObj = SystemHeader()
    
        self.radarControllerHeaderObj = RadarControllerHeader()
    
        self.processingHeaderObj = ProcessingHeader()

    def hasAllDataInBuffer(self):
        if self.profileIndex >= self.processingHeaderObj.profilesPerBlock:
            return 1
        return 0


    def setBlockDimension(self):
        """
        Obtiene las formas dimensionales del los subbloques de datos que componen un bloque

        Affected:
            self.shape_spc_Buffer
            self.shape_cspc_Buffer
            self.shape_dc_Buffer

        Return: None
        """
        self.shapeBuffer = (self.processingHeaderObj.profilesPerBlock,
                            self.processingHeaderObj.nHeights,
                            self.systemHeaderObj.nChannels)
            
        self.datablock = numpy.zeros((self.systemHeaderObj.nChannels,
                                     self.processingHeaderObj.profilesPerBlock,
                                     self.processingHeaderObj.nHeights),
                                     dtype=numpy.dtype('complex64'))

        
    def writeBlock(self):
        """
        Escribe el buffer en el file designado
            
        Affected:
            self.profileIndex 
            self.flagIsNewFile
            self.flagIsNewBlock
            self.nTotalBlocks
            self.blockIndex    
            
        Return: None
        """
        data = numpy.zeros( self.shapeBuffer, self.dtype )
        
        junk = numpy.transpose(self.datablock, (1,2,0))
        
        data['real'] = junk.real
        data['imag'] = junk.imag
        
        data = data.reshape( (-1) )
            
        data.tofile( self.fp )
        
        self.datablock.fill(0)
        
        self.profileIndex = 0 
        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1
        
        self.blockIndex += 1
        self.nTotalBlocks += 1
        
    def putData(self):
        """
        Setea un bloque de datos y luego los escribe en un file 
            
        Affected:
            self.flagIsNewBlock
            self.profileIndex

        Return: 
            0    :    Si no hay data o no hay mas files que puedan escribirse 
            1    :    Si se escribio la data de un bloque en un file
        """
        if self.dataOut.flagNoData:
            return 0
        
        self.flagIsNewBlock = 0
        
        if self.dataOut.flagTimeBlock:
            
            self.datablock.fill(0)
            self.profileIndex = 0
            self.setNextFile()
        
        if self.profileIndex == 0:
            self.setBasicHeader()
        
        self.datablock[:,self.profileIndex,:] = self.dataOut.data
        
        self.profileIndex += 1
        
        if self.hasAllDataInBuffer():
            #if self.flagIsNewFile: 
            self.writeNextBlock()
#            self.setFirstHeader()
        
        return 1
    
    def __getProcessFlags(self):
        
        processFlags = 0
        
        dtype0 = numpy.dtype([('real','<i1'),('imag','<i1')])
        dtype1 = numpy.dtype([('real','<i2'),('imag','<i2')])
        dtype2 = numpy.dtype([('real','<i4'),('imag','<i4')])
        dtype3 = numpy.dtype([('real','<i8'),('imag','<i8')])
        dtype4 = numpy.dtype([('real','<f4'),('imag','<f4')])
        dtype5 = numpy.dtype([('real','<f8'),('imag','<f8')])
        
        dtypeList = [dtype0, dtype1, dtype2, dtype3, dtype4, dtype5]
        
        
        
        datatypeValueList =  [PROCFLAG.DATATYPE_CHAR, 
                           PROCFLAG.DATATYPE_SHORT, 
                           PROCFLAG.DATATYPE_LONG, 
                           PROCFLAG.DATATYPE_INT64, 
                           PROCFLAG.DATATYPE_FLOAT, 
                           PROCFLAG.DATATYPE_DOUBLE]
        
        
        for index in range(len(dtypeList)):
            if self.dataOut.dtype == dtypeList[index]:
                dtypeValue = datatypeValueList[index]
                break
        
        processFlags += dtypeValue
        
        if self.dataOut.flagDecodeData:
            processFlags += PROCFLAG.DECODE_DATA
        
        if self.dataOut.flagDeflipData:
            processFlags += PROCFLAG.DEFLIP_DATA
        
        if self.dataOut.code != None:
            processFlags += PROCFLAG.DEFINE_PROCESS_CODE
        
        if self.dataOut.nCohInt > 1:
            processFlags += PROCFLAG.COHERENT_INTEGRATION
        
        return processFlags
    
    
    def __getBlockSize(self):
        '''
        Este metodos determina el cantidad de bytes para un bloque de datos de tipo Voltage
        '''
        
        dtype0 = numpy.dtype([('real','<i1'),('imag','<i1')])
        dtype1 = numpy.dtype([('real','<i2'),('imag','<i2')])
        dtype2 = numpy.dtype([('real','<i4'),('imag','<i4')])
        dtype3 = numpy.dtype([('real','<i8'),('imag','<i8')])
        dtype4 = numpy.dtype([('real','<f4'),('imag','<f4')])
        dtype5 = numpy.dtype([('real','<f8'),('imag','<f8')])
        
        dtypeList = [dtype0, dtype1, dtype2, dtype3, dtype4, dtype5]
        datatypeValueList = [1,2,4,8,4,8]
        for index in range(len(dtypeList)):
            if self.dataOut.dtype == dtypeList[index]:
                datatypeValue = datatypeValueList[index]
                break
        
        blocksize = int(self.dataOut.nHeights * self.dataOut.nChannels * self.profilesPerBlock * datatypeValue * 2)
        
        return blocksize
    
    def setFirstHeader(self):
        
        """
        Obtiene una copia del First Header
         
        Affected:
            self.systemHeaderObj
            self.radarControllerHeaderObj
            self.dtype

        Return: 
            None
        """
        
        self.systemHeaderObj = self.dataOut.systemHeaderObj.copy()
        self.systemHeaderObj.nChannels = self.dataOut.nChannels
        self.radarControllerHeaderObj = self.dataOut.radarControllerHeaderObj.copy()
        
        self.setBasicHeader()
        
        processingHeaderSize = 40 # bytes    
        self.processingHeaderObj.dtype = 0 # Voltage
        self.processingHeaderObj.blockSize = self.__getBlockSize()
        self.processingHeaderObj.profilesPerBlock = self.profilesPerBlock
        self.processingHeaderObj.dataBlocksPerFile = self.blocksPerFile
        self.processingHeaderObj.nWindows = 1 #podria ser 1 o self.dataOut.processingHeaderObj.nWindows
        self.processingHeaderObj.processFlags = self.__getProcessFlags()
        self.processingHeaderObj.nCohInt = self.dataOut.nCohInt
        self.processingHeaderObj.nIncohInt = 1 # Cuando la data de origen es de tipo Voltage
        self.processingHeaderObj.totalSpectra = 0 # Cuando la data de origen es de tipo Voltage
        
#         if self.dataOut.code != None:
#             self.processingHeaderObj.code = self.dataOut.code
#             self.processingHeaderObj.nCode = self.dataOut.nCode
#             self.processingHeaderObj.nBaud = self.dataOut.nBaud
#             codesize = int(8 + 4 * self.dataOut.nCode * self.dataOut.nBaud)
#             processingHeaderSize += codesize
        
        if self.processingHeaderObj.nWindows != 0:
            self.processingHeaderObj.firstHeight = self.dataOut.heightList[0]
            self.processingHeaderObj.deltaHeight = self.dataOut.heightList[1] - self.dataOut.heightList[0]
            self.processingHeaderObj.nHeights = self.dataOut.nHeights
            self.processingHeaderObj.samplesWin = self.dataOut.nHeights
            processingHeaderSize += 12
            
        self.processingHeaderObj.size = processingHeaderSize