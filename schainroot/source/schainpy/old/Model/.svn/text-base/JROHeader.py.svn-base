'''
Created on 23/01/2012

@author $Author: vsarmiento $
@version $Id: HeaderIO.py 37 2012-03-26 22:55:13Z vsarmiento $
'''

import numpy
import copy

class Header:
    
    def __init__(self):
        raise
    
    def copy(self):
        return copy.deepcopy(self)

    def read():
        pass

    def write():
        pass

class BasicHeader(Header):
    
    size = None
    version = None
    dataBlock = None
    utc = None
    miliSecond = None
    timeZone = None
    dstFlag = None
    errorCount = None
    struct = None
        
    def __init__(self):
        self.size = 0
        self.version = 0
        self.dataBlock = 0
        self.utc = 0
        self.miliSecond = 0
        self.timeZone = 0
        self.dstFlag = 0
        self.errorCount = 0
        self.struct = numpy.dtype([
                              ('nSize','<u4'),
                              ('nVersion','<u2'),
                              ('nDataBlockId','<u4'),
                              ('nUtime','<u4'),
                              ('nMilsec','<u2'),     
                              ('nTimezone','<i2'),
                              ('nDstflag','<i2'),
                              ('nErrorCount','<u4')
                              ])   
        
    
    def read(self, fp):
        try:
            header = numpy.fromfile(fp, self.struct,1)
            self.size = header['nSize'][0]
            self.version = header['nVersion'][0]
            self.dataBlock = header['nDataBlockId'][0]
            self.utc = header['nUtime'][0]
            self.miliSecond = header['nMilsec'][0]
            self.timeZone = header['nTimezone'][0]
            self.dstFlag = header['nDstflag'][0]
            self.errorCount = header['nErrorCount'][0]
        except:
            return 0
        
        return 1
    
    def write(self, fp):
        headerTuple = (self.size,self.version,self.dataBlock,self.utc,self.miliSecond,self.timeZone,self.dstFlag,self.errorCount)
        header = numpy.array(headerTuple,self.struct)        
        header.tofile(fp)
        
        return 1

class SystemHeader(Header):
    
    size = None
    numSamples = None
    numProfiles = None
    numChannels = None
    adcResolution = None
    pciDioBusWidth = None
    struct = None
        
    def __init__(self):
        self.size = 0 
        self.numSamples = 0
        self.numProfiles = 0
        self.numChannels = 0
        self.adcResolution = 0
        self.pciDioBusWidth = 0
        self.struct = numpy.dtype([
                            ('nSize','<u4'),
                            ('nNumSamples','<u4'),
                            ('nNumProfiles','<u4'),
                            ('nNumChannels','<u4'),
                            ('nADCResolution','<u4'),
                            ('nPCDIOBusWidth','<u4'),
                            ])
    

    def read(self, fp):
        try:
            header = numpy.fromfile(fp,self.struct,1)
            self.size = header['nSize'][0]
            self.numSamples = header['nNumSamples'][0]
            self.numProfiles = header['nNumProfiles'][0]
            self.numChannels = header['nNumChannels'][0]
            self.adcResolution = header['nADCResolution'][0]
            self.pciDioBusWidth = header['nPCDIOBusWidth'][0]
        except:
            return 0
        
        return 1
    
    def write(self, fp):
        headerTuple = (self.size,self.numSamples,self.numProfiles,self.numChannels,self.adcResolution,self.pciDioBusWidth)
        header = numpy.array(headerTuple,self.struct)
        header.tofile(fp)
        
        return 1
    
class RadarControllerHeader(Header):
    
    size = None
    expType = None
    nTx = None
    ipp = None
    txA = None
    txB = None
    numWindows = None
    numTaus = None
    codeType = None
    line6Function = None
    line5Function = None
    fClock = None
    prePulseBefore = None
    prePulserAfter = None
    rangeIpp = None
    rangeTxA = None
    rangeTxB = None
    struct = None
        
    def __init__(self):
        self.size = 0
        self.expType = 0
        self.nTx = 0
        self.ipp = 0
        self.txA = 0
        self.txB = 0
        self.numWindows = 0
        self.numTaus = 0
        self.codeType = 0
        self.line6Function = 0
        self.line5Function = 0
        self.fClock = 0
        self.prePulseBefore = 0
        self.prePulserAfter = 0
        self.rangeIpp = 0
        self.rangeTxA = 0
        self.rangeTxB = 0
        self.struct = numpy.dtype([
                             ('nSize','<u4'),
                             ('nExpType','<u4'),
                             ('nNTx','<u4'),
                             ('fIpp','<f4'),
                             ('fTxA','<f4'),
                             ('fTxB','<f4'),
                             ('nNumWindows','<u4'),
                             ('nNumTaus','<u4'),
                             ('nCodeType','<u4'),
                             ('nLine6Function','<u4'),
                             ('nLine5Function','<u4'),
                             ('fClock','<f4'),
                             ('nPrePulseBefore','<u4'),
                             ('nPrePulseAfter','<u4'),
                             ('sRangeIPP','<a20'),
                             ('sRangeTxA','<a20'),
                             ('sRangeTxB','<a20'),
                             ])
        
        self.samplingWindowStruct = numpy.dtype([('h0','<f4'),('dh','<f4'),('nsa','<u4')])
        
        self.samplingWindow = None
        self.numHeights = None
        self.firstHeight = None
        self.deltaHeight = None
        self.samplesWin = None
        
        self.numCode = None
        self.numBaud = None
        self.code = None
        self.flip1 = None
        self.flip2 = None
        
        self.dynamic = numpy.array([],numpy.dtype('byte'))
        

    def read(self, fp):
        try:
            startFp = fp.tell()
            header = numpy.fromfile(fp,self.struct,1)
            self.size = header['nSize'][0]
            self.expType = header['nExpType'][0]
            self.nTx = header['nNTx'][0]
            self.ipp = header['fIpp'][0]
            self.txA = header['fTxA'][0]
            self.txB = header['fTxB'][0]
            self.numWindows = header['nNumWindows'][0]
            self.numTaus = header['nNumTaus'][0]
            self.codeType = header['nCodeType'][0]
            self.line6Function = header['nLine6Function'][0]
            self.line5Function = header['nLine5Function'][0]
            self.fClock = header['fClock'][0]
            self.prePulseBefore = header['nPrePulseBefore'][0]
            self.prePulserAfter = header['nPrePulseAfter'][0]
            self.rangeIpp = header['sRangeIPP'][0]
            self.rangeTxA = header['sRangeTxA'][0]
            self.rangeTxB = header['sRangeTxB'][0]
            # jump Dynamic Radar Controller Header
            jumpFp =  self.size - 116
            self.dynamic = numpy.fromfile(fp,numpy.dtype('byte'),jumpFp)
            #pointer backward to dynamic header and read
            backFp = fp.tell() - jumpFp
            fp.seek(backFp)
            
            self.samplingWindow = numpy.fromfile(fp,self.samplingWindowStruct,self.numWindows)
            self.numHeights = numpy.sum(self.samplingWindow['nsa'])
            self.firstHeight = self.samplingWindow['h0']
            self.deltaHeight = self.samplingWindow['dh']
            self.samplesWin = self.samplingWindow['nsa']
            
            self.Taus = numpy.fromfile(fp,'<f4',self.numTaus)
    
            if self.codeType != 0:
                self.numCode = numpy.fromfile(fp,'<u4',1)
                self.numBaud = numpy.fromfile(fp,'<u4',1)
                self.code = numpy.empty([self.numCode,self.numBaud],dtype='u1')
                tempList = []
                for ic in range(self.numCode):
                    temp = numpy.fromfile(fp,'u1',4*numpy.ceil(self.numBaud/32.))
                    tempList.append(temp)
                    self.code[ic] = numpy.unpackbits(temp[::-1])[-1*self.numBaud:]
                self.code = 2.0*self.code - 1.0
            
            if self.line5Function == RCfunction.FLIP:
                self.flip1 = numpy.fromfile(fp,'<u4',1)

            if self.line6Function == RCfunction.FLIP:
                self.flip2 = numpy.fromfile(fp,'<u4',1)
                
            endFp = self.size + startFp
            jumpFp =  endFp - fp.tell()
            if jumpFp > 0:
                fp.seek(jumpFp)

        except:
            return 0
        
        return 1
    
    def write(self, fp):
        headerTuple = (self.size,
                       self.expType,
                       self.nTx,
                       self.ipp,
                       self.txA,
                       self.txB,
                       self.numWindows,
                       self.numTaus,
                       self.codeType,
                       self.line6Function,
                       self.line5Function,
                       self.fClock,
                       self.prePulseBefore,
                       self.prePulserAfter,
                       self.rangeIpp,
                       self.rangeTxA,
                       self.rangeTxB)
        
        header = numpy.array(headerTuple,self.struct)
        header.tofile(fp)
        
        dynamic = self.dynamic
        dynamic.tofile(fp)
        
        return 1

    
    
class ProcessingHeader(Header):
    
    size = None
    dataType = None
    blockSize = None
    profilesPerBlock = None
    dataBlocksPerFile = None
    numWindows = None
    processFlags = None
    coherentInt = None
    incoherentInt = None
    totalSpectra = None
    struct = None
    flag_dc = None
    flag_cspc = None
        
    def __init__(self):
        self.size = 0
        self.dataType = 0
        self.blockSize = 0
        self.profilesPerBlock = 0
        self.dataBlocksPerFile = 0
        self.numWindows = 0
        self.processFlags = 0
        self.coherentInt = 0
        self.incoherentInt = 0
        self.totalSpectra = 0
        self.struct = numpy.dtype([
                               ('nSize','<u4'),
                               ('nDataType','<u4'),
                               ('nSizeOfDataBlock','<u4'),
                               ('nProfilesperBlock','<u4'),
                               ('nDataBlocksperFile','<u4'),
                               ('nNumWindows','<u4'),
                               ('nProcessFlags','<u4'),
                               ('nCoherentIntegrations','<u4'),
                               ('nIncoherentIntegrations','<u4'),
                               ('nTotalSpectra','<u4')
                               ])
        self.samplingWindow = 0
        self.structSamplingWindow = numpy.dtype([('h0','<f4'),('dh','<f4'),('nsa','<u4')])
        self.numHeights = 0
        self.firstHeight = 0
        self.deltaHeight = 0
        self.samplesWin = 0
        self.spectraComb = 0
        self.numCode = 0
        self.code = 0
        self.numBaud = 0
        self.shif_fft = False
        self.flag_dc = False
        self.flag_cspc = False
    
    def read(self, fp):
        try:
            header = numpy.fromfile(fp,self.struct,1)
            self.size = header['nSize'][0]
            self.dataType = header['nDataType'][0]
            self.blockSize = header['nSizeOfDataBlock'][0]
            self.profilesPerBlock = header['nProfilesperBlock'][0]
            self.dataBlocksPerFile = header['nDataBlocksperFile'][0]
            self.numWindows = header['nNumWindows'][0]
            self.processFlags = header['nProcessFlags']
            self.coherentInt = header['nCoherentIntegrations'][0]
            self.incoherentInt = header['nIncoherentIntegrations'][0]
            self.totalSpectra = header['nTotalSpectra'][0]
            self.samplingWindow = numpy.fromfile(fp,self.structSamplingWindow,self.numWindows)
            self.numHeights = numpy.sum(self.samplingWindow['nsa'])
            self.firstHeight = self.samplingWindow['h0']
            self.deltaHeight = self.samplingWindow['dh']
            self.samplesWin = self.samplingWindow['nsa']
            self.spectraComb = numpy.fromfile(fp,'u1',2*self.totalSpectra)
            
            if ((self.processFlags & PROCFLAG.DEFINE_PROCESS_CODE) == PROCFLAG.DEFINE_PROCESS_CODE):
                self.numCode = numpy.fromfile(fp,'<u4',1)
                self.numBaud = numpy.fromfile(fp,'<u4',1)
                self.code = numpy.fromfile(fp,'<f4',self.numCode*self.numBaud).reshape(self.numBaud,self.numCode)
            
            if ((self.processFlags & PROCFLAG.SHIFT_FFT_DATA) == PROCFLAG.SHIFT_FFT_DATA):
                self.shif_fft = True
            else:
                self.shif_fft = False
                
            if ((self.processFlags & PROCFLAG.SAVE_CHANNELS_DC) == PROCFLAG.SAVE_CHANNELS_DC):
                self.flag_dc = True
            
            nChannels = 0
            nPairs = 0
            pairList = []
            
            for i in range( 0, self.totalSpectra*2, 2 ):
                if self.spectraComb[i] == self.spectraComb[i+1]:
                    nChannels = nChannels + 1   #par de canales iguales 
                else:
                    nPairs = nPairs + 1 #par de canales diferentes
                    pairList.append( (self.spectraComb[i], self.spectraComb[i+1]) )
            
            self.flag_cspc = False
            if nPairs > 0:
                self.flag_cspc = True
                
        except:
            return 0
        
        return 1
    
    def write(self, fp):
        headerTuple = (self.size,
                       self.dataType,
                       self.blockSize,
                       self.profilesPerBlock,
                       self.dataBlocksPerFile,
                       self.numWindows,
                       self.processFlags,
                       self.coherentInt,
                       self.incoherentInt,
                       self.totalSpectra)
        
        header = numpy.array(headerTuple,self.struct)  
        header.tofile(fp)
        
        if self.numWindows != 0:
            sampleWindowTuple = (self.firstHeight,self.deltaHeight,self.samplesWin)
            samplingWindow = numpy.array(sampleWindowTuple,self.structSamplingWindow)
            samplingWindow.tofile(fp)

            
        if self.totalSpectra != 0:
            spectraComb = numpy.array([],numpy.dtype('u1'))
            spectraComb = self.spectraComb
            spectraComb.tofile(fp)

            
        if self.processFlags & PROCFLAG.DEFINE_PROCESS_CODE == PROCFLAG.DEFINE_PROCESS_CODE:
            numCode = self.numCode
            numCode.tofile(fp)

            numBaud = self.numBaud
            numBaud.tofile(fp)

            code = self.code.reshape(numCode*numBaud)
            code.tofile(fp)
            
        return 1

class RCfunction:
    NONE=0
    FLIP=1
    CODE=2
    SAMPLING=3
    LIN6DIV256=4
    SYNCHRO=5

class nCodeType:
    NONE=0
    USERDEFINE=1
    BARKER2=2
    BARKER3=3
    BARKER4=4
    BARKER5=5
    BARKER7=6
    BARKER11=7
    BARKER13=8
    AC128=9
    COMPLEMENTARYCODE2=10
    COMPLEMENTARYCODE4=11
    COMPLEMENTARYCODE8=12
    COMPLEMENTARYCODE16=13
    COMPLEMENTARYCODE32=14
    COMPLEMENTARYCODE64=15
    COMPLEMENTARYCODE128=16
    CODE_BINARY28=17

class PROCFLAG:    
    COHERENT_INTEGRATION = numpy.uint32(0x00000001)
    DECODE_DATA = numpy.uint32(0x00000002) 
    SPECTRA_CALC = numpy.uint32(0x00000004)
    INCOHERENT_INTEGRATION = numpy.uint32(0x00000008) 
    POST_COHERENT_INTEGRATION = numpy.uint32(0x00000010)
    SHIFT_FFT_DATA = numpy.uint32(0x00000020)
    
    DATATYPE_CHAR = numpy.uint32(0x00000040)
    DATATYPE_SHORT = numpy.uint32(0x00000080)
    DATATYPE_LONG = numpy.uint32(0x00000100)
    DATATYPE_INT64 = numpy.uint32(0x00000200)
    DATATYPE_FLOAT = numpy.uint32(0x00000400)
    DATATYPE_DOUBLE = numpy.uint32(0x00000800)
    
    DATAARRANGE_CONTIGUOUS_CH = numpy.uint32(0x00001000) 
    DATAARRANGE_CONTIGUOUS_H = numpy.uint32(0x00002000) 
    DATAARRANGE_CONTIGUOUS_P = numpy.uint32(0x00004000) 
    
    SAVE_CHANNELS_DC = numpy.uint32(0x00008000)
    DEFLIP_DATA = numpy.uint32(0x00010000)    
    DEFINE_PROCESS_CODE = numpy.uint32(0x00020000) 
     
    ACQ_SYS_NATALIA = numpy.uint32(0x00040000)
    ACQ_SYS_ECHOTEK = numpy.uint32(0x00080000)
    ACQ_SYS_ADRXD = numpy.uint32(0x000C0000)
    ACQ_SYS_JULIA = numpy.uint32(0x00100000)
    ACQ_SYS_XXXXXX = numpy.uint32(0x00140000)
    
    EXP_NAME_ESP = numpy.uint32(0x00200000)
    CHANNEL_NAMES_ESP = numpy.uint32(0x00400000)
        
    OPERATION_MASK = numpy.uint32(0x0000003F)
    DATATYPE_MASK = numpy.uint32(0x00000FC0)
    DATAARRANGE_MASK = numpy.uint32(0x00007000)
    ACQ_SYS_MASK = numpy.uint32(0x001C0000)