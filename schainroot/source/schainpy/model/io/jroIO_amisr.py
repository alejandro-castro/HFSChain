'''
@author: Daniel Suarez
'''

import os
import sys
import glob
import fnmatch
import datetime
import time
import re
import h5py
import numpy

from model.proc.jroproc_base import ProcessingUnit, Operation
from model.data.jroamisr import AMISR

class RadacHeader():
    def __init__(self, fp):
        header = 'Raw11/Data/RadacHeader'
        self.beamCodeByPulse = fp.get(header+'/BeamCode')
        self.beamCode = fp.get('Raw11/Data/Beamcodes')
        self.code = fp.get(header+'/Code')
        self.frameCount = fp.get(header+'/FrameCount')
        self.modeGroup = fp.get(header+'/ModeGroup')
        self.nsamplesPulse = fp.get(header+'/NSamplesPulse')
        self.pulseCount = fp.get(header+'/PulseCount')
        self.radacTime = fp.get(header+'/RadacTime')
        self.timeCount = fp.get(header+'/TimeCount')
        self.timeStatus = fp.get(header+'/TimeStatus')
        
        self.nrecords = self.pulseCount.shape[0] #nblocks
        self.npulses = self.pulseCount.shape[1] #nprofile
        self.nsamples = self.nsamplesPulse[0,0] #ngates
        self.nbeams = self.beamCode.shape[1]
        
    
    def getIndexRangeToPulse(self, idrecord=0):
        #indexToZero = numpy.where(self.pulseCount.value[idrecord,:]==0)
        #startPulseCountId = indexToZero[0][0]
        #endPulseCountId = startPulseCountId - 1
        #range1 = numpy.arange(startPulseCountId,self.npulses,1)
        #range2 = numpy.arange(0,startPulseCountId,1)
        #return range1, range2
        zero = 0
        npulse = max(self.pulseCount[0,:]+1)-1
        looking_index = numpy.where(self.pulseCount.value[idrecord,:]==npulse)[0]
        getLastIndex = looking_index[-1]
        index_data = numpy.arange(0,getLastIndex+1,1)
        index_buffer = numpy.arange(getLastIndex+1,self.npulses,1)
        return index_data, index_buffer
    
class AMISRReader(ProcessingUnit):
    
    path = None
    startDate = None
    endDate = None
    startTime = None
    endTime = None
    walk = None
    isConfig = False
    
    def __init__(self):
        self.set = None
        self.subset = None
        self.extension_file = '.h5'
        self.dtc_str = 'dtc'
        self.dtc_id = 0
        self.status = True
        self.isConfig = False
        self.dirnameList = []
        self.filenameList = []
        self.fileIndex = None
        self.flagNoMoreFiles = False
        self.flagIsNewFile = 0
        self.filename = ''
        self.amisrFilePointer = None
        self.radacHeaderObj = None
        self.dataOut = self.__createObjByDefault()
        self.datablock = None
        self.rest_datablock = None
        self.range = None
        self.idrecord_count = 0
        self.profileIndex = 0
        self.index_amisr_sample = None 
        self.index_amisr_buffer = None
        self.beamCodeByFrame = None
        self.radacTimeByFrame = None
        #atributos originales tal y como esta en el archivo de datos
        self.beamCodesFromFile = None
        self.radacTimeFromFile = None
        self.rangeFromFile = None
        self.dataByFrame = None
        self.dataset = None
        
        self.beamCodeDict = {}
        self.beamRangeDict = {}
        
        #experiment cgf file
        self.npulsesint_fromfile = None
        self.recordsperfile_fromfile = None
        self.nbeamcodes_fromfile = None
        self.ngates_fromfile = None
        self.ippSeconds_fromfile = None
        self.frequency_h5file = None
        
        
        self.__firstFile = True
        self.buffer_radactime = None
        
        self.index4_schain_datablock = None
        self.index4_buffer = None
        self.schain_datablock = None
        self.buffer = None
        self.linear_pulseCount = None
        self.npulseByFrame = None
        self.profileIndex_offset = None
        self.timezone = 'ut'
        
        self.__waitForNewFile = 20
        self.__filename_online = None 
        
    def __createObjByDefault(self):
        
        dataObj = AMISR()
        
        return dataObj
    
    def __setParameters(self,path='', startDate='',endDate='',startTime='', endTime='', walk=''):
        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.walk = walk
    
    def __checkPath(self):
        if os.path.exists(self.path):
            self.status = 1
        else:
            self.status = 0
            print 'Path:%s does not exists'%self.path
            
        return
    
    def __selDates(self, amisr_dirname_format):
        try:
            year = int(amisr_dirname_format[0:4])
            month = int(amisr_dirname_format[4:6])
            dom = int(amisr_dirname_format[6:8])
            thisDate = datetime.date(year,month,dom)
            
            if (thisDate>=self.startDate and thisDate <= self.endDate):
                return amisr_dirname_format
        except:
            return None
    
    def __findDataForDates(self,online=False):
        
        
        
        if not(self.status):
            return None
        
        pat = '\d+.\d+'
        dirnameList = [re.search(pat,x) for x in os.listdir(self.path)]
        dirnameList = filter(lambda x:x!=None,dirnameList)
        dirnameList = [x.string for x in dirnameList]
        if not(online):
            dirnameList = [self.__selDates(x) for x in dirnameList]
            dirnameList = filter(lambda x:x!=None,dirnameList)
        if len(dirnameList)>0:
            self.status = 1
            self.dirnameList = dirnameList
            self.dirnameList.sort()
        else:
            self.status = 0
            return None
    
    def __getTimeFromData(self):
        startDateTime_Reader = datetime.datetime.combine(self.startDate,self.startTime)
        endDateTime_Reader = datetime.datetime.combine(self.endDate,self.endTime)

        print 'Filtering Files from %s to %s'%(startDateTime_Reader, endDateTime_Reader)
        print '........................................'
        filter_filenameList = []
        self.filenameList.sort()
        for i in range(len(self.filenameList)-1):
            filename = self.filenameList[i]
            fp = h5py.File(filename,'r')
            time_str = fp.get('Time/RadacTimeString')
            
            startDateTimeStr_File = time_str[0][0].split('.')[0]
            junk = time.strptime(startDateTimeStr_File, '%Y-%m-%d %H:%M:%S')
            startDateTime_File = datetime.datetime(junk.tm_year,junk.tm_mon,junk.tm_mday,junk.tm_hour, junk.tm_min, junk.tm_sec)
            
            endDateTimeStr_File = time_str[-1][-1].split('.')[0]
            junk = time.strptime(endDateTimeStr_File, '%Y-%m-%d %H:%M:%S')
            endDateTime_File = datetime.datetime(junk.tm_year,junk.tm_mon,junk.tm_mday,junk.tm_hour, junk.tm_min, junk.tm_sec)
            
            fp.close()
            
            if self.timezone == 'lt':
                startDateTime_File = startDateTime_File - datetime.timedelta(minutes = 300)
                endDateTime_File = endDateTime_File - datetime.timedelta(minutes = 300)

            if (endDateTime_File>=startDateTime_Reader and endDateTime_File<endDateTime_Reader):
                #self.filenameList.remove(filename)
                filter_filenameList.append(filename)
        
        filter_filenameList.sort()
        self.filenameList = filter_filenameList
        return 1
    
    def __filterByGlob1(self, dirName):
        filter_files = glob.glob1(dirName, '*.*%s'%self.extension_file)
        filterDict = {}
        filterDict.setdefault(dirName)
        filterDict[dirName] = filter_files
        return filterDict
    
    def __getFilenameList(self, fileListInKeys, dirList):
        for value in fileListInKeys:
            dirName = value.keys()[0]
            for file in value[dirName]:
                filename = os.path.join(dirName, file)
                self.filenameList.append(filename)
    
    
    def __selectDataForTimes(self, online=False):
        #aun no esta implementado el filtro for tiempo
        if not(self.status):
            return None
        
        dirList = [os.path.join(self.path,x) for x in self.dirnameList]
        
        fileListInKeys = [self.__filterByGlob1(x) for x in dirList]
        
        self.__getFilenameList(fileListInKeys, dirList)
        if not(online):
            #filtro por tiempo
            if not(self.all):
                self.__getTimeFromData()

            if len(self.filenameList)>0:
                self.status = 1
                self.filenameList.sort()
            else:
                self.status = 0
                return None
            
        else:
            #get the last file - 1
            self.filenameList = [self.filenameList[-2]]
        
        new_dirnameList = []
        for dirname in self.dirnameList:
            junk = numpy.array([dirname in x for x in self.filenameList])
            junk_sum = junk.sum()
            if junk_sum > 0:
                new_dirnameList.append(dirname)
        self.dirnameList = new_dirnameList
        return 1
        
    def __searchFilesOnline(self,
                            path,
                            walk=True):
        
        startDate = datetime.datetime.utcnow().date()
        endDate = datetime.datetime.utcnow().date()
        
        self.__setParameters(path=path, startDate=startDate, endDate=endDate, walk=walk)
        
        self.__checkPath()
        
        self.__findDataForDates(online=True)
        
        self.dirnameList = [self.dirnameList[-1]]
        
        self.__selectDataForTimes(online=True)
        
        return
        
    
    def __searchFilesOffline(self,
                            path,
                            startDate,
                            endDate,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            walk=True):
        
        self.__setParameters(path, startDate, endDate, startTime, endTime, walk)
        
        self.__checkPath()
        
        self.__findDataForDates()
        
        self.__selectDataForTimes()
        
        for i in range(len(self.filenameList)):
            print "%s" %(self.filenameList[i])
        
        return

    def __setNextFileOffline(self):
        idFile = self.fileIndex

        while (True):
            idFile += 1
            if not(idFile < len(self.filenameList)):
                self.flagNoMoreFiles = 1
                print "No more Files"
                return 0

            filename = self.filenameList[idFile]

            amisrFilePointer = h5py.File(filename,'r')
            
            break

        self.flagIsNewFile = 1
        self.fileIndex = idFile
        self.filename = filename

        self.amisrFilePointer = amisrFilePointer

        print "Setting the file: %s"%self.filename

        return 1
    
    
    def __setNextFileOnline(self):
        filename = self.filenameList[0]
        if self.__filename_online != None:
            self.__selectDataForTimes(online=True)
            filename = self.filenameList[0]
            while self.__filename_online == filename:
                print 'waiting %d seconds to get a new file...'%(self.__waitForNewFile)
                time.sleep(self.__waitForNewFile)
                self.__selectDataForTimes(online=True)
                filename = self.filenameList[0]
        
        self.__filename_online = filename
        
        self.amisrFilePointer = h5py.File(filename,'r')
        self.flagIsNewFile = 1
        self.filename = filename
        print "Setting the file: %s"%self.filename
        return 1
    
    
    def __readHeader(self):
        self.radacHeaderObj = RadacHeader(self.amisrFilePointer)
        
        #update values from experiment cfg file
        if self.radacHeaderObj.nrecords == self.recordsperfile_fromfile:
            self.radacHeaderObj.nrecords = self.recordsperfile_fromfile
        self.radacHeaderObj.nbeams = self.nbeamcodes_fromfile
        self.radacHeaderObj.npulses = self.npulsesint_fromfile
        self.radacHeaderObj.nsamples = self.ngates_fromfile
        
        #looking index list for data
        start_index = self.radacHeaderObj.pulseCount[0,:][0]
        end_index = self.radacHeaderObj.npulses
        range4data = range(start_index, end_index)
        self.index4_schain_datablock = numpy.array(range4data)
        
        buffer_start_index = 0
        buffer_end_index = self.radacHeaderObj.pulseCount[0,:][0]
        range4buffer = range(buffer_start_index, buffer_end_index)
        self.index4_buffer = numpy.array(range4buffer)
        
        self.linear_pulseCount = numpy.array(range4data + range4buffer)
        self.npulseByFrame = max(self.radacHeaderObj.pulseCount[0,:]+1)

        #get tuning frequency
        frequency_h5file_dataset = self.amisrFilePointer.get('Rx'+'/TuningFrequency')
        self.frequency_h5file = frequency_h5file_dataset[0,0]
        
        self.flagIsNewFile = 1
    
    def __getBeamCode(self):
        self.beamCodeDict = {}
        self.beamRangeDict = {}
        
        beamCodeMap = self.amisrFilePointer.get('Setup/BeamcodeMap')
        
        for i in range(len(self.radacHeaderObj.beamCode[0,:])):
            self.beamCodeDict.setdefault(i)
            self.beamRangeDict.setdefault(i)
            beamcodeValue = self.radacHeaderObj.beamCode[0,i]
            beamcodeIndex = numpy.where(beamCodeMap[:,0] == beamcodeValue)[0][0]
            x = beamCodeMap[beamcodeIndex][1]
            y = beamCodeMap[beamcodeIndex][2]
            z = beamCodeMap[beamcodeIndex][3]
            self.beamCodeDict[i] = [beamcodeValue, x, y, z]
            
        just4record0 = self.radacHeaderObj.beamCodeByPulse[0,:]
        
        for i in range(len(self.beamCodeDict.values())):
            xx = numpy.where(just4record0==self.beamCodeDict.values()[i][0])
            indexPulseByBeam = self.linear_pulseCount[xx[0]]
            self.beamRangeDict[i] = indexPulseByBeam
    
    def __getExpParameters(self):
        if not(self.status):
            return None
        
        experimentCfgPath = os.path.join(self.path, self.dirnameList[0], 'Setup')
        
        expFinder = glob.glob1(experimentCfgPath,'*.exp')
        if len(expFinder)== 0:
            self.status = 0
            return None
        
        experimentFilename = os.path.join(experimentCfgPath,expFinder[0])
        
        f = open(experimentFilename)
        lines = f.readlines()
        f.close()
        
        parmsList = ['npulsesint*','recordsperfile*','nbeamcodes*','ngates*']
        filterList = [fnmatch.filter(lines, x) for x in parmsList]

        
        values = [re.sub(r'\D',"",x[0]) for x in filterList]
        
        self.npulsesint_fromfile = int(values[0])
        self.recordsperfile_fromfile = int(values[1])
        self.nbeamcodes_fromfile = int(values[2])
        self.ngates_fromfile = int(values[3])
        
        tufileFinder = fnmatch.filter(lines, 'tufile=*')
        tufile = tufileFinder[0].split('=')[1].split('\n')[0]
        tufile = tufile.split('\r')[0]
        tufilename = os.path.join(experimentCfgPath,tufile)
        
        f = open(tufilename)
        lines = f.readlines()
        f.close()
        self.ippSeconds_fromfile = float(lines[1].split()[2])/1E6
        
        
        self.status = 1
    
    def __setIdsAndArrays(self):
        self.dataByFrame = self.__setDataByFrame()
        self.beamCodeByFrame = self.amisrFilePointer.get('Raw11/Data/RadacHeader/BeamCode').value[0, :]        
        self.readRanges()
        self.index_amisr_sample, self.index_amisr_buffer = self.radacHeaderObj.getIndexRangeToPulse(0)
        self.radacTimeByFrame = numpy.zeros(self.radacHeaderObj.npulses)
        if len(self.index_amisr_buffer) > 0:
            self.buffer_radactime = numpy.zeros_like(self.radacTimeByFrame)
        
    
    def __setNextFile(self,online=False):
        
        if not(online):
            newFile = self.__setNextFileOffline()
        else:
            newFile = self.__setNextFileOnline() 
        
        if not(newFile):
            return 0
        
        self.__readHeader()
        
        if self.__firstFile:
            self.__setIdsAndArrays()
            self.__firstFile = False
        
        self.__getBeamCode()
        self.readDataBlock()

    
    def setup(self,path=None,
                    startDate=None, 
                    endDate=None, 
                    startTime=datetime.time(0,0,0), 
                    endTime=datetime.time(23,59,59),
                    walk=True,
                    timezone='ut',
                    all=0,
                    online=False):
        
        self.timezone = timezone
        self.all = all
        self.online = online
        if not(online):
            #Busqueda de archivos offline
            self.__searchFilesOffline(path, startDate, endDate, startTime, endTime, walk)
        else:
            self.__searchFilesOnline(path, walk)
        
        if not(self.filenameList):
            print "There is no files into the folder: %s"%(path)
                
            sys.exit(-1)

        self.__getExpParameters()

        self.fileIndex = -1
        
        self.__setNextFile(online)
        
#         first_beamcode = self.radacHeaderObj.beamCodeByPulse[0,0]
#         index = numpy.where(self.radacHeaderObj.beamCodeByPulse[0,:]!=first_beamcode)[0][0]
        self.profileIndex_offset = self.radacHeaderObj.pulseCount[0,:][0]
        self.profileIndex = self.profileIndex_offset
    
    def readRanges(self):
        dataset = self.amisrFilePointer.get('Raw11/Data/Samples/Range')
        
        self.rangeFromFile = numpy.reshape(dataset.value,(-1))
        return self.rangeFromFile
    
    
    def readRadacTime(self,idrecord, range1, range2):
        self.radacTimeFromFile = self.radacHeaderObj.radacTime.value
        
        radacTimeByFrame = numpy.zeros((self.radacHeaderObj.npulses))
        #radacTimeByFrame = dataset[idrecord - 1,range1]
        #radacTimeByFrame = dataset[idrecord,range2]
        
        return radacTimeByFrame
        
    def readBeamCode(self, idrecord, range1, range2):
        dataset = self.amisrFilePointer.get('Raw11/Data/RadacHeader/BeamCode')
        beamcodeByFrame = numpy.zeros((self.radacHeaderObj.npulses))
        self.beamCodesFromFile = dataset.value
        
        #beamcodeByFrame[range1] = dataset[idrecord - 1, range1]
        #beamcodeByFrame[range2] = dataset[idrecord, range2]
        beamcodeByFrame[range1] = dataset[idrecord, range1]
        beamcodeByFrame[range2] = dataset[idrecord, range2]
        
        return beamcodeByFrame
    
    
    def __setDataByFrame(self):
        ndata = 2 # porque es complejo
        dataByFrame = numpy.zeros((self.radacHeaderObj.npulses, self.radacHeaderObj.nsamples, ndata))
        return dataByFrame
    
    def __readDataSet(self):
        dataset = self.amisrFilePointer.get('Raw11/Data/Samples/Data')
        return dataset

    def __setDataBlock(self,):
        real = self.dataByFrame[:,:,0] #asumo que 0 es real
        imag = self.dataByFrame[:,:,1] #asumo que 1 es imaginario
        datablock = real + imag*1j #armo el complejo
        return datablock
    
    def readSamples_version1(self,idrecord):
        #estas tres primeras lineas solo se deben ejecutar una vez
        if self.flagIsNewFile:
            #reading dataset
            self.dataset = self.__readDataSet()    
            self.flagIsNewFile = 0
        
        if idrecord == 0:
            self.dataByFrame[self.index4_schain_datablock, : ,:] = self.dataset[0, self.index_amisr_sample,:,:]
            self.radacTimeByFrame[self.index4_schain_datablock] = self.radacHeaderObj.radacTime[0, self.index_amisr_sample]
            datablock = self.__setDataBlock()
            if len(self.index_amisr_buffer) > 0:
                self.buffer = self.dataset[0, self.index_amisr_buffer,:,:]
                self.buffer_radactime = self.radacHeaderObj.radacTime[0, self.index_amisr_buffer]
            
            return datablock
        if len(self.index_amisr_buffer) > 0:
            self.dataByFrame[self.index4_buffer,:,:] = self.buffer.copy()
            self.radacTimeByFrame[self.index4_buffer] = self.buffer_radactime.copy()
        self.dataByFrame[self.index4_schain_datablock,:,:] = self.dataset[idrecord, self.index_amisr_sample,:,:]
        self.radacTimeByFrame[self.index4_schain_datablock] = self.radacHeaderObj.radacTime[idrecord, self.index_amisr_sample]
        datablock = self.__setDataBlock()
        if len(self.index_amisr_buffer) > 0:
            self.buffer = self.dataset[idrecord, self.index_amisr_buffer, :, :]
            self.buffer_radactime = self.radacHeaderObj.radacTime[idrecord, self.index_amisr_buffer]    
        
        return datablock
        
    
    def readSamples(self,idrecord):
        if self.flagIsNewFile:
            self.dataByFrame = self.__setDataByFrame()        
            self.beamCodeByFrame = self.amisrFilePointer.get('Raw11/Data/RadacHeader/BeamCode').value[idrecord, :]
                
            #reading ranges
            self.readRanges()
            #reading dataset
            self.dataset = self.__readDataSet()
        
        self.flagIsNewFile = 0
        self.radacTimeByFrame = self.radacHeaderObj.radacTime.value[idrecord, :]
        self.dataByFrame = self.dataset[idrecord, :, :, :]
        datablock = self.__setDataBlock()
        return datablock
    
    
    def readDataBlock(self):
        
        self.datablock = self.readSamples_version1(self.idrecord_count)
        #self.datablock = self.readSamples(self.idrecord_count)
        #print 'record:', self.idrecord_count
        
        self.idrecord_count += 1 
        self.profileIndex = 0
        
        if self.idrecord_count >= self.radacHeaderObj.nrecords:
            self.idrecord_count = 0
            self.flagIsNewFile = 1
    
    def readNextBlock(self):
        
        self.readDataBlock()
        
        if self.flagIsNewFile:
            self.__setNextFile(self.online)
        pass
    
    def __hasNotDataInBuffer(self):
        #self.radacHeaderObj.npulses debe ser otra variable para considerar el numero de pulsos a tomar en el primer y ultimo record
        if self.profileIndex >= self.radacHeaderObj.npulses:
            return 1
        return 0
    
    def printUTC(self):
        print self.dataOut.utctime
        print ''
    
    def setObjProperties(self):
        
        self.dataOut.heightList = self.rangeFromFile/1000.0 #km
        self.dataOut.nProfiles = self.radacHeaderObj.npulses
        self.dataOut.nRecords = self.radacHeaderObj.nrecords
        self.dataOut.nBeams = self.radacHeaderObj.nbeams
        self.dataOut.ippSeconds = self.ippSeconds_fromfile
#         self.dataOut.timeInterval = self.dataOut.ippSeconds * self.dataOut.nCohInt
        self.dataOut.frequency = self.frequency_h5file
        self.dataOut.npulseByFrame = self.npulseByFrame
        self.dataOut.nBaud = None
        self.dataOut.nCode = None
        self.dataOut.code = None
        
        self.dataOut.beamCodeDict = self.beamCodeDict
        self.dataOut.beamRangeDict = self.beamRangeDict
        
        if self.timezone == 'lt':
            self.dataOut.timeZone = time.timezone / 60. #get the timezone in minutes
        else: 
            self.dataOut.timeZone = 0 #by default time is UTC
            
    def getData(self):
        
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            print 'Process finished'
            return 0
        
        if self.__hasNotDataInBuffer():
            self.readNextBlock()

        
        if self.datablock == None: # setear esta condicion cuando no hayan datos por leers
            self.dataOut.flagNoData = True 
            return 0
        
        self.dataOut.data = numpy.reshape(self.datablock[self.profileIndex,:],(1,-1))
        
        self.dataOut.utctime = self.radacTimeByFrame[self.profileIndex]
        self.dataOut.profileIndex = self.profileIndex
        self.dataOut.flagNoData = False
        
        self.profileIndex += 1
        
        return self.dataOut.data


    def run(self, **kwargs):
        if not(self.isConfig):
            self.setup(**kwargs)
            self.setObjProperties()
            self.isConfig = True
        
        self.getData()
