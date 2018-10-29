'''
@author: Daniel Suarez
'''
import numpy
from jroproc_base import ProcessingUnit, Operation
from model.data.jroamisr import AMISR

class AMISRProc(ProcessingUnit):
    def __init__(self):
        ProcessingUnit.__init__(self)
        self.objectDict = {}
        self.dataOut = AMISR()
        
    def run(self):
        if self.dataIn.type == 'AMISR':
            self.dataOut.copy(self.dataIn) 


class PrintInfo(Operation):
    def __init__(self):
        self.__isPrinted = False
    
    def run(self, dataOut):
        
        if not self.__isPrinted:
            print 'Number of Records by File: %d'%dataOut.nRecords
            print 'Number of Pulses: %d'%dataOut.nProfiles
            print 'Number of Pulses by Frame: %d'%dataOut.npulseByFrame
            print 'Number of Samples by Pulse: %d'%len(dataOut.heightList)
            print 'Ipp Seconds: %f'%dataOut.ippSeconds
            print 'Number of Beams: %d'%dataOut.nBeams
            print 'BeamCodes:'
            beamStrList = ['Beam %d -> Code=%d, azimuth=%2.2f,  zenith=%2.2f, gain=%2.2f'%(k,v[0],v[1],v[2],v[3]) for k,v in dataOut.beamCodeDict.items()]
            for b in beamStrList:
                print b
            self.__isPrinted = True
        
        return
        
        
class BeamSelector(Operation):
    profileIndex = None
    nProfiles = None
    
    def __init__(self):
        
        self.profileIndex = 0
        self.__isConfig = False
    
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
    
    def run(self, dataOut, beam=None):
        
        dataOut.flagNoData = True
        
        if not(self.__isConfig):
            
            self.nProfiles = dataOut.nProfiles
            self.profileIndex = dataOut.profileIndex
            self.__isConfig = True

        if beam != None:
            if self.isProfileInList(dataOut.beamRangeDict[beam]):
                beamInfo = dataOut.beamCodeDict[beam]
                dataOut.azimuth = beamInfo[1]
                dataOut.zenith = beamInfo[2]
                dataOut.gain = beamInfo[3]
                dataOut.flagNoData = False
                
            self.incIndex()
            return 1
        
        else:
            raise ValueError, "BeamSelector needs beam value"
        
        return 0

class ProfileToChannels(Operation):

    def __init__(self):
        self.__isConfig = False
        self.__counter_chan = 0
        self.buffer = None

    def isProfileInList(self, profileList):
        
        if self.profileIndex not in profileList:
            return False
        
        return True
    
    def run(self, dataOut):
        
        dataOut.flagNoData = True
        
        if not(self.__isConfig):
            nchannels = len(dataOut.beamRangeDict.keys())
            nsamples = dataOut.nHeights
            self.buffer = numpy.zeros((nchannels, nsamples), dtype = 'complex128')
            dataOut.beam.codeList = [dataOut.beamCodeDict[x][0] for x in range(nchannels)]
            dataOut.beam.azimuthList = [dataOut.beamCodeDict[x][1] for x in range(nchannels)]
            dataOut.beam.zenithList = [dataOut.beamCodeDict[x][2] for x in range(nchannels)]
            self.__isConfig = True
        
        for i in range(self.buffer.shape[0]):
            if dataOut.profileIndex in dataOut.beamRangeDict[i]:
                self.buffer[i,:] = dataOut.data
                break
        
        
        self.__counter_chan += 1
          
        if self.__counter_chan >= self.buffer.shape[0]:
            self.__counter_chan = 0
            dataOut.data = self.buffer.copy()
            dataOut.channelList = range(self.buffer.shape[0])
            self.__isConfig = False
            dataOut.flagNoData = False
        pass
              