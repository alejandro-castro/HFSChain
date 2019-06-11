import numpy
import time
import os
import h5py
import re
import copy

from model.data.jrodata import *
from model.proc.jroproc_base import ProcessingUnit, Operation
from model.io.jroIO_base import *

#Alejandro Castro: This class is not used in HF, therefore it hasn't been reviewed
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
		#self.all = all
		#self.online = online
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

		#self.__getExpParameters()

		self.fileIndex = -1

		self.__setNextFileOffline()

		self.__readMetadata()

		self.blockIndex = 0


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

		#self.__setParameters(path, startDate, endDate, startTime, endTime, walk)
		#
		#self.__checkPath()
		#
		#self.__findDataForDates()
		#
		#self.__selectDataForTimes()
		#
		#for i in range(len(self.filenameList)):
			#print "%s" %(self.filenameList[i])

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
			filename			:	nombre completo del archivo de datos en formato Jicamarca (.r)

			startTime		  :	tiempo inicial del rango seleccionado en formato datetime.time

			endTime			:	tiempo final del rango seleccionado en formato datetime.time

		Return:
			Boolean	:	Retorna True si el archivo de datos contiene datos en el rango de
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
		#self.nRecords = self.fp['Data'].attrs['blocksPerFile']
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

	def __setDataArray(self, nRecords, dataset, shapes):

		nChannels = shapes[0]	#Dimension 0

		nPoints = shapes[1]	  #Dimension 1, number of Points or Parameters

		nSamples = shapes[2]	 #Dimension 2, number of samples or ranges

		mode = shapes[3]

		#if nPoints>1:
			#arrayData = numpy.zeros((nRecords,nChannels,nPoints,nSamples))
		#else:
			#arrayData = numpy.zeros((nRecords,nChannels,nSamples))
		#
		#chn = 'channel'
		#
		#for i in range(nChannels):
			#data = dataset[chn + str(i)].value
			#if nPoints>1:
				#data = numpy.rollaxis(data,2)

			#arrayData[:,i,:] = data

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

		if type =='Parameters':
			self.dataOut = Parameters()
		elif type =='Spectra':
			self.dataOut = Spectra()
		elif type =='Voltage':
			self.dataOut = Voltage()
		elif type =='Correlation':
			self.dataOut = Correlation()


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
				#setattr(self.dataOut,listDataname[j],listData[j][blockList[blockIndex]])
				setattr(self.dataOut,'utctimeInit',listData[j][blockList[blockIndex]])
				continue

			setattr(self.dataOut,listDataname[j],listData[j][blockList[blockIndex],:])

		return self.dataOut.data_param

	def getData(self):

		#if self.flagNoMoreFiles:
			#self.dataOut.flagNoData = True
			#print 'Process finished'
			#return 0

		if self.dataOut.flagLastFile == True:
			print 'flagLastFile:',self.dataOut.flagLastFile

		if self.blockIndex==self.blocksPerFile:
			 if not( self.__setNextFileOffline() ):
				self.dataOut.flagNoData = True
				return 0

		#
		#if self.datablock == None: # setear esta condicion cuando no hayan datos por leers
			#self.dataOut.flagNoData = True
			#return 0

		self.__readData()
		self.__setDataOut()
		self.dataOut.flagNoData = False

		self.blockIndex += 1


	def run(self, **kwargs):

		if not(self.isConfig):
			self.setup(**kwargs)
			#self.setObjProperties()
			self.isConfig = True

		self.getData()


class HDF5Writer(Operation):
	def __init__(self):
		Operation.__init__(self)
		self.isConfig = False
		self.path = None
		self.location = None
		self.identifier = None
		#List of data and metadata to be save_int_data
		self.dataList = None
		self.metadataList = None

		# Dimensions and Data Arrays:
		self.arrayDim = None
		self.tableDim = None
		self.dtype = [('arrayName', 'S20'),('nDimensions', 'i'), ('dim2', 'i'), ('dim1', 'i'),('dim0', 'i')]
		self.nDatas = None	#Number of datasets to be stored per array
		self.nDims = None  #Number Dimensions in each dataset
		#File Configurations
		self.blocksPerFile = None
		self.ext = ".hdf5"
		self.optchar = "D"
		self.metaoptchar = "M"

		#Flags
		self.blockIndex = None
		self.fp = None

		#Others
		self.metaFile = None
		self.grp = None
		self.ds_aux= None
		self.firsttime = True
		self.dataOut = None

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

		if 'location' in self.dataList:#Only uses the datalist to ensure the location is set only when wanted
			self.dataList.remove('location')
			if kwargs.has_key('location'):
				self.location = kwargs['location']

		if 'identifier' in self.dataList:#Only uses the datalist to ensure the identifier is set only when wanted
			self.dataList.remove('identifier')
			if kwargs.has_key('identifier'):
				self.identifier = kwargs['identifier']


		self.dataOut = dataOut

		arrayDim = numpy.zeros((len(self.dataList),4))

		tableList = []

		for i in range(len(self.dataList)):
			dataAux = getattr(self.dataOut, self.dataList[i]) # here we extract the any attribute from dataout. must macht with the string name

			arrayDim0 = dataAux.shape
			arrayDim[i,0] = len(arrayDim0)# Guarda en la primera posicion el numero de dimensiones de la data pedida, RGB, param, etc

			if len(arrayDim0) == 3:# dataAux tiene un array de 3 dimensiones
				arrayDim[i,1:] = numpy.array(arrayDim0)
			elif len(arrayDim0) == 2:# dataAux tiene un array de 2 dimensiones
				arrayDim[i,2:] = numpy.array(arrayDim0) #nHeights
			elif len(arrayDim0) == 1:# dataAux tiene un array de 1 dimensiones
				arrayDim[i,3] = numpy.array(arrayDim0)
			elif len(arrayDim0) == 0:# dataAux es posiblemente un escalar de Numpy
				arrayDim[i,0] = 1
				arrayDim[i,3] = 1

			table = numpy.array((self.dataList[i],) + tuple(arrayDim[i,:]),dtype = self.dtype)
			tableList.append(table)

		self.arrayDim = arrayDim
		self.tableDim = numpy.array(tableList, dtype = self.dtype)# The same as arrayDim but it has the name of the parameter added
		self.blockIndex = 0

	def putMetadata(self):

		fp = self.createMetadataFile()
		self.writeMetadata(fp)
		fp.close()

	def createMetadataFile(self):
		#TODO by Jm : Aqui agregar todos los atributos de la estacion por ejemplo:
		#LAT,LONG,ALT,NOMBRE,UBICACION,TIPO DE USRP Y DE DAUGTHERBOARD, TIPO DE ANTENA
		#NUMERO DE CANALES, ORIENTACION, ENTRADA DE REFERENCIA PARA CALIBRACION, etc.
		#Que son los datos, por ejemplo explicar de donde viene la data RGB, o la CrossData, etc.
		timeTuple = time.localtime(self.dataOut.utctime)
		fullpath = self.path + ("/" if self.path[-1]!="/" else "")

		if not os.path.exists(fullpath):
			os.mkdir(fullpath)

		filex = '%s%4.4d%3.3d%s' % (self.metaoptchar,
										timeTuple.tm_year,
										timeTuple.tm_yday,
										self.ext)

		filename = os.path.join(fullpath, filex)
		self.metaFile = filex
		fp = h5py.File(filename,'w')

		return fp

	def writeMetadata(self, fp):
		grp = fp.create_group("Metadata")
		grp.create_dataset('array dimensions', data = self.tableDim, dtype = self.dtype, compression="gzip")

		for i in range(len(self.metadataList)):
			#Try to compress
			data=getattr(self.dataOut, self.metadataList[i])
			if hasattr(data, 'len') and type(data)!=str:
				grp.create_dataset(self.metadataList[i], data=data, compression="gzip")
			else:
				grp.create_dataset(self.metadataList[i], data=data)

	def setNextFileName(self):
		if self.fp != None:
			self.fp.close()
		timeTuple = time.localtime(self.dataOut.utctime)
		subfolder = 'd%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)

		fullpath = os.path.join(self.path, subfolder )
		if not( os.path.exists(fullpath) ):
			os.mkdir(fullpath)
		# Se elimino el uso de setFile flag porque no es util el ver los archivos y luego crear nuevos existentes en la carpeta destino
		# Y luego crear nuevos dado que esto hace que el correr dos veces el mismo programa genere mas y mas archivos de data repetidos

		file = '%s%012d%s' % (self.optchar, round(self.dataOut.utctime),
										self.ext )

		filename = os.path.join(self.path, subfolder, file )

		#Setting HDF5 File
		try:
			fp = h5py.File(filename,'a')#Se cambio de w a a para que asi el ultimo set next file cuando se termina antes de 23:59:59 no elimine la data del prox archivo
		except IOError:
			fp = h5py.File(filename,'w')
		self.fp = fp

	def setNextFile(self):
		# if self.fp != None:
		# 	self.fp.close()
		# timeTuple = time.localtime(self.dataOut.utctime)
		# subfolder = 'd%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)
		#
		# fullpath = os.path.join(self.path, subfolder )
		# if not( os.path.exists(fullpath) ):
		# 	os.mkdir(fullpath)
		# # Se elimino el uso de setFile flag porque no es util el ver los archivos y luego crear nuevos existentes en la carpeta destino
		# # Y luego crear nuevos dado que esto hace que el correr dos veces el mismo programa genere mas y mas archivos de data repetidos
		#
		# file = '%s%012d%s' % (self.optchar, round(self.dataOut.utctime),
		# 								self.ext )
		#
		# filename = os.path.join(self.path, subfolder, file )
		#
		# #Setting HDF5 File
		# try:
		# 	fp = h5py.File(filename,'a')#Se cambio de w a a para que asi el ultimo set next file cuando se termina antes de 23:59:59 no elimine la data del prox archivo
		# except IOError:
		# 	fp = h5py.File(filename,'w')
		data = []

		nDatas = numpy.zeros(len(self.dataList))
		nDims = self.arrayDim[:,0]

		for i in range(len(self.dataList)):
			if nDims[i]==1:
				data.append(numpy.zeros(1,dtype = numpy.float64))#"c"
			else:
				if nDims[i]==3:
					nDatas[i] = self.arrayDim[i,1]

				elif nDims[i]==2:
					nDatas[i] = self.arrayDim[i,2]

				#Create the number of datasets required by the group
				for j in range(int(nDatas[i])): # this put each channel or param"X"
					if nDims[i] == 3:
						data.append(numpy.zeros((1,1,1),dtype="f", order='F'))
					else:
						data.append(numpy.zeros((1,1),dtype="f", order='F'))
		self.nDatas = nDatas
		self.nDims = nDims

		#Saving variables
		# self.fp = fp
		self.data = data

		self.firsttime = True
		self.blockIndex = 0

	def putData(self):
		if self.blockIndex == 0: # was incremented by 1 by the self.writeBlock method
			self.setNextFileName()

		self.setBlock()
		self.writeBlock()
		#If file is the last file  writeBlockF!
		#Viene de jroproc_parameters, deberia ser true


		if self.dataOut.flagLastFile: #This case occurs when the files are no NumberBlocks multipler.
			#self.setNextFile()# added 06/06/19
			self.writeBlockF()
			self.fp.close()

		elif self.blockIndex == self.blocksPerFile:
			#self.setNextFile()# added 06/06/19
			self.writeBlockF() # this function is the only one that write data in hdf5 files
			self.setNextFile()# it was here uncommented 06/06/19


	def setBlock(self):
		'''
		data Array configured
		self.data
		'''
		#Creating Arrays
		data = self.data
		nDatas = self.nDatas
		nDims = self.nDims
		ind = 0

		for i in range(len(self.dataList)):
			dataAux = getattr(self.dataOut,self.dataList[i])
			if nDims[i] == 1:
				newData = dataAux

				if self.firsttime:
					data[ind][0]= newData
				else:
					data[ind].resize(data[ind].size+1)
					data[ind][-1]= newData
				ind += 1

			else:
				for j in range(int(nDatas[i])):
					if nDims[i] == 3:
						newData = dataAux[j,:,:].transpose()
					else:
						newData = dataAux[j,:]
					if self.firsttime:
						data[ind]=numpy.array([newData], order='F')
					else:
						aux = data[ind].tolist()
						aux.append(newData)
						data[ind] = numpy.array(aux, order='F')

					ind += 1

		self.data = data

	def writeBlock(self):
		'''
		Saves the block in the HDF5 file
		'''
		self.blockIndex += 1
		self.firsttime = False

	def writeBlockF(self):
		'''
		Saves the block in the HDF5 file
		'''
		#print self.dataOut.data_SNR[:,0], self.dataOut.data_param[:,:,0]

		nDims = self.arrayDim[:,0]
		k=0
		if "Data" in self.fp.keys():#Means the file exists, so its data should be erased
			del self.fp["Data"]
			del self.fp["location"]
			del self.fp["identifier"]


		grp = self.fp.create_group("Data")
		grp.attrs['metadata'] = self.metaFile
		grp.attrs.modify('nRecords', self.blockIndex)
		for i in range(len(self.dataList)):
			if len(self.data[k].shape) ==1:
				ds0 = grp.create_dataset(self.dataList[i], (1, self.data[k].shape[0]), maxshape=(1,None) , chunks = True, compression="gzip", dtype= numpy.float64)
				ds0[...] = self.data[k] # put the data
				k+=1

			else:
				strMode = "channel"

				grp0 = grp.create_group(self.dataList[i]) # create groupList la lista de datos
				#Create the number of dataset required by the group
				for j in range(int(self.nDatas[i])): # this put each channel or param"X"
					tableName = strMode + str(j) #This is the name param0 param1 param2 viewed at hdf5 file or channel0 -channel1

					if self.dataList[i] == "CrossData": #Exception
						if j == 0:
							tableName = "amplitude"
						elif j == 1:
							tableName = "phase"
						else:
							raise ValueError("CrossData was generated wrong")

					if nDims[i] == 3:
						self.data[k] = self.data[k].transpose()# Because the blocks per file should be the last shape
						ds0 = grp0.create_dataset(tableName, (self.data[k].shape[0],self.data[k].shape[1],self.data[k].shape[2]) , maxshape=(None,None,None), chunks=True,dtype="f", compression="gzip")
					else:
						ds0 = grp0.create_dataset(tableName, (self.data[k].shape[0],self.data[k].shape[1]) , maxshape=(None,None), chunks=True,dtype="f", compression="gzip")

					ds0[...] = self.data[k] # put the data
					k+=1
		if self.location != None:
			self.fp['location']= self.location

		if self.identifier != None:
			self.fp['identifier']= self.identifier
		print 'Writing the file: %s'%self.fp.filename

	def run(self, dataOut, **kwargs):#dataOut debe ser dataIn ya que es entrada de esta operacion aunque venga de un proc
		if not(self.isConfig):
			self.setup(dataOut, **kwargs)
			self.isConfig = True # Just do it the first time
			self.putMetadata()
			self.setNextFile() # it was here uncommented 06/06/19

		self.putData()
