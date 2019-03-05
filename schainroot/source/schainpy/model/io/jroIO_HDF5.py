import numpy
import time
import os
import h5py
import re

from model.data.jrodata import *
from model.proc.jroproc_base import ProcessingUnit, Operation
from model.io.jroIO_base import *


class HDF5Reader(ProcessingUnit):

    ext = ".hdf5"

    optchar = "D"

    timezone = None

    secStart = None

    secEnd = None

    fileIndex = None

    blockIndex = None

    blocksPerFile = None

    path = None

    #List of Files

    filenameList = None

    datetimeList = None

    #Hdf5 File

    fpMetadata = None

    pathMeta = None

    listMetaname = None

    listMeta = None

    listDataname = None

    listData = None

    listShapes = None

    fp = None

    #dataOut reconstruction

    dataOut = None

    nRecords = None


    def __init__(self):
        self.dataOut = self.__createObjByDefault()
        return

    def __createObjByDefault(self):

        dataObj = Parameters()

        return dataObj

    def setup(self,path=None,
                    startDate=None,
                    endDate=None,
                    startTime=datetime.time(0,0,0),
                    endTime=datetime.time(23,59,59),
                    walk=True,
                    timezone='ut',
                    all=0,
                    online=False,
                    ext=None):

        if ext==None:
            ext = self.ext
        self.timezone = timezone
#         self.all = all
#         self.online = online
        self.path = path

        startDateTime = datetime.datetime.combine(startDate,startTime)
        endDateTime = datetime.datetime.combine(endDate,endTime)
        secStart = (startDateTime-datetime.datetime(1970,1,1)).total_seconds()
        secEnd = (endDateTime-datetime.datetime(1970,1,1)).total_seconds()

        self.secStart = secStart
        self.secEnd = secEnd

        if not(online):
            #Busqueda de archivos offline
            self.__searchFilesOffline(path, startDate, endDate, ext, startTime, endTime, secStart, secEnd, walk)
        else:
            self.__searchFilesOnline(path, walk)

        if not(self.filenameList):
            print "There is no files into the folder: %s"%(path)
            sys.exit(-1)

#         self.__getExpParameters()

        self.fileIndex = -1

        self.__setNextFileOffline()

        self.__readMetadata()

        self.blockIndex = 0

        return

    def __searchFilesOffline(self,
                            path,
                            startDate,
                            endDate,
                            ext,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            secStart = 0,
                            secEnd = numpy.inf,
                            walk=True):

#         self.__setParameters(path, startDate, endDate, startTime, endTime, walk)
#
#         self.__checkPath()
#
#         self.__findDataForDates()
#
#         self.__selectDataForTimes()
#
#         for i in range(len(self.filenameList)):
#             print "%s" %(self.filenameList[i])

        pathList = []

        if not walk:
            #pathList.append(path)
            multi_path = path.split(',')
            for single_path in multi_path:
                pathList.append(single_path)

        else:
            #dirList = []
            multi_path = path.split(',')
            for single_path in multi_path:
                dirList = []
                for thisPath in os.listdir(single_path):
                    if not os.path.isdir(os.path.join(single_path,thisPath)):
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
                        pathList.append(os.path.join(single_path,match))

                    thisDate += datetime.timedelta(1)

        if pathList == []:
            print "Any folder was found for the date range: %s-%s" %(startDate, endDate)
            return None, None

        print "%d folder(s) was(were) found for the date range: %s - %s" %(len(pathList), startDate, endDate)

        filenameList = []
        datetimeList = []
        pathDict = {}
        filenameList_to_sort = []

        for i in range(len(pathList)):

            thisPath = pathList[i]

            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()
            pathDict.setdefault(fileList[0])
            pathDict[fileList[0]] = i
            filenameList_to_sort.append(fileList[0])

        filenameList_to_sort.sort()

        for file in filenameList_to_sort:
            thisPath = pathList[pathDict[file]]

            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()

            for file in fileList:

                filename = os.path.join(thisPath,file)
                thisDatetime = self.__isFileinThisTime(filename, secStart, secEnd)

                if not(thisDatetime):
                    continue

                filenameList.append(filename)
                datetimeList.append(thisDatetime)

        if not(filenameList):
            print "Any file was found for the time range %s - %s" %(startTime, endTime)
            return None, None

        print "%d file(s) was(were) found for the time range: %s - %s" %(len(filenameList), startTime, endTime)
        for i in range(len(filenameList)):
            print "%s -> [%s]" %(filenameList[i], datetimeList[i].ctime())

        self.filenameList = filenameList
        self.datetimeList = datetimeList

        return pathList, filenameList

    def __isFileinThisTime(self, filename, startSeconds, endSeconds):
        """
        Retorna 1 si el archivo de datos se encuentra dentro del rango de horas especificado.

        Inputs:
            filename            :    nombre completo del archivo de datos en formato Jicamarca (.r)

            startTime          :    tiempo inicial del rango seleccionado en formato datetime.time

            endTime            :    tiempo final del rango seleccionado en formato datetime.time

        Return:
            Boolean    :    Retorna True si el archivo de datos contiene datos en el rango de
                            fecha especificado, de lo contrario retorna False.

        Excepciones:
            Si el archivo no existe o no puede ser abierto
            Si la cabecera no puede ser leida.

        """

        try:
            fp = fp = h5py.File(filename,'r')
        except IOError:
            traceback.print_exc()
            raise IOError, "The file %s can't be opened" %(filename)

        grp = fp['Data']
        timeAux = grp['time']
        time0 = timeAux[:][0].astype(numpy.float)   #Time Vector

        fp.close()

        if self.timezone == 'lt':
            time0 -= 5*3600

        boolTimer = numpy.logical_and(time0 >= startSeconds,time0 < endSeconds)

        if not (numpy.any(boolTimer)):
            return None

        thisDatetime = datetime.datetime.utcfromtimestamp(time0[0])
        return thisDatetime

    def __checkPath(self):
        if os.path.exists(self.path):
            self.status = 1
        else:
            self.status = 0
            print 'Path:%s does not exists'%self.path

        return

    def __setNextFileOffline(self):
        idFile = self.fileIndex
        idFile += 1

        if not(idFile < len(self.filenameList)):
            print "No more Files"
            return 0

        filename = self.filenameList[idFile]

        filePointer = h5py.File(filename,'r')

        self.flagIsNewFile = 1
        self.fileIndex = idFile
        self.filename = filename

        self.fp = filePointer

        print "Setting the file: %s"%self.filename

        self.__readMetadata()
        self.__setBlockList()
#         self.nRecords = self.fp['Data'].attrs['blocksPerFile']
        self.nRecords = self.fp['Data'].attrs['nRecords']
        self.blockIndex = 0
        return 1

    def __setBlockList(self):
        '''
        self.fp
        self.startDateTime
        self.endDateTime

        self.blockList
        self.blocksPerFile

        '''
        filePointer = self.fp
        secStart = self.secStart
        secEnd = self.secEnd

        grp = filePointer['Data']
        timeVector = grp['time'].value.astype(numpy.float)[0]

        if self.timezone == 'lt':
            timeVector -= 5*3600

        ind = numpy.where(numpy.logical_and(timeVector >= secStart , timeVector < secEnd))[0]

        self.blockList = ind
        self.blocksPerFile = len(ind)

        return

    def __readMetadata(self):
        '''
        self.pathMeta

        self.listShapes
        self.listMetaname
        self.listMeta

        '''

        grp = self.fp['Data']
        pathMeta = os.path.join(self.path, grp.attrs['metadata'])

        if pathMeta == self.pathMeta:
            return
        else:
            self.pathMeta = pathMeta

        filePointer = h5py.File(self.pathMeta,'r')
        groupPointer = filePointer['Metadata']

        listMetaname = []
        listMetadata = []
        for item in groupPointer.items():
            name = item[0]

            if name=='array dimensions':
                table = groupPointer[name][:]
                listShapes = {}
                for shapes in table:
                    listShapes[shapes[0]] = numpy.array([shapes[1],shapes[2],shapes[3],shapes[4]])
            else:
                data = groupPointer[name].value
                listMetaname.append(name)
                listMetadata.append(data)

                if name=='type':
                    self.__initDataOut(data)

        filePointer.close()

        self.listShapes = listShapes
        self.listMetaname = listMetaname
        self.listMeta = listMetadata

        return

    def __readData(self):
        grp = self.fp['Data']
        listdataname = []
        listdata = []

        for item in grp.items():
            name = item[0]

            if name == 'time':
                listdataname.append('utctime')
                timeAux = grp[name].value.astype(numpy.float)[0]
                listdata.append(timeAux)
                continue

            listdataname.append(name)
            array = self.__setDataArray(self.nRecords, grp[name],self.listShapes[name])
            listdata.append(array)

        self.listDataname = listdataname
        self.listData = listdata
        return

    def __setDataArray(self, nRecords, dataset, shapes):

        nChannels = shapes[0]    #Dimension 0

        nPoints = shapes[1]      #Dimension 1, number of Points or Parameters

        nSamples = shapes[2]     #Dimension 2, number of samples or ranges

        mode = shapes[3]

#         if nPoints>1:
#             arrayData = numpy.zeros((nRecords,nChannels,nPoints,nSamples))
#         else:
#             arrayData = numpy.zeros((nRecords,nChannels,nSamples))
#
#         chn = 'channel'
#
#         for i in range(nChannels):
#
#             data = dataset[chn + str(i)].value
#
#             if nPoints>1:
#                 data = numpy.rollaxis(data,2)
#
#             arrayData[:,i,:] = data

        arrayData = numpy.zeros((nRecords,nChannels,nPoints,nSamples))
        doSqueeze = False
        if mode == 0:
            strds = 'channel'
            nDatas = nChannels
            newShapes = (nRecords,nPoints,nSamples)
            if nPoints == 1:
                doSqueeze = True
                axisSqueeze = 2
        else:
            strds = 'param'
            nDatas = nPoints
            newShapes = (nRecords,nChannels,nSamples)
            if nChannels == 1:
                doSqueeze = True
                axisSqueeze = 1

        for i in range(nDatas):

            data = dataset[strds + str(i)].value
            data = data.reshape(newShapes)

            if mode == 0:
                arrayData[:,i,:,:] = data
            else:
                arrayData[:,:,i,:] = data

        if doSqueeze:
                arrayData = numpy.squeeze(arrayData, axis=axisSqueeze)

        return arrayData

    def __initDataOut(self, type):

#         if type =='Parameters':
#             self.dataOut = Parameters()
#         elif type =='Spectra':
#             self.dataOut = Spectra()
#         elif type =='Voltage':
#             self.dataOut = Voltage()
#         elif type =='Correlation':
#             self.dataOut = Correlation()

        return

    def __setDataOut(self):
        listMeta = self.listMeta
        listMetaname = self.listMetaname
        listDataname = self.listDataname
        listData = self.listData

        blockIndex = self.blockIndex
        blockList = self.blockList

        for i in range(len(listMeta)):
            setattr(self.dataOut,listMetaname[i],listMeta[i])
        raw_input(listData)
        for j in range(len(listData)):
            if listDataname[j]=='utctime':
#                 setattr(self.dataOut,listDataname[j],listData[j][blockList[blockIndex]])
                setattr(self.dataOut,'utctimeInit',listData[j][blockList[blockIndex]])
                continue

            setattr(self.dataOut,listDataname[j],listData[j][blockList[blockIndex],:])

        return self.dataOut.data_param

    def getData(self):

#         if self.flagNoMoreFiles:
#             self.dataOut.flagNoData = True
#             print 'Process finished'
#             return 0
#
        if self.blockIndex==self.blocksPerFile:
             if not( self.__setNextFileOffline() ):
                self.dataOut.flagNoData = True
                return 0

#
#         if self.datablock == None: # setear esta condicion cuando no hayan datos por leers
#             self.dataOut.flagNoData = True
#             return 0

        self.__readData()
        self.__setDataOut()
        self.dataOut.flagNoData = False

        self.blockIndex += 1

        return

    def run(self, **kwargs):

        if not(self.isConfig):
            self.setup(**kwargs)
#             self.setObjProperties()
            self.isConfig = True

        self.getData()

        return

class HDF5Writer(Operation):

    ext = ".hdf5"

    optchar = "D"

    metaoptchar = "M"

    metaFile = None

    path = None

    setFile = None

    fp = None

    grp = None

    ds = None
    ds_aux= None

    firsttime = True

    #Configurations

    blocksPerFile = None

    blockIndex = None

    dataOut = None

    #Data Arrays

    dataList = None

    metadataList = None

    arrayDim = None

    tableDim = None

#     dtype = [('arrayName', 'S20'),('nChannels', 'i'), ('nPoints', 'i'), ('nSamples', 'i'),('mode', 'b')]

    dtype = [('arrayName', 'S20'),('nDimensions', 'i'), ('dim2', 'i'), ('dim1', 'i'),('dim0', 'i'),('mode', 'b')]

    mode = None

    nDatas = None    #Number of datasets to be stored per array

    nDims = None  #Number Dimensions in each dataset

    def __init__(self):

        Operation.__init__(self)
        self.isConfig = False
        return


    def setup(self, dataOut, **kwargs):

        self.path = kwargs['path']

        if kwargs.has_key('ext'):
            self.ext = kwargs['ext']

        if kwargs.has_key('blocksPerFile'):
            self.blocksPerFile = kwargs['blocksPerFile']
        else:
            self.blocksPerFile = 10

        self.metadataList = kwargs['metadataList'] # Jm: Every important information goes at metadataList

        self.dataList = kwargs['dataList'] # Jm : all data that we want put in the file

        self.dataOut = dataOut
        #print 'self.dataOut.last_block:',self.dataOut.last_block

        if kwargs.has_key('mode'):
            mode = kwargs['mode']

            if type(mode) == int:
                mode = numpy.zeros(len(self.dataList)) + mode
                #Mode is the number of parameters? mode = [1,1,1]

        else:
            mode = numpy.zeros(len(self.dataList))

        self.mode = mode

        arrayDim = numpy.zeros((len(self.dataList),5)) # Jm: this has to be the Parameters
        #arrayDim = [[ 0.  0.  0.  0.  0.] [ 0.  0.  0.  0.  0.] [ 0.  0.  0.  0.  0.]]
        #print 'arrayDim:', arrayDim
        #Table dimensions

        dtype0 = self.dtype

        tableList = []

        for i in range(len(self.dataList)): # this FOR feed the hdf5 metadata file!!! this made 3 times

            dataAux = getattr(self.dataOut, self.dataList[i]) # here we extract the any attribute from dataout. must macht with the string name

            if type(dataAux)==float or type(dataAux)==int:
                arrayDim[i,0] = 1
            else:

                arrayDim0 = dataAux.shape
                arrayDim[i,0] = len(arrayDim0)
                arrayDim[i,4] = mode[i]

                if len(arrayDim0) == 3:
                    #print 'len(arrayDim0) == 3 : ', numpy.array(arrayDim0)
                    arrayDim[i,1:-1] = numpy.array(arrayDim0)
                elif len(arrayDim0) == 2:
                    #print 'len(arrayDim0) == 2 : ', numpy.array(arrayDim0)
                    arrayDim[i,2:-1] = numpy.array(arrayDim0) #nHeights
                elif len(arrayDim0) == 1:
                    #print 'len(arrayDim0) == 1 : ', numpy.array(arrayDim0)
                    arrayDim[i,3] = numpy.array(arrayDim0)
                elif len(arrayDim0) == 0:
                    #print 'len(arrayDim0) == 0 : ', numpy.array(arrayDim0)
                    arrayDim[i,0] = 1
                    arrayDim[i,3] = 1
            #print 'arrayDim[i,:]',arrayDim[i,:]#Are the array dimensions
            table = numpy.array((self.dataList[i],) + tuple(arrayDim[i,:]),dtype = dtype0)
            tableList.append(table)

        self.arrayDim = arrayDim
        self.tableDim = numpy.array(tableList, dtype = dtype0)
        self.blockIndex = 0

        return

    def putMetadata(self):

        fp = self.createMetadataFile()
        self.writeMetadata(fp)
        fp.close()
        return

    def createMetadataFile(self):
        ext = self.ext
        path = self.path
        setFile = self.setFile

        timeTuple = time.localtime(self.dataOut.utctime)
        subfolder = ''

        fullpath = os.path.join( path, subfolder )
        if not( os.path.exists(fullpath) ):
            os.mkdir(fullpath)
            setFile = -1 #inicializo mi contador de seteo
        else:
            filesList = os.listdir( fullpath )
            if len( filesList ) > 0:
                filesList = sorted( filesList, key=str.lower )
                filen = filesList[-1]
                # el filename debera tener el siguiente formato
                # 0 1234 567 89A BCDE (hex)
                # x YYYY DDD SSS .ext
                if isNumber( filen[8:11] ):
                    setFile = int( filen[8:11] ) #inicializo mi contador de seteo al seteo del ultimo file
                else:
                    setFile = -1
            else:
                setFile = -1 #inicializo mi contador de seteo

        setFile += 1

        filex = '%s%4.4d%3.3d%3.3d%s' % (self.metaoptchar,
                                        timeTuple.tm_year,
                                        timeTuple.tm_yday,
                                        setFile,
                                        ext )

        filename = os.path.join( path, subfolder, filex )
        self.metaFile = filex
        fp = h5py.File(filename,'w')

        return fp

    def writeMetadata(self, fp):

        grp = fp.create_group("Metadata")
        grp.create_dataset('array dimensions', data = self.tableDim, dtype = self.dtype)

        for i in range(len(self.metadataList)):
            grp.create_dataset(self.metadataList[i], data=getattr(self.dataOut, self.metadataList[i]))
        return

    def setNextFile(self):

        ext = self.ext
        path = self.path
        setFile = self.setFile
        mode = self.mode

        if self.fp != None:
            self.fp.close()

        timeTuple = time.localtime(self.dataOut.utctime)
        subfolder = 'd%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)

        fullpath = os.path.join( path, subfolder )
        if not( os.path.exists(fullpath) ):
            os.mkdir(fullpath)
            setFile = -1 #inicializo mi contador de seteo
        else:
            filesList = os.listdir( fullpath )
            if len( filesList ) > 0:
                filesList = sorted( filesList, key=str.lower )
                filen = filesList[-1]
                # el filename debera tener el siguiente formato
                # 0 1234 567 89A BCDE (hex)
                # x YYYY DDD SSS .ext
                if isNumber( filen[8:11] ):
                    setFile = int( filen[8:11] ) #inicializo mi contador de seteo al seteo del ultimo file
                else:
                    setFile = -1
            else:
                setFile = -1 #inicializo mi contador de seteo

        setFile += 1

        file = '%s%4.4d%3.3d%3.3d%s' % (self.optchar,
                                        timeTuple.tm_year,
                                        timeTuple.tm_yday,
                                        setFile,
                                        ext )

        filename = os.path.join( path, subfolder, file )

        #Setting HDF5 File
        fp = h5py.File(filename,'w')
        #grp = fp.create_group("Data")
        #grp.attrs['metadata'] = self.metaFile

#         grp.attrs['blocksPerFile'] = 0

        ds_aux = []
        ds= []
        data = []

        nDatas = numpy.zeros(len(self.dataList))
        nDims = self.arrayDim[:,0]

        for i in range(len(self.dataList)):

            if nDims[i]==1:
                #ds0 = grp.create_dataset(self.dataList[i], (1,1), maxshape=(1,None) , chunks = True,dtype='S20')
                #ds.append(ds0)

                ds0_aux=numpy.zeros((20),dtype = "f") #"c"
                ds_aux.append(ds0_aux)

                data.append([])

            else:

                if mode[i]==0:
                    strMode = "channel"
                    nDatas[i] = self.arrayDim[i,1]
                else:
                    strMode = "param"
                    nDatas[i] = self.arrayDim[i,2]

                if nDims[i]==2:
                    nDatas[i] = self.arrayDim[i,2]

                #grp0 = grp.create_group(self.dataList[i]) # create subgroupList la lista de datos
                #Create the number of dataset required by the group
                for j in range(int(nDatas[i])): # this put each channel or param"X"
                    tableName = strMode + str(j) #This is the name param0 param1 param2 viewed at hdf5 file or channel0 -channel1

                    if nDims[i] == 3:
                        #ds0 = grp0.create_dataset(tableName, (1,1,1) , maxshape=(None,None,None), chunks=True,dtype="f")
                        ds0_aux = numpy.zeros((1,1,1),dtype="f")
                    else:
                        #ds0 = grp0.create_dataset(tableName, (1,1) , maxshape=(None,None), chunks=True,dtype="f")
                        ds0_aux = numpy.zeros((1,1),dtype="f")

                    #ds.append(ds0) #this is a datasets buffer
                    ds_aux.append(ds0_aux)
                    data.append([])

        self.nDatas = nDatas
        self.nDims = nDims

        #Saving variables
        print 'Writing the file: %s'%filename
        self.fp = fp
        #self.grp = grp #This is the hdf5 files, here we can create N groups
        self.ds = ds
        self.ds_aux = ds_aux
        self.data = data

        self.setFile = setFile
        self.firsttime = True
        self.blockIndex = 0
        return

    def putData(self):
        self.setBlock()
        #Just for testing
        self.writeBlock()
        #If file is the last file  writeBlockF!
        if self.blockIndex == self.blocksPerFile:
            self.writeBlockF() # this function is the only one that write data in hdf5 files
            self.setNextFile()
        print 'self.dataOut.flagNoData:', self.dataOut.flagLastFile
        #raw_input("2. Si existe el Flag de last file entonces writeBlockF, hay q traerlo por dataOut.")
        #Hay q acomodar los datos que van a entrar para ver si se puede grabar asi sin 10 bloques.
        return

    def setBlock(self):
        '''
        data Array configured
        self.data
        '''
        #Creating Arrays
        data = self.data
        nDatas = self.nDatas
        nDims = self.nDims
        mode = self.mode
        ind = 0

        for i in range(len(self.dataList)):
            dataAux = getattr(self.dataOut,self.dataList[i])
            if nDims[i] == 1:
                data[ind] = numpy.array([str(dataAux)]).reshape((1,1))
                if not self.firsttime:
                    #data[ind] = numpy.hstack((self.ds[ind][:], self.data[ind]))
                    data[ind] = numpy.hstack((self.ds_aux[ind][:], self.data[ind]))
                ind += 1

            else:
                for j in range(int(nDatas[i])):
                    if (mode[i] == 0) or (nDims[i] == 2):       #In case division per channel or Dimensions is only 1
                        data[ind] = dataAux[j,:]
                    else:
                        data[ind] = dataAux[:,j,:]

                    if nDims[i] == 3:
                        data[ind] = data[ind].reshape((data[ind].shape[0],data[ind].shape[1],1))

                        if not self.firsttime:
                            #data[ind] = numpy.dstack((self.ds[ind][:], data[ind]))
                            data[ind] = numpy.dstack((self.ds_aux[ind][:], data[ind]))

                    else:
                        data[ind] = data[ind].reshape((1,data[ind].shape[0]))

                        if not self.firsttime:
                            #data[ind] = numpy.vstack((self.ds[ind][:], data[ind]))
                            data[ind] = numpy.vstack((self.ds_aux[ind][:], data[ind]))
                    ind += 1

        self.data = data
        return

    def writeBlock(self):
        '''
        Saves the block in the HDF5 file
        '''
        #for i in range(len(self.ds)):
        for i in range(len(self.ds_aux)):
            self.ds_aux[i].resize(self.data[i].shape)#Prepare the dataset to put the data
            self.ds_aux[i][:] = self.data[i] # put the data

        self.blockIndex += 1
        #self.grp.attrs.modify('nRecords', self.blockIndex)
        self.firsttime = False
        return

    def writeBlockF(self):
        '''
        Saves the block in the HDF5 file
        '''
        nDatas = numpy.zeros(len(self.dataList))
        nDims = self.arrayDim[:,0]
        k=0
        grp = self.fp.create_group("Data")
        grp.attrs['metadata'] = self.metaFile
        grp.attrs.modify('nRecords', self.blockIndex)
        for i in range(len(self.dataList)):
            if self.data[k].shape[0]==1:
                #TODO : when is one array element, try to put the correct dtype to dataset, now is set by the incoming variable
                ds0 = grp.create_dataset(self.dataList[i], (self.data[k].shape[0],self.data[k].shape[1]), maxshape=(1,None) , chunks = True)
                ds0.resize(self.data[k].shape)#Prepare the dataset to put the data
                ds0[...] = self.ds_aux[k] # put the data
                k+=1

            else:
                if self.mode[i]==0:
                    strMode = "channel"
                    nDatas[i] = self.arrayDim[i,1]
                else:
                    strMode = "param"
                    nDatas[i] = self.arrayDim[i,2]

                if nDims[i]==2:
                    nDatas[i] = self.arrayDim[i,2]

                grp0 = grp.create_group(self.dataList[i]) # create groupList la lista de datos
                #Create the number of dataset required by the group
                for j in range(int(nDatas[i])): # this put each channel or param"X"
                    tableName = strMode + str(j) #This is the name param0 param1 param2 viewed at hdf5 file or channel0 -channel1
                    #print  tableName
                    if nDims[i] == 3:
                        ds0 = grp0.create_dataset(tableName, (self.data[k].shape[0],self.data[k].shape[1],self.data[k].shape[2]) , maxshape=(None,None,None), chunks=True,dtype="f")
                    else:
                        ds0 = grp0.create_dataset(tableName, (self.data[k].shape[0],self.data[k].shape[1]) , maxshape=(None,None), chunks=True,dtype="f")

                    ds0[...] = self.ds_aux[k] # put the data
                    k+=1
        return

    def run(self, dataOut, **kwargs):
        if not(self.isConfig):
            self.setup(dataOut, **kwargs)
            self.isConfig = True # Just do it the first time
            self.putMetadata()
            self.setNextFile()

        self.putData()
        #TODO : IF the HDF5 file is the last one, call writeBlockF and close the file.
        return
