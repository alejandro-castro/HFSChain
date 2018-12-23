'''
Created on Jul 3, 2014

@author: roj-com0419
'''

import os,sys
import time,datetime
import h5py
import numpy
import fnmatch
import glob
import traceback

from model.data.jroheaderIO import RadarControllerHeader, SystemHeader
from model.data.jrodata import Voltage
from model.proc.jroproc_base import ProcessingUnit, Operation


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

def isFileinThisTime(filename,startDate,endDate,startTime,endTime,timezone):
    startDateTime_Reader = datetime.datetime.combine(startDate,startTime)
    endDateTime_Reader = datetime.datetime.combine(endDate,endTime)
    try:
        fp= h5py.File(filename,'r')
    except IOError:
        traceback.print_exc()
        raise IOError, "The file %s can't be opened" %(filename)

    hipoc=fp['t'].value
    hipoc=hipoc+timezone
    date_time=datetime.datetime.utcfromtimestamp(hipoc)
    print date_time
    fp.close()

    this_time=date_time

    if not ((startDateTime_Reader <= this_time) and (endDateTime_Reader> this_time)):
       return None

    return this_time

def verifyFile(filename,size):
    sizeoffile=os.path.getsize(filename)
    if not (sizeoffile==size):
        return None

    return sizeoffile


def isDoyFolder(folder):
    try:
        year = int(folder[1:5])
    except:
        return 0

    try:
        doy = int(folder[5:8])
    except:
        return 0

    return 1

def getFileFromSet(path, ext, set=None):
    validFilelist = []
    fileList = os.listdir(path)


    if len(fileList) < 1:
        return None

    # 0 1234 567 89A BCDE
    # H YYYY DDD SSS .ext

    for thisFile in fileList:
        try:
            number= int(thisFile[7:17])
     #       year = int(thisFile[1:5])
     #       doy  = int(thisFile[5:8])
        except:
            continue

        if (os.path.splitext(thisFile)[-1].lower() != ext.lower()):
            continue

        validFilelist.append(thisFile)

    if len(validFilelist) < 1:
        return None

    validFilelist = sorted( validFilelist, key=str.lower )

    if set == None:
        return validFilelist[-1]

    #print "set =" ,set
    for thisFile in validFilelist:
        if set <= int(thisFile[7:17]):
            #print thisFile,int(thisFile[7:17])
            return thisFile

    return validFilelist[-1]

    myfile = fnmatch.filter(validFilelist,'*%10d*'%(set))
    #myfile = fnmatch.filter(validFilelist,'*%4.4d%3.3d%3.3d*'%(year,doy,set))

    if len(myfile)!= 0:
        return myfile[0]
    else:
        filename = '*%10.10d%s'%(set,ext.lower())
        print 'the filename %s does not exist'%filename
        print '...going to the last file: '

    if validFilelist:
        validFilelist = sorted( validFilelist, key=str.lower )
        return validFilelist[-1]

    return None

def getlastFileFromPath(path, ext):
    """
    Depura el fileList dejando solo los que cumplan el formato de "res-xxxxxx.ext"
    al final de la depuracion devuelve el ultimo file de la lista que quedo.

    Input:
        fileList    :    lista conteniendo todos los files (sin path) que componen una determinada carpeta
        ext         :    extension de los files contenidos en una carpeta

    Return:
        El ultimo file de una determinada carpeta, no se considera el path.
    """
    validFilelist = []
    fileList = os.listdir(path)

    # 0 1234 567 89A BCDE
    # H YYYY DDD SSS .ext

    for thisFile in fileList:

        try:
            number= int(thisFile[7:17])
        except:
            print "There is a file or folder with different format"
        if not isNumber(number):
            continue

#        year = thisFile[1:5]
#        if not isNumber(year):
#            continue

#       doy = thisFile[5:8]
#        if not isNumber(doy):
#            continue

        number= int(number)
#        year = int(year)
#        doy = int(doy)

        if (os.path.splitext(thisFile)[-1].lower() != ext.lower()):
            continue


        validFilelist.append(thisFile)


    if validFilelist:
        validFilelist = sorted( validFilelist, key=str.lower )
        return validFilelist[-1]

    return None

class HFReader(ProcessingUnit):
    '''
    classdocs
    '''
    path     = None
    startDate= None
    endDate  = None
    startTime= None
    endTime  = None
    walk     = None
    isConfig = False
    dataOut=None
    nTries = 3
    ext      = ".hdf5"

    def __init__(self):
        '''
        Constructor
        '''
        ProcessingUnit.__init__(self)

        self.isConfig =False

        self.datablock = None

        self.dataImage = None

        self.filename_current=None

        self.utc = 0

        self.ext='.hdf5'

        self.flagIsNewFile = 1

        #-------------------------------------------------
        self.fileIndex=None

        self.profileIndex_offset=None

        self.filenameList=[]

        self.hfFilePointer= None

        self.filename_online = None

        self.status=True

        self.flagNoMoreFiles= False

        self.__waitForNewFile = 45

        self.__inc_int = 0

        self.sizeofHF_File= None

        self.campaign = 1

        #--------------------------------------------------

        self.dataOut = self.createObjByDefault()


    def createObjByDefault(self):

        dataObj = Voltage()

        return dataObj

    def setObjProperties(self):

        pass

    def getBlockDimension(self):
        """
        Obtiene la cantidad de puntos a leer por cada bloque de datos

        Affected:
            self.blocksize

        Return:
            None
        """
        pts2read =self.nChannels*self.nHeights*self.nProfiles
        self.blocksize = pts2read

    def __readHeader(self):

	#self.nProfiles = 100#600
        self.nHeights = 1000
        self.nChannels =2
        self.__firstHeigth=0
        self.__nSamples=1000
        self.__deltaHeigth=1.5
        self.__sample_rate=1e5
        self.__frequency=None
        self.__online = False
        self.filename_next_set=None

    def __setParameters(self,path='',frequency='', startDate='',endDate='',startTime='', endTime='', walk=''):
        self.path = path
        self.frequency=frequency
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.walk = walk

    def __checkPath(self):
        if os.path.exists(self.path):
            self.status=1
        else:
            self.status=0
            print 'Path %s does not exits'%self.path
            return
        return

    def __selDates(self, hf_dirname_format):
        try:
            dir_hf_filename= self.path+"/"+hf_dirname_format
            fp= h5py.File(dir_hf_filename,'r')
            hipoc=fp['t'].value
            fp.close()
            date_time=datetime.datetime.utcfromtimestamp(hipoc)
            thisDate= date_time
            if (thisDate>=self.startDate and thisDate <= self.endDate):
                return hf_dirname_format
        except:
            return None

    def __findDataForDates(self,online=False):
        if not(self.status):
            return None
        pathList = []
        multi_path=self.path.split(',')
        for single_path in multi_path:
            dirList=[]
            for thisPath in os.listdir(single_path):
                if not os.path.isdir(os.path.join(single_path,thisPath)):
                    continue
                if not isDoyFolder(thisPath):
                    continue

                dirList.append(thisPath)

            if not(dirList):
                return None, None

            thisDate=self.startDate

            while(thisDate <= self.endDate):
                    year = thisDate.timetuple().tm_year
                    doy = thisDate.timetuple().tm_yday

                    matchlist = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy) + '*')
                    if len(matchlist) == 0:
                        thisDate += datetime.timedelta(1)
                        continue
                    for match in matchlist:
                        pathList.append(os.path.join(single_path,match))

                    thisDate += datetime.timedelta(1)

        if pathList == []:
            print "Any folder was found for the date range: %s-%s" %(self.startDate, self.endDate)
            return None, None

        print "%d folder(s) was(were) found for the date range: %s - %s" %(len(pathList), self.startDate, self.endDate)
        filenameList = []
        datetimeList = []
        pathDict = {}
        filenameList_to_sort = []

        flag=False
        if self.frequency<3:
            add_folder='sp'+str(self.code)+'1_f0'
            flag=True
        if self.frequency>=3:
            add_folder='sp'+str(self.code)+'1_f1'
            flag=True

        if flag==False:
            print "Please write 2.72 or 3.64"
            return 0

        for i in range(len(pathList)):
            pathList[i] = pathList[i]+"/"+add_folder

        for i in range(len(pathList)):
            thisPath = pathList[i]
            fileList = glob.glob1(thisPath, "*%s" %self.ext)
            fileList.sort()
            pathDict.setdefault(fileList[0])
            pathDict[fileList[0]] = i
            filenameList_to_sort.append(fileList[0])

        filenameList_to_sort.sort()

        for file in filenameList_to_sort:
            thisPath = pathList[pathDict[file]]
            fileList = glob.glob1(thisPath, "*%s" %self.ext)
            fileList.sort()
            ##################### NEW - PART - OFF LINE ##############
            last_filename=os.path.join(thisPath,fileList[-1])
            self.sizeofHF_File=os.path.getsize(last_filename)
            ##################################################
            for file in fileList:

                filename = os.path.join(thisPath,file)
                sizeoffile= verifyFile(filename,size=self.sizeofHF_File)#9650368 en 600
                if not (sizeoffile):
                    continue

                thisDatetime = isFileinThisTime(filename, self.startDate,self.endDate,self.startTime, self.endTime,self.timezone)

                if not(thisDatetime):
                    continue

                filenameList.append(filename)
                datetimeList.append(thisDatetime)

        if not(filenameList):
            print "Any file was found for the time range %s - %s" %(self.startTime, self.endTime)
            return None, None

        print "%d file(s) was(were) found for the time range: %s - %s" %(len(filenameList), self.startTime, self.endTime)
        print

        for i in range(len(filenameList)):
            print "%s -> [%s]" %(filenameList[i], datetimeList[i].ctime())

        self.filenameList = filenameList
        self.datetimeList = datetimeList

        return pathList, filenameList


    def __getTimeFromData(self):
        startDateTime_Reader = datetime.datetime.combine(self.startDate,self.startTime)
        endDateTime_Reader = datetime.datetime.combine(self.endDate,self.endTime)
        print 'Filtering Files from %s to %s'%(startDateTime_Reader, endDateTime_Reader)
        print '........................................'
        filter_filenameList=[]
        self.filenameList.sort()
        for i in range(len(self.filenameList)-1):
            filename=self.filenameList[i]
            dir_hf_filename= filename
            fp= h5py.File(dir_hf_filename,'r')
            hipoc=fp['t'].value
            hipoc=hipoc+self.timezone
            date_time=datetime.datetime.utcfromtimestamp(hipoc)
            fp.close()
            this_time=date_time
            if (this_time>=startDateTime_Reader and this_time <= endDateTime_Reader):
                filter_filenameList.append(filename)
        filter_filenameList.sort()
        self.filenameList = filter_filenameList
        return 1

    def __getFilenameList(self):

        dirList = [os.path.join(self.path,x) for x in self.dirnameList]
        self.filenameList= dirList

    def __selectDataForTimes(self, online=False):

        if not(self.status):
            return None
        #----------------
        self.__getFilenameList()
        #----------------
        if not(online): #offline
            if not(self.all):
                self.__getTimeFromData()
            if len(self.filenameList)>0:
                self.status=1
                self.filenameList.sort()
            else:
                self.status=0
                return None
        else:

            if self.campaign == 1:
                value_set=6
            else:
                if self.__inc_int==0:
                    value_set=1
                else:
                    value_set=self.__inc_int

            if self.set != None:
                filename=getFileFromSet(self.path,self.ext,self.set)
                if self.flag_nextfile==True:
                    self.dirnameList=[filename]
                    fullfilename=self.path+"/"+filename
                    self.filenameList=[fullfilename]
                    self.filename_next_set=int(filename[7:17])+10*value_set
                    self.flag_nextfile=False
                else:
                    if filename == None:
                        raise ValueError, "corregir"

                    self.dirnameList=[filename]
                    fullfilename=self.path+"/"+filename
                    self.filenameList=[fullfilename]
                    self.filename_next_set=int(filename[7:17])+10*value_set
                    print "Setting next file: ",self.filename_next_set
                    self.set=int(filename[7:17])
                    if True:
                        pass
                    else:
                        print "No existe el siguiente archivo"

            else:
                filename =getlastFileFromPath(self.path,self.ext)

                if self.flag_nextfile==True:
                    self.dirnameList=[filename]
                    fullfilename=self.path+"/"+filename
                    self.filenameList=[self.filenameList[-1]]
                    self.filename_next_set=int(filename[7:17])+10*value_set

                    self.flag_nextfile=False
                else:
                   filename=getFileFromSet(self.path,self.ext,self.set)
                   print filename,"Primera condicion"

                   if filename == None:
                       raise ValueError, "corregir"

                   self.dirnameList=[filename]
                   fullfilename=self.path+"/"+filename
                   self.filenameList=[fullfilename]
                   self.filename_next_set=int(filename[7:17])+10*value_set
                   print "Setting next file",self.filename_next_set
                   self.set=int(filename[7:17])
                   if True:
                       pass
                   else:
                       print "No existe el siguiente archivo"



    def __searchFilesOffline(self,
                            path,
                            frequency,
                            startDate,
                            endDate,
                            ext,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            walk=True):

        self.__setParameters(path,frequency,startDate, endDate, startTime, endTime, walk)
        self.__checkPath()
        pathList,filenameList=self.__findDataForDates()
        return

    def __searchFilesOnline(self,
                            path,
                            frequency,
                            startDate,
                            endDate,
                            ext,
                            walk,
                            set):

        startDate = datetime.datetime.utcnow().date()
        endDate = datetime.datetime.utcnow().date()

        self.__setParameters(path,frequency,startDate,endDate,walk)

        self.__checkPath()
        if not walk:
            fullpath=path
        else:
            multi_path=self.path.split(',')
            for single_path in multi_path:
                dirList=[]
                for thisPath in os.listdir(single_path):
                    if not os.path.isdir(os.path.join(single_path,thisPath)):
                        continue
                    if not isDoyFolder(thisPath):
                        continue

                    dirList.append(thisPath)
                    dirList.sort()

                if not(dirList):
                    return None, None,None

            tmp = dirList[-1]
            flag=False
            #print self.frequency,"HOLA AMIGO QUE TAL"
            if self.frequency<3:
                add_folder='sp'+str(self.code)+'1_f0'
                flag=True
            if self.frequency>=3:
                add_folder='sp'+str(self.code)+'1_f1'
                flag=True
            if flag==False:
                print "Please write 2.72 or 3.64"
                return 0

            fullpath = path+"/"+tmp+"/"+add_folder
            self.path= fullpath

        print "%s folder was found: " %(fullpath )
        #print "5ER PRINT",set
        if set == None:
            self.set=None
            filename =getlastFileFromPath(fullpath,ext)
            startDate= datetime.datetime.utcnow().date
            endDate= datetime.datetime.utcnow().date()

        else:
            filename= getFileFromSet(fullpath,ext,set)
            startDate=None
            endDate=None

        if not (filename):
            return None,None,None,None,None

        filenameList= fullpath+"/"+filename
        ############### ON LINE##################
        self.sizeofHF_File = os.path.getsize(filenameList)
        ########################################
        self.dirnameList=[filename]
        self.filenameList=[filenameList]
        self.flag_nextfile=True
        return

    def __setNextFile(self,online=False):
        """
        """
        if not(online):
            newFile = self.__setNextFileOffline()
        else:
            newFile = self.__setNextFileOnline()

        if not(newFile):
            return 0
        return 1

    def __setNextFileOffline(self):
        """
        """
        idFile= self.fileIndex
        while(True): #TODO 2018, xq dentro de un while?
            idFile += 1
            if not (idFile < len(self.filenameList)):
                self.flagNoMoreFiles = 1
                print "No more Files"
                return 0

            filename = self.filenameList[idFile]
            hfFilePointer =h5py.File(filename,'r')
            epoc=hfFilePointer['t'].value
            name_prof='pw0_C'+str(self.code)
            self.nProfiles= len((hfFilePointer[name_prof]))
            break

        self.flagIsNewFile = 1
        self.fileIndex = idFile
        self.filename = filename

        self.hfFilePointer = hfFilePointer
        hfFilePointer.close()
        self.__t0=epoc
        print "Setting the file: %s"%self.filename

        return 1

    def __setNextFileOnline(self):
        """
        """
        #print "SOY NONE",self.set
        if self.set==None:
            pass
        else:
            self.set +=60

        filename = self.filenameList[0]#fullfilename
        a=0
        if self.filename_online != None:
                self.__selectDataForTimes(online=True)
                filename = self.filenameList[0]
                while self.filename_online == filename:
                    print 'waiting %d seconds to get a new file...'%(self.__waitForNewFile)
                    time.sleep(self.__waitForNewFile)
                    #self.__findDataForDates(online=True)
                    self.set=self.filename_next_set
                    self.__selectDataForTimes(online=True)
                    filename = self.filenameList[0]
                    sizeoffile=os.path.getsize(filename)
                    a+=1
                    if a==10:
                        break
        if a==10:
            self.flagNoMoreFiles= True

        #print "filename",filename
        sizeoffile=os.path.getsize(filename)
        #print "sizeoffile",sizeoffile
        if sizeoffile<self.sizeofHF_File:#1650368:#1622336
            print "%s is not the rigth  size"%filename
            delay=90
            print 'waiting %d seconds for delay...'%(delay)
            time.sleep(delay)

        try:
            fp= h5py.File(filename,'r')
        except IOError:
            traceback.print_exc()
            raise IOError, "The file %s can't be opened" %(filename)

        self.filename_online=filename
        epoc=fp['t'].value
        ############ ON LINE #################
        name_prof='pw0_C'+str(self.code)
        self.nProfiles= len((fp[name_prof]))
        #self.nProfiles= len((fp['pw0_C0']))
        #######################################
        self.hfFilePointer=fp
        fp.close()
        self.__t0=epoc

        self.flagIsNewFile = 1
        self.filename = filename

        print "Setting the file: %s"%self.filename
        return 1

    def __getExpParameters(self):
        if not(self.status):
            return None

    def setup(self,
               path = None,
               frequency=None,
               campaign = None,
               inc_int=None,
               startDate = None,
               code = 0,
               endDate = None,
               startTime = datetime.time(0,0,0),
               endTime = datetime.time(23,59,59),
               set = None,
               expLabel = "",
               ext = None,
               all=0,
               timezone=0,
               online = False,
               delay = 60,
               walk = True):
        '''
        In this method we should set all initial parameters.

        '''
        if path==None:
            raise ValueError,"The path is not valid"

        if frequency==None:
            raise ValueError,"The frequency is not valid"

        if campaign == None:
            raise ValueError,"The Campaign is not valid"

        if inc_int== None:
            raise ValueError, "The number of incoherent integration is not defined"

        if ext==None:
            ext = self.ext

        self.code=code
        self.frequency= frequency
        self.campaign = campaign

        try:
            self.__inc_int= int(inc_int)
        except:
            print "The number of incoherent integration should be an integer"
        if self.__inc_int>6:
            raise ValueError, "The number of incoherent integration should be between 0 and 6"

        self.timezone= timezone
        self.online= online
        self.all=all

        if not(online):
            print "Searching files in offline mode..."

            self.__searchFilesOffline(path,frequency,startDate, endDate, ext, startTime, endTime, walk)
        else:
            print "Searching files in online mode..."
            self.__searchFilesOnline(path,frequency,startDate,endDate,ext,walk,set)
            if set==None:
                pass
            else:
                self.set=set-10

        if not(self.filenameList):
            print "There  is no files into the folder: %s"%(path)
            sys.exit(-1)

        self.__getExpParameters()


        self.fileIndex = -1

        self.__setNextFile(online)

        self.__readMetadata()

        self.__setLocalVariables()

        self.__setHeaderDO()
        #self.profileIndex_offset= 0

        #self.profileIndex = self.profileIndex_offset
        self.isConfig = True

    def __readMetadata(self):
        self.__readHeader()

    def __setLocalVariables(self):

        self.datablock = numpy.zeros((self.nChannels, self.nHeights,self.nProfiles), dtype = numpy.complex)
        self.datacspec = numpy.zeros(( self.nHeights,self.nProfiles), dtype = numpy.complex)
        self.dataImage  = numpy.zeros((self.nHeights,3,self.nChannels), dtype = numpy.float) #RGBdata
        self.profileIndex = 9999

    def __setHeaderDO(self):

        self.dataOut.radarControllerHeaderObj = RadarControllerHeader()
        self.dataOut.systemHeaderObj = SystemHeader()
        #---------------------------------------------------------
        self.dataOut.systemHeaderObj.nProfiles=100
        self.dataOut.systemHeaderObj.nSamples=1000

        SAMPLING_STRUCTURE=[('h0', '<f4'), ('dh', '<f4'), ('nsa', '<u4')]
        self.dataOut.radarControllerHeaderObj.samplingWindow=numpy.zeros((1,),SAMPLING_STRUCTURE)
        self.dataOut.radarControllerHeaderObj.samplingWindow['h0']=0
        self.dataOut.radarControllerHeaderObj.samplingWindow['dh']=1.5
        self.dataOut.radarControllerHeaderObj.samplingWindow['nsa']=1000
        self.dataOut.radarControllerHeaderObj.nHeights=int(self.dataOut.radarControllerHeaderObj.samplingWindow['nsa'])
        self.dataOut.radarControllerHeaderObj.firstHeight = self.dataOut.radarControllerHeaderObj.samplingWindow['h0']
        self.dataOut.radarControllerHeaderObj.deltaHeight = self.dataOut.radarControllerHeaderObj.samplingWindow['dh']
        self.dataOut.radarControllerHeaderObj.samplesWin = self.dataOut.radarControllerHeaderObj.samplingWindow['nsa']

        self.dataOut.radarControllerHeaderObj.nWindows=1
        self.dataOut.radarControllerHeaderObj.codetype=0
        self.dataOut.radarControllerHeaderObj.numTaus=0
        #self.dataOut.radarControllerHeaderObj.Taus = numpy.zeros((1,),'<f4')
        #self.dataOut.radarControllerHeaderObj.nCode=numpy.zeros((1,), '<u4')
        #self.dataOut.radarControllerHeaderObj.nBaud=numpy.zeros((1,), '<u4')
        #self.dataOut.radarControllerHeaderObj.code=numpy.zeros(0)

        self.dataOut.radarControllerHeaderObj.code_size=0
        self.dataOut.nBaud=0
        self.dataOut.nCode=0
        self.dataOut.nPairs=0
        #nuevo
        self.dataOut.radarControllerHeaderObj.expType=2
        self.dataOut.radarControllerHeaderObj.nTx=1
        self.dataOut.radarControllerHeaderObj.txA=0
        self.dataOut.radarControllerHeaderObj.txB=0
        #---------------------------------------------------------

        self.dataOut.type = "Voltage"

        self.dataOut.data = None

        self.dataOut.dtype = numpy.dtype([('real','<f4'),('imag','<f4')])

        self.dataOut.nProfiles = 1

        self.dataOut.heightList = self.__firstHeigth + numpy.arange(self.__nSamples, dtype = numpy.float)*self.__deltaHeigth

        self.dataOut.channelList = range(self.nChannels)

        #self.dataOut.channelIndexList = None

        self.dataOut.flagNoData = True

        #Set to TRUE if the data is discontinuous
        self.dataOut.flagDiscontinuousBlock = False

        self.dataOut.utctime = None

        self.dataOut.useLocalTime=True

        self.dataOut.timeZone = -self.timezone# original en -self.timezone/60

        self.dataOut.dstFlag = 0

        self.dataOut.errorCount = 0

        self.dataOut.nCohInt = 1 #6(60seg) o 1(10seg)

        self.dataOut.blocksize = self.dataOut.getNChannels() * self.dataOut.getNHeights()

        self.dataOut.flagDecodeData = False #asumo que la data esta decodificada

        self.dataOut.flagDeflipData = False #asumo que la data esta sin flip

        self.dataOut.flagShiftFFT = False

        self.dataOut.ippSeconds = 1.0*self.__nSamples/self.__sample_rate*10  ######

        self.dataOut.ippSeconds= 0.1

        #Time interval between profiles
        #self.dataOut.timeInterval =self.dataOut.ippSeconds * self.dataOut.nCohInt


        self.dataOut.frequency = self.__frequency

        self.dataOut.nIncohInt = self.__inc_int

        #print "QUE INTERESANTE",self.dataOut.nIncohInt,self.__inc_int

        self.dataOut.realtime = self.__online

        self.dataOut.last_block = len(self.filenameList)

    def __hasNotDataInBuffer(self):

        if self.profileIndex >= self.nProfiles:
            return 1

        return 0

    def readNextBlock(self):
        if not(self.__setNewBlock()):
            return 0

        if not(self.readBlock()):
            return 0

        return 1

    def __setNewBlock(self):

        if self.hfFilePointer==None:
            return 0

        if self.flagIsNewFile:
            return 1

        if self.profileIndex < self.nProfiles:
            return 1

        self.__setNextFile(self.online)

        return 1

    def readBlock(self):
        try:
            fp=h5py.File(self.filename,'r')
        except:
            print "Error reading file %s"%self.filename

        #TODO 2018: Si ya hay un try arriba, porque hay un for abajo?

        for i in range(4): #TODO 2018 , no deberia ir hasta 4 si esta en offline mode
            sizeoffile=os.path.getsize(self.filename) #TODO: what happend when is in online mode?
            #TODO 2018 > esto va ha fallar cuando sea online, xq el peso siempre sera igual al peso del archivo en ese instante.
            if sizeoffile<self.sizeofHF_File:#1650368:#1622336
                delay=80#WTFP?
                print 'sizeofile less than 9650368'
                print 'waiting %d  more seconds for delay...'%(delay)
                time.sleep(delay)
                fp=h5py.File(self.filename,'r')

        #Puntero que apunta al archivo hdf5
	if self.code==None:
	 	self.code=0
        name0='pw0_C'+str(self.code)
        name1='pw1_C'+str(self.code)
        name2='cspec01_C'+str(self.code)
        #name3='image0_C'+str(self.code)
        #name4='image1_C'+str(self.code)
        name3='image0_c'+str(self.code)
        name4='image1_c'+str(self.code)

        ch0=(fp[name0]).value    #Primer canal (100,1000)--(perfiles,alturas)
        ch1=(fp[name1]).value    #Segundo canal (100,1000)--(perfiles,alturas)
        cspc=(fp[name2]).value   #cross spectra data from ch0 and ch1
        ch0_image = (fp[name3]).value #Image information to make RGB
        ch1_image = (fp[name4]).value #Image information to make RGB
        fp.close()

        ch0= ch0.swapaxes(0,1)   #Primer canal (100,1000)--(alturas,perfiles)
        ch1= ch1.swapaxes(0,1)   #Segundo canal (100,1000)--(alturas,perfiles)
        self.datablock = numpy.array([ch0,ch1])
        self.datacspec = numpy.array([cspc])
        self.dataImage = numpy.array([ch0_image,ch1_image])
        self.flagIsNewFile=0

        self.profileIndex=0

        return 1

    def getData(self):
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            print 'Process finished'
            return 0

        if self.__hasNotDataInBuffer():
            if not(self.readNextBlock()):
                self.dataOut.flagNodata=True
                return 0

        ##############################
        ##############################
        self.dataOut.data = self.datablock[:,:,self.profileIndex]
        self.dataOut.data_cspec = self.datacspec[:,self.profileIndex]
        self.dataOut.utctime = self.__t0 + self.dataOut.ippSeconds*self.profileIndex
        self.dataOut.Image = self.dataImage
        self.dataOut.profileIndex= self.profileIndex
        self.dataOut.flagNoData=False
        self.profileIndex +=1

        return self.dataOut.data


    def run(self, **kwargs):
        '''
        This method will be called many times so here you should put all your code
        '''

        if not self.isConfig:
            self.setup(**kwargs)
            self.isConfig = True
        self.getData()


class HFParamReader(HFReader):
    '''
    20/12/18 : Esta clase se genera para poder plotear de los datos reducidos.
    Reads HDF5 compress format files.
    inputparameters :  path
    startDate
    endDate
    startTime
    endTime
    '''
    ext = ".hdf5"
    optchar = "D"
    timezone = None
    startTime = None
    endTime = None
    fileIndex = None
    utcList = None      #To select data in the utctime list
    blockList = None    #List to blocks to be read from the file
    blocksPerFile = None    #Number of blocks to be read
    blockIndex = None
    path = None
    filenameList = None
    datetimeList = None
    listMetaname = None
    listMeta = None
    listDataname = None
    listData = None
    listShapes = None
    fp = None
    dataOut = None
    isConfig = False
    def __init__(self):
        '''
        Constructor
        '''
        ProcessingUnit.__init__(self)
        self.isConfig =False
        self.datablock = None
        self.dataImage = None
        self.filename_current=None
        self.utc = 0
        self.ext='.hdf5'
        self.flagIsNewFile = 1
        self.fileIndex=None
        self.profileIndex_offset=None
        self.filenameList=[]
        self.hfFilePointer= None
        self.filename_online = None
        self.status=True
        self.flagNoMoreFiles= False
        self.__waitForNewFile = 45
        self.__inc_int = 0
        self.sizeofHF_File= None
        self.campaign = 1
        self.dataOut = self.dataIn#Parameters() # En este caso parameters hereda de JROData

    def setup(self,
               path = None,
               frequency=None,
               campaign = None,
               inc_int=None,
               startDate = None,
               code = 0,
               endDate = None,
               startTime = datetime.time(0,0,0),
               endTime = datetime.time(23,59,59),
               set = None,
               expLabel = "",
               ext = None,
               all=0,
               timezone=0,
               online = False,
               delay = 60,
               walk = True):
        '''
        In this method we should set all initial parameters.

        '''
        if path==None:
            raise ValueError,"The path is not valid"

        if frequency==None:
            raise ValueError,"The frequency is not valid"

        if campaign == None:
            raise ValueError,"The Campaign is not valid"

        if inc_int== None:
            raise ValueError, "The number of incoherent integration is not defined"

        if ext==None:
            ext = self.ext

        self.code=code
        self.frequency= frequency
        self.campaign = campaign

        try:
            self.__inc_int= int(inc_int)
        except:
            print "The number of incoherent integration should be an integer"
        if self.__inc_int>6:
            raise ValueError, "The number of incoherent integration should be between 0 and 6"

        self.timezone= timezone
        self.online= online
        self.all=all

        if not(online):
            print "Searching files in offline mode..."
            self.__searchFilesOffline(path,frequency,startDate, endDate, ext, startTime, endTime, walk)
        else: #Solo voy a dejar la base para que se haga de modo online...
            print "Searching files in online mode..."
            self.__searchFilesOnline(path,frequency,startDate,endDate,ext,walk,set)
            if set==None:
                pass
            else:
                self.set=set-10

        if not(self.filenameList):
            print "There  is no files into the folder: %s"%(path)
            sys.exit(-1)

        self.__getExpParameters()
        self.fileIndex = -1

        self.__readMetadata()

        self.__setNextFile(online)

        #self.__setLocalVariables()
        #self.__setHeaderDO()
        self.isConfig = True


    def __getExpParameters(self):
        if not(self.status):
            return None

    def __readMetadata(self):
        '''
        Reads Metadata
        self.pathMeta
        self.listShapes
        self.listMetaname
        self.listMeta
        '''
        filename = self.filenameList[0]

        fp = h5py.File(filename,'r')

        gp = fp['Metadata']

        listMetaname = []
        listMetadata = []
        for item in list(gp.items()):
            name = item[0]

            if name=='array dimensions':
                table = gp[name][:]
                listShapes = {}
                for shapes in table:
                    listShapes[shapes[0]] = numpy.array([shapes[1],shapes[2],shapes[3],shapes[4],shapes[5]])
            else:
                data = gp[name].value
                listMetaname.append(name)
                listMetadata.append(data)

        self.listShapes = listShapes
        self.listMetaname = listMetaname
        self.listMeta = listMetadata

        fp.close()
        return

    def __setNextFile(self,online=False):
        """
        """
        if not(online):
            newFile = self.__setNextFileOffline()
        else:
            newFile = self.__setNextFileOnline()

        if not(newFile):
            return 0
        return 1

    def __searchFilesOffline(self,
                            path,
                            frequency,
                            startDate,
                            endDate,
                            ext,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            walk=True):

        self.__setParameters(path,frequency,startDate, endDate, startTime, endTime, walk)
        self.__checkPath()
        pathList,filenameList=self.__findDataForDates()
        return

    def __searchFilesOffline(self,
                            path,
                            frequency,
                            startDate,
                            endDate,
                            ext,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            walk=True):

        self.__setParameters(path,frequency,startDate, endDate, startTime, endTime, walk)
        self.__checkPath()
        pathList,filenameList=self.__findDataForDates()
        return

    def __setNextFileOffline(self): # TODO Arreglar par alos nuevos tipos de archivos comprimidos
        """
        """
        idFile= self.fileIndex
        while(True): #TODO 2018, xq dentro de un while?
            idFile += 1
            if not (idFile < len(self.filenameList)):
                self.flagNoMoreFiles = 1
                print "No more Files"
                return 0

            filename = self.filenameList[idFile]
            hfFilePointer =h5py.File(filename,'r')
            epoc=hfFilePointer['t'].value
            name_prof='pw0_C'+str(self.code)
            self.nProfiles= len((hfFilePointer[name_prof]))
            break

        self.flagIsNewFile = 1
        self.fileIndex = idFile
        self.filename = filename

        self.hfFilePointer = hfFilePointer
        hfFilePointer.close()
        self.__t0=epoc
        print "Setting the file: %s"%self.filename

        return 1

    def __setNextFileOnline(self):
        """
        """
        #print "SOY NONE",self.set
        if self.set==None:
            pass
        else:
            self.set +=60

        filename = self.filenameList[0]#fullfilename
        a=0
        if self.filename_online != None:
                self.__selectDataForTimes(online=True)
                filename = self.filenameList[0]
                while self.filename_online == filename:
                    print 'waiting %d seconds to get a new file...'%(self.__waitForNewFile)
                    time.sleep(self.__waitForNewFile)
                    #self.__findDataForDates(online=True)
                    self.set=self.filename_next_set
                    self.__selectDataForTimes(online=True)
                    filename = self.filenameList[0]
                    sizeoffile=os.path.getsize(filename)
                    a+=1
                    if a==10:
                        break
        if a==10:
            self.flagNoMoreFiles= True

        #print "filename",filename
        sizeoffile=os.path.getsize(filename)
        #print "sizeoffile",sizeoffile
        if sizeoffile<self.sizeofHF_File:#1650368:#1622336
            print "%s is not the rigth  size"%filename
            delay=90
            print 'waiting %d seconds for delay...'%(delay)
            time.sleep(delay)

        try:
            fp= h5py.File(filename,'r')
        except IOError:
            traceback.print_exc()
            raise IOError, "The file %s can't be opened" %(filename)

        self.filename_online=filename
        epoc=fp['t'].value
        ############ ON LINE #################
        name_prof='pw0_C'+str(self.code)
        self.nProfiles= len((fp[name_prof]))
        #self.nProfiles= len((fp['pw0_C0']))
        #######################################
        self.hfFilePointer=fp
        fp.close()
        self.__t0=epoc

        self.flagIsNewFile = 1
        self.filename = filename

        print "Setting the file: %s"%self.filename
        return 1

    def run(self, **kwargs):
        '''
        This method will be called many times so here you should put all your code
        '''
        if not self.isConfig:
            self.setup(**kwargs)
            self.isConfig = True
        self.getData()
