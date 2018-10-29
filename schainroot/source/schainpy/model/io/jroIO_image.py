'''
Created on Jul 2, 2014

@author: roj-idl71
'''
import numpy

from jroIO_base import LOCALTIME, JRODataReader, JRODataWriter
from model.proc.jroproc_base import ProcessingUnit, Operation
from model.data.jroheaderIO import PROCFLAG, BasicHeader, SystemHeader, RadarControllerHeader, ProcessingHeader
from model.data.jrodata import Image


class ImageWriter(JRODataWriter, Operation):

    """
    Esta clase permite escribir datos de espectros a archivos procesados (.pdata). La escritura
    de los datos siempre se realiza por bloques.
    """

    ext = ".out"

    optchar = "H"

    data_genaro=None

    shapeBuffer = None

    dataOut = None

    standard = None

    def __init__(self):
        """
        Inicializador de la clase SpectraWriter para la escritura de datos de espectros.

        Affected:
            self.dataOut

        Return: None
        """

        Operation.__init__(self)

        self.isConfig = False

        self.nTotalBlocks = 0

        self.profileIndex=0

        self.isConfig=False

        self.fp = None

        self.flagIsNewFile = 1

        self.nTotalBlocks = 0

        self.flagIsNewBlock = 0

        self.setFile = None

        self.dtype = None

        self.path = None

        self.noMoreFiles = 0

        self.filename = None

        self.data_genaro=None

        self.data_timege=None               #User1 was here

        self.data_doppler= None
#        self.glados=None            #User1 was here

#        self.dataOut = None                 # User1 puso esto aqui
        #self.datatime = self.dataOut.datatime.date()

        self.standard = False

        self.basicHeaderObj = BasicHeader(LOCALTIME)

        self.systemHeaderObj = SystemHeader()

        self.radarControllerHeaderObj = RadarControllerHeader()

#opObj11.addParamete
        self.processingHeaderObj = ProcessingHeader()

#        self.glados2 = None

    def hasAllDataInBuffer(self):
        return 1


    def setBlockDimension(self):
        """
        Obtiene las formas dimensionales del los subbloques de datos que componen un bloque

        Affected:
            self.shape_spc_Buffer
            self.shape_cspc_Buffer
            self.shape_dc_Buffer

        Return: None
        """
        self.shapeBuffer=(self.processingHeaderObj.nHeights)
#                          self.dataOut.datatime.time())  # User1 puso esto aqui

        self.datablock=numpy.zeros(self.processingHeaderObj.nHeights,
#                                   self.dataOut.datatime.time,     # User1 puso esto aqui
                                   dtype=numpy.dtype('complex64'))   # User1 puso complex64 en luegar de float

    def writeBlock(self):
        """
        Escribe el buffer en el file designado

        Affected:
            self.data_spc
            self.data_cspc
            self.data_dc
            self.flagIsNewFile
            self.flagIsNewBlock
            self.nTotalBlocks
            self.nWriteBlocks

        Return: None
        """
        #print "escribe el valor:D"
        data_genaro=self.data_genaro
        data_timege=self.data_timege
        data_doppler=self.data_doppler

        #data=numpy.zeros(self.shapeBuffer,self.dtype)
        #print "Imprime valores del datablock",self.datablock

        self.fp.write("%f %f  %f\n" %(data_timege,data_genaro,data_doppler))           #User1 was here
        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1
        self.nTotalBlocks += 1
        self.nWriteBlocks += 1
        self.blockIndex += 1

#         print "[Writing] Block = %d04" %self.blockIndex

    def putData(self):
        """
        Setea un bloque de datos y luego los escribe en un file

        Affected:
            self.data_spc
            self.data_cspc
            self.data_dc

        Return:
            0    :    Si no hay data o no hay mas files que puedan escribirse
            1    :    Si se escribio la data de un bloque en un file
        """

        if self.dataOut.flagNoData:
            return 0

#        if self.profileIndex==0:
#            print "Voy a empezar a escribir"

        self.flagIsNewBlock = 0

        if self.dataOut.flagDiscontinuousBlock:
            if self.nTotalBlocks>self.blocksPerFile:
                self.setNextFile()

        if self.flagIsNewFile == 0:
            self.setBasicHeader()

        self.data_genaro= self.dataOut.data_img_genaro
        self.data_timege= self.dataOut.data_time_genaro         #User1 was here
        #######NUEVO PARA OBTENER DOPPLER
        parameterObject = "data_param"
        parameterIndex=1
        data_param = getattr(self.dataOut, parameterObject)
        self.data_tmp_doppler=data_param[numpy.array(self.dataOut.channel_img),parameterIndex,:]
        self.data_doppler=self.data_tmp_doppler[int(self.data_genaro/1.5)]# debe ser entre 1.5 porque los 1500 alturas e indices.
        ############AnADIR PLOTEO Y GRAFICO

        #self.profileIndex +=1


        # #self.processingHeaderObj.dataBlocksPerFile)
        if self.hasAllDataInBuffer():
#            self.setFirstHeader()
            self.writeNextBlock()

        return 1


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

        self.processingHeaderObj.dtype = 1 # Spectra
        #self.processingHeaderObj.blockSize = self.__getBlockSize()
        self.processingHeaderObj.profilesPerBlock = self.dataOut.nFFTPoints
        self.processingHeaderObj.dataBlocksPerFile = self.blocksPerFile
        self.processingHeaderObj.nWindows = 1 #podria ser 1 o self.dataOut.processingHeaderObj.nWindows
        self.processingHeaderObj.nCohInt = self.dataOut.nCohInt# Se requiere para determinar el valor de timeInterval
        self.processingHeaderObj.nIncohInt = self.dataOut.nIncohInt
        #self.processingHeaderObj.totalSpectra = self.dataOut.nPairs + self.dataOut.nChannels
        self.processingHeaderObj.shif_fft = self.dataOut.flagShiftFFT

        if self.processingHeaderObj.totalSpectra > 0:
            channelList = []
            for channel in range(self.dataOut.nChannels):
                channelList.append(channel)
                channelList.append(channel)

            pairsList = []
            if self.dataOut.nPairs > 0:
                for pair in self.dataOut.pairsList:
                    pairsList.append(pair[0])
                    pairsList.append(pair[1])

            spectraComb = channelList + pairsList
            spectraComb = numpy.array(spectraComb, dtype="u1")
            self.processingHeaderObj.spectraComb = spectraComb

        if self.dataOut.code is not None:
            self.processingHeaderObj.code = self.dataOut.code
            self.processingHeaderObj.nCode = self.dataOut.nCode
            self.processingHeaderObj.nBaud = self.dataOut.nBaud

        if self.processingHeaderObj.nWindows != 0:
            self.processingHeaderObj.firstHeight = self.dataOut.heightList[0]
            self.processingHeaderObj.deltaHeight = self.dataOut.heightList[1] - self.dataOut.heightList[0]
            self.processingHeaderObj.nHeights = self.dataOut.nHeights
            self.processingHeaderObj.samplesWin = self.dataOut.nHeights

        #self.processingHeaderObj.processFlags = self.getProcessFlags()

        self.setBasicHeader()
