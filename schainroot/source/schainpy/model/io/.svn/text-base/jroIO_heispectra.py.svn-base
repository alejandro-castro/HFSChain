'''

'''

import os, sys
import time, datetime
import numpy
import fnmatch
import glob

try:
    import pyfits
except:
    """
    """

from xml.etree.ElementTree import ElementTree

from jroIO_base import isDoyFolder, isNumber
from model.proc.jroproc_base import Operation, ProcessingUnit

class ParameterConf:
    ELEMENTNAME = 'Parameter'
    def __init__(self):
        self.name = ''
        self.value = ''

    def readXml(self, parmElement):
        self.name = parmElement.get('name')
        self.value = parmElement.get('value')

    def getElementName(self):
        return self.ELEMENTNAME

class Metadata:
    
    def __init__(self, filename):
        self.parmConfObjList = []
        self.readXml(filename)
        
    def readXml(self, filename):
        self.projectElement = None
        self.procUnitConfObjDict = {}
        self.projectElement = ElementTree().parse(filename)
        self.project = self.projectElement.tag      

        parmElementList = self.projectElement.getiterator(ParameterConf().getElementName())
        
        for parmElement in parmElementList:
            parmConfObj = ParameterConf()
            parmConfObj.readXml(parmElement)
            self.parmConfObjList.append(parmConfObj)

class FitsWriter(Operation):
    
    def __init__(self):
        self.isConfig = False
        self.dataBlocksPerFile = None
        self.blockIndex = 0
        self.flagIsNewFile = 1
        self.fitsObj = None
        self.optchar = 'P'
        self.ext = '.fits'
        self.setFile = 0
        
    def setFitsHeader(self, dataOut, metadatafile):
        
        header_data = pyfits.PrimaryHDU()
        
        metadata4fits = Metadata(metadatafile)
        for parameter in metadata4fits.parmConfObjList:
            parm_name = parameter.name
            parm_value = parameter.value
            
#             if parm_value == 'fromdatadatetime':
#                 value = time.strftime("%b %d %Y %H:%M:%S", dataOut.datatime.timetuple())
#             elif parm_value == 'fromdataheights':
#                 value = dataOut.nHeights
#             elif parm_value == 'fromdatachannel':
#                 value = dataOut.nChannels
#             elif parm_value == 'fromdatasamples':
#                 value = dataOut.nFFTPoints
#             else:
#                 value = parm_value
                
            header_data.header[parm_name] = parm_value
            
        
        header_data.header['DATETIME'] = time.strftime("%b %d %Y %H:%M:%S", dataOut.datatime.timetuple())
        header_data.header['CHANNELLIST'] = str(dataOut.channelList)
        header_data.header['NCHANNELS'] = dataOut.nChannels
        #header_data.header['HEIGHTS'] = dataOut.heightList
        header_data.header['NHEIGHTS'] = dataOut.nHeights
        
        header_data.header['IPPSECONDS'] = dataOut.ippSeconds
        header_data.header['NCOHINT'] = dataOut.nCohInt
        header_data.header['NINCOHINT'] = dataOut.nIncohInt
        header_data.header['TIMEZONE'] = dataOut.timeZone
        header_data.header['NBLOCK'] = self.blockIndex
        
        header_data.writeto(self.filename)
        
        self.addExtension(dataOut.heightList,'HEIGHTLIST')
        
        
    def setup(self, dataOut, path, dataBlocksPerFile, metadatafile):
        
        self.path = path
        self.dataOut = dataOut
        self.metadatafile = metadatafile
        self.dataBlocksPerFile = dataBlocksPerFile
    
    def open(self):
        self.fitsObj = pyfits.open(self.filename, mode='update')

    
    def addExtension(self, data, tagname):
        self.open()
        extension = pyfits.ImageHDU(data=data, name=tagname)
        #extension.header['TAG'] = tagname
        self.fitsObj.append(extension)
        self.write()
    
    def addData(self, data):
        self.open()
        extension = pyfits.ImageHDU(data=data, name=self.fitsObj[0].header['DATATYPE'])
        extension.header['UTCTIME'] = self.dataOut.utctime
        self.fitsObj.append(extension)
        self.blockIndex += 1
        self.fitsObj[0].header['NBLOCK'] = self.blockIndex

        self.write()

    def write(self):
        
        self.fitsObj.flush(verbose=True)
        self.fitsObj.close()
        
    
    def setNextFile(self):

        ext = self.ext
        path = self.path
        
        timeTuple = time.localtime( self.dataOut.utctime)
        subfolder = 'd%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)

        fullpath = os.path.join( path, subfolder )
        if not( os.path.exists(fullpath) ):
            os.mkdir(fullpath)
            self.setFile = -1 #inicializo mi contador de seteo
        else:
            filesList = os.listdir( fullpath )
            if len( filesList ) > 0:
                filesList = sorted( filesList, key=str.lower )
                filen = filesList[-1]
 
                if isNumber( filen[8:11] ):
                    self.setFile = int( filen[8:11] ) #inicializo mi contador de seteo al seteo del ultimo file
                else:    
                    self.setFile = -1
            else:
                self.setFile = -1 #inicializo mi contador de seteo
                
        setFile = self.setFile
        setFile += 1
                
        file = '%s%4.4d%3.3d%3.3d%s' % (self.optchar,
                                        timeTuple.tm_year,
                                        timeTuple.tm_yday,
                                        setFile,
                                        ext )

        filename = os.path.join( path, subfolder, file )
        
        self.blockIndex = 0
        self.filename = filename
        self.setFile = setFile
        self.flagIsNewFile = 1

        print 'Writing the file: %s'%self.filename
                
        self.setFitsHeader(self.dataOut, self.metadatafile)
        
        return 1

    def writeBlock(self):
        self.addData(self.dataOut.data_spc)        
        self.flagIsNewFile = 0

    
    def __setNewBlock(self):

        if self.flagIsNewFile:
            return 1
        
        if self.blockIndex < self.dataBlocksPerFile:
            return 1
        
        if not( self.setNextFile() ):
            return 0
        
        return 1

    def writeNextBlock(self):
        if not( self.__setNewBlock() ):
            return 0
        self.writeBlock()
        return 1  
    
    def putData(self):        
        if self.flagIsNewFile:
            self.setNextFile()
        self.writeNextBlock()
        
    def run(self, dataOut, **kwargs):
        if not(self.isConfig):
            self.setup(dataOut, **kwargs)
            self.isConfig = True
        self.putData()
    
    
class FitsReader(ProcessingUnit):
    
#     __TIMEZONE = time.timezone
    
    expName = None
    datetimestr = None
    utc = None
    nChannels = None
    nSamples = None
    dataBlocksPerFile = None
    comments = None 
    lastUTTime = None
    header_dict = None
    data = None
    data_header_dict = None
    
    def __init__(self):
        self.isConfig = False
        self.ext = '.fits'
        self.setFile = 0
        self.flagNoMoreFiles = 0
        self.flagIsNewFile = 1
        self.flagTimeBlock = None
        self.fileIndex = None
        self.filename = None
        self.fileSize = None
        self.fitsObj = None
        self.timeZone = None
        self.nReadBlocks = 0
        self.nTotalBlocks = 0
        self.dataOut = self.createObjByDefault()
        self.maxTimeStep = 10# deberia ser definido por el usuario usando el metodo setup()
        self.blockIndex = 1 
    
    def createObjByDefault(self):
        
        dataObj = Fits()
        
        return dataObj
    
    def isFileinThisTime(self, filename, startTime, endTime, useLocalTime=False):
        try:
            fitsObj = pyfits.open(filename,'readonly')
        except:
            raise IOError, "The file %s can't be opened" %(filename)
        
        header = fitsObj[0].header
        struct_time = time.strptime(header['DATETIME'], "%b %d %Y %H:%M:%S")
        utc = time.mktime(struct_time) - time.timezone #TIMEZONE debe ser un parametro del header FITS
        
        ltc = utc
        if useLocalTime:
            ltc -= time.timezone
        thisDatetime = datetime.datetime.utcfromtimestamp(ltc)
        thisTime = thisDatetime.time()
        
        if not ((startTime <= thisTime) and (endTime > thisTime)):
            return None
        
        return thisDatetime
    
    def __setNextFileOnline(self):
        raise ValueError, "No implemented" 
    
    def __setNextFileOffline(self):
        idFile = self.fileIndex

        while (True):
            idFile += 1
            if not(idFile < len(self.filenameList)):
                self.flagNoMoreFiles = 1
                print "No more Files"
                return 0

            filename = self.filenameList[idFile]

#            if not(self.__verifyFile(filename)):
#                continue

            fileSize = os.path.getsize(filename)
            fitsObj = pyfits.open(filename,'readonly')
            break

        self.flagIsNewFile = 1
        self.fileIndex = idFile
        self.filename = filename
        self.fileSize = fileSize
        self.fitsObj = fitsObj
        self.blockIndex = 0
        print "Setting the file: %s"%self.filename

        return 1
    
    def readHeader(self):
        headerObj = self.fitsObj[0]
        
        self.header_dict = headerObj.header
        if 'EXPNAME' in headerObj.header.keys():
            self.expName = headerObj.header['EXPNAME']
        
        if 'DATATYPE' in headerObj.header.keys():
            self.dataType = headerObj.header['DATATYPE']
        
        self.datetimestr = headerObj.header['DATETIME']
        channelList = headerObj.header['CHANNELLIST']
        channelList = channelList.split('[')
        channelList = channelList[1].split(']')
        channelList = channelList[0].split(',')
        channelList = [int(ch) for ch in channelList]
        self.channelList = channelList
        self.nChannels = headerObj.header['NCHANNELS']
        self.nHeights = headerObj.header['NHEIGHTS']
        self.ippSeconds = headerObj.header['IPPSECONDS']
        self.nCohInt = headerObj.header['NCOHINT']
        self.nIncohInt = headerObj.header['NINCOHINT']
        self.dataBlocksPerFile = headerObj.header['NBLOCK']
        self.timeZone = headerObj.header['TIMEZONE']
        
#         self.timeInterval = self.ippSeconds * self.nCohInt * self.nIncohInt
        
        if 'COMMENT' in headerObj.header.keys():
            self.comments = headerObj.header['COMMENT']
        
        self.readHeightList()
    
    def readHeightList(self):
        self.blockIndex = self.blockIndex + 1
        obj = self.fitsObj[self.blockIndex]
        self.heightList = obj.data
        self.blockIndex = self.blockIndex + 1
    
    def readExtension(self):
        obj = self.fitsObj[self.blockIndex]
        self.heightList = obj.data
        self.blockIndex = self.blockIndex + 1
    
    def setNextFile(self):

        if self.online:
            newFile = self.__setNextFileOnline()
        else:
            newFile = self.__setNextFileOffline()

        if not(newFile):
            return 0
        
        self.readHeader()
        
        self.nReadBlocks = 0
#         self.blockIndex = 1
        return 1

    def __searchFilesOffLine(self,
                            path,
                            startDate,
                            endDate,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            set=None,
                            expLabel='',
                            ext='.fits',
                            walk=True):
        
        pathList = []
        
        if not walk:
            pathList.append(path)
        
        else:
            dirList = []
            for thisPath in os.listdir(path):
                if not os.path.isdir(os.path.join(path,thisPath)):
                    continue
                if not isDoyFolder(thisPath):
                    continue
                
                dirList.append(thisPath)
    
            if not(dirList):
                return None, None
            
            thisDate = startDate
            
            while(thisDate <= endDate):
                year = thisDate.timetuple().tm_year
                doy = thisDate.timetuple().tm_yday
                
                matchlist = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy) + '*')
                if len(matchlist) == 0:
                    thisDate += datetime.timedelta(1)
                    continue
                for match in matchlist:
                    pathList.append(os.path.join(path,match,expLabel))
                
                thisDate += datetime.timedelta(1)
        
        if pathList == []:
            print "Any folder was found for the date range: %s-%s" %(startDate, endDate)
            return None, None
        
        print "%d folder(s) was(were) found for the date range: %s - %s" %(len(pathList), startDate, endDate)
            
        filenameList = []
        datetimeList = []
        
        for i in range(len(pathList)):
            
            thisPath = pathList[i]
            
            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()
            
            for file in fileList:
                
                filename = os.path.join(thisPath,file)
                thisDatetime = self.isFileinThisTime(filename, startTime, endTime)
                
                if not(thisDatetime):
                    continue
                
                filenameList.append(filename)
                datetimeList.append(thisDatetime)
                
        if not(filenameList):
            print "Any file was found for the time range %s - %s" %(startTime, endTime)
            return None, None
        
        print "%d file(s) was(were) found for the time range: %s - %s" %(len(filenameList), startTime, endTime)
        print
        
        for i in range(len(filenameList)):
            print "%s -> [%s]" %(filenameList[i], datetimeList[i].ctime())

        self.filenameList = filenameList
        self.datetimeList = datetimeList
        
        return pathList, filenameList
    
    def setup(self, path=None,
                startDate=None, 
                endDate=None, 
                startTime=datetime.time(0,0,0), 
                endTime=datetime.time(23,59,59), 
                set=0, 
                expLabel = "", 
                ext = None, 
                online = False,
                delay = 60,
                walk = True):
        
        if path == None:
            raise ValueError, "The path is not valid"

        if ext == None:
            ext = self.ext
        
        if not(online):
            print "Searching files in offline mode ..."
            pathList, filenameList = self.__searchFilesOffLine(path, startDate=startDate, endDate=endDate,
                                                               startTime=startTime, endTime=endTime,
                                                               set=set, expLabel=expLabel, ext=ext,
                                                               walk=walk)
            
            if not(pathList):
                print "No *%s files into the folder %s \nfor the range: %s - %s"%(ext, path,
                                                        datetime.datetime.combine(startDate,startTime).ctime(),
                                                        datetime.datetime.combine(endDate,endTime).ctime())
                
                sys.exit(-1)

            self.fileIndex = -1
            self.pathList = pathList
            self.filenameList = filenameList
        
        self.online = online
        self.delay = delay
        ext = ext.lower()
        self.ext = ext

        if not(self.setNextFile()):
            if (startDate!=None) and (endDate!=None):
                print "No files in range: %s - %s" %(datetime.datetime.combine(startDate,startTime).ctime(), datetime.datetime.combine(endDate,endTime).ctime())
            elif startDate != None:
                print "No files in range: %s" %(datetime.datetime.combine(startDate,startTime).ctime())
            else:
                print "No files"

            sys.exit(-1)
    

    
    def readBlock(self):
        dataObj = self.fitsObj[self.blockIndex]

        self.data = dataObj.data
        self.data_header_dict = dataObj.header
        self.utc = self.data_header_dict['UTCTIME']
        
        self.flagIsNewFile = 0
        self.blockIndex += 1
        self.nTotalBlocks += 1
        self.nReadBlocks += 1
          
        return 1
    
    def __jumpToLastBlock(self):
        raise ValueError, "No implemented" 

    def __waitNewBlock(self):
        """
        Return 1 si se encontro un nuevo bloque de datos, 0 de otra forma. 
        
        Si el modo de lectura es OffLine siempre retorn 0
        """
        if not self.online:
            return 0
        
        if (self.nReadBlocks >= self.dataBlocksPerFile):
            return 0
        
        currentPointer = self.fp.tell()
        
        neededSize = self.processingHeaderObj.blockSize + self.basicHeaderSize
        
        for nTries in range( self.nTries ):
            
            self.fp.close()
            self.fp = open( self.filename, 'rb' )
            self.fp.seek( currentPointer )

            self.fileSize = os.path.getsize( self.filename )
            currentSize = self.fileSize - currentPointer

            if ( currentSize >= neededSize ):
                self.__rdBasicHeader()
                return 1
            
            print "\tWaiting %0.2f seconds for the next block, try %03d ..." % (self.delay, nTries+1)
            time.sleep( self.delay )
            
        
        return 0
    
    def __setNewBlock(self):

        if self.online:
            self.__jumpToLastBlock()
        
        if self.flagIsNewFile:
            return 1
        
        self.lastUTTime = self.utc

        if self.online:
            if self.__waitNewBlock():
                return 1
        
        if self.nReadBlocks < self.dataBlocksPerFile:
            return 1
        
        if not(self.setNextFile()):
            return 0
        
        deltaTime = self.utc - self.lastUTTime 
        
        self.flagTimeBlock = 0

        if deltaTime > self.maxTimeStep:
            self.flagTimeBlock = 1

        return 1
    
    
    def readNextBlock(self):
        if not(self.__setNewBlock()):
            return 0

        if not(self.readBlock()):
            return 0

        return 1
    
    
    def getData(self):
        
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            print 'Process finished'
            return 0
        
        self.flagTimeBlock = 0
        self.flagIsNewBlock = 0

        if not(self.readNextBlock()):
            return 0
        
        if self.data == None:
            self.dataOut.flagNoData = True
            return 0
        
        self.dataOut.data = self.data
        self.dataOut.data_header = self.data_header_dict
        self.dataOut.utctime = self.utc
        
        self.dataOut.header = self.header_dict 
        self.dataOut.expName = self.expName
        self.dataOut.nChannels = self.nChannels
        self.dataOut.timeZone = self.timeZone
        self.dataOut.dataBlocksPerFile = self.dataBlocksPerFile
        self.dataOut.comments = self.comments 
        self.dataOut.timeInterval = self.timeInterval
        self.dataOut.channelList = self.channelList
        self.dataOut.heightList = self.heightList
        self.dataOut.flagNoData = False
        
        return self.dataOut.data
    
    def run(self, **kwargs):
    
        if not(self.isConfig):
            self.setup(**kwargs)
            self.isConfig = True
            
        self.getData()

class SpectraHeisWriter(Operation):    
#    set = None
    setFile = None
    idblock = None
    doypath = None
    subfolder = None
    
    def __init__(self):
        self.wrObj = FITS()
#        self.dataOut = dataOut 
        self.nTotalBlocks=0
#        self.set = None
        self.setFile = None
        self.idblock = 0
        self.wrpath = None
        self.doypath = None
        self.subfolder = None
        self.isConfig = False 
        
    def isNumber(str):
        """
        Chequea si el conjunto de caracteres que componen un string puede ser convertidos a un numero.

        Excepciones: 
        Si un determinado string no puede ser convertido a numero
        Input:
        str, string al cual se le analiza para determinar si convertible a un numero o no
        
        Return:
        True    :    si el string es uno numerico
        False   :    no es un string numerico
        """
        try:
            float( str )
            return True
        except:
            return False   
        
    def setup(self, dataOut, wrpath):

        if not(os.path.exists(wrpath)):
            os.mkdir(wrpath)
       
        self.wrpath = wrpath
#        self.setFile = 0
        self.dataOut = dataOut

    def putData(self):
        name= time.localtime( self.dataOut.utctime)
        ext=".fits"    
           
        if self.doypath == None:
           self.subfolder = 'F%4.4d%3.3d_%d' % (name.tm_year,name.tm_yday,time.mktime(datetime.datetime.now().timetuple()))
           self.doypath = os.path.join( self.wrpath, self.subfolder )
           os.mkdir(self.doypath)
        
        if self.setFile == None:
#           self.set = self.dataOut.set
           self.setFile = 0
#        if self.set != self.dataOut.set:
##            self.set = self.dataOut.set
#            self.setFile = 0
        
        #make the filename
        file = 'D%4.4d%3.3d_%3.3d%s' % (name.tm_year,name.tm_yday,self.setFile,ext) 

        filename = os.path.join(self.wrpath,self.subfolder, file) 
        
        idblock = numpy.array([self.idblock],dtype="int64")
        header=self.wrObj.cFImage(idblock=idblock, 
                                year=time.gmtime(self.dataOut.utctime).tm_year,
                                month=time.gmtime(self.dataOut.utctime).tm_mon,
                                day=time.gmtime(self.dataOut.utctime).tm_mday, 
                                hour=time.gmtime(self.dataOut.utctime).tm_hour,
                                minute=time.gmtime(self.dataOut.utctime).tm_min, 
                                second=time.gmtime(self.dataOut.utctime).tm_sec)
        
        c=3E8
        deltaHeight = self.dataOut.heightList[1] - self.dataOut.heightList[0]
        freq=numpy.arange(-1*self.dataOut.nHeights/2.,self.dataOut.nHeights/2.)*(c/(2*deltaHeight*1000))
        
        colList = []
        
        colFreq=self.wrObj.setColF(name="freq", format=str(self.dataOut.nFFTPoints)+'E', array=freq)
        
        colList.append(colFreq)

        nchannel=self.dataOut.nChannels
        
        for i in range(nchannel):
            col = self.wrObj.writeData(name="PCh"+str(i+1),
                                         format=str(self.dataOut.nFFTPoints)+'E',
                                          data=10*numpy.log10(self.dataOut.data_spc[i,:]))
            
            colList.append(col)
                
        data=self.wrObj.Ctable(colList=colList)
        
        self.wrObj.CFile(header,data)
        
        self.wrObj.wFile(filename)      
        
        #update the setFile
        self.setFile += 1
        self.idblock += 1
        
        return 1
    
    def run(self, dataOut, **kwargs):
        
        if not(self.isConfig):
            
            self.setup(dataOut, **kwargs)
            self.isConfig = True
            
        self.putData()