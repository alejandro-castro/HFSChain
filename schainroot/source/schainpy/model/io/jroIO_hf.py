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
from model.data.jrodata import Voltage, Parameters
from model.proc.jroproc_base import ProcessingUnit, Operation

def isNumber(str):
	"""
	Chequea si el conjunto de caracteres que componen un string puede ser convertidos a un numero.
	Input:
		str, string al cual se le analiza para determinar si convertible a un numero o no
	Return:
		True	:	si el string es uno numerico
		False   :	no es un string numerico
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
	#print date_time
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
	except ValueError:
		return 0

	try:
		doy = int(folder[5:8])
	except ValueError:
		return 0

	return 1

###Online mode functions
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
	 #	   year = int(thisFile[1:5])
	 #	   doy  = int(thisFile[5:8])
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
		fileList	:	lista conteniendo todos los files (sin path) que componen una determinada carpeta
		ext		 :	extension de los files contenidos en una carpeta

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
		#year = thisFile[1:5]
		#if not isNumber(year):
			#continue
		#doy = thisFile[5:8]
		#if not isNumber(doy):
		#continue
		number= int(number)
		#year = int(year)
		#doy = int(doy)
		if (os.path.splitext(thisFile)[-1].lower() != ext.lower()):
			continue
		validFilelist.append(thisFile)
	if validFilelist:
		validFilelist = sorted( validFilelist, key=str.lower )
		return validFilelist[-1]
	return None

class HFReader(ProcessingUnit):
	walk	 = None
	def __init__(self):
		ProcessingUnit.__init__(self)
		### Path and Time
		self.path	 = None
		self.startDate= None
		self.endDate  = None
		self.startTime= None
		self.endTime  = None
		self.add_folder = '' # add_folder determines the last subfolder down the doy folder, where the hdf5 files are
		#For example in HFreader is should be sp11_f1, etc and for the HDF5 with momments, should be ''
		###Flags
		self.status=True
		self.isConfig =False
		self.flagIsNewFile = True
		self.flagLastFile = None
		self.flagNoMoreFiles= False
		###File Searching
		self.fileIndex = 0
		self.filenameList=[]
		self.datetimeList=[]
		self.sizeofHF_File= None
		self.ext='.hdf5'
		###Online
		self.filename_online = None
		self.__waitForNewFile = 45
		self.filename_next_set=None
		###Campaign
		self.campaign = 1
		self.__inc_int = 0
		###Data and DataOut
		self.datablock = None
		self.dataImage = None
		self.datacspec = None
		self.dataOut = Voltage()
		###Paremeters
		self.nChannels = 2
		self.frequency = None
		self.__firstHeigth=0
		self.__nSamples=1000
		self.__deltaHeigth=1.5
		self.__sample_rate=1e5
		self.profileIndex = 0

	def __setParameters(self,path='',frequency='', startDate='',endDate='',startTime='', endTime='', walk=''):
		self.path = path
		self.frequency=frequency
		self.startDate = startDate
		self.endDate = endDate
		self.startTime = startTime
		self.endTime = endTime
		self.walk = walk

	def __checkPath(self):
		self.status = os.path.exists(self.path)
		if not self.status:
			print 'Path %s does not exist.'%self.path

	def isFileInTimeRange(self, filename,startDate,endDate,startTime,endTime,timezone):
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
		#print date_time
		fp.close()

		this_time=date_time

		if not ((startDateTime_Reader <= this_time) and (endDateTime_Reader> this_time)):
			return None

		return this_time

	###Online Methods
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

	def __selectDataForTimes(self, online=False):
		if not(self.status):
			return None
		self.__getFilenameList()
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

					fullfilename=self.path+"/"+filename
					self.filenameList=[fullfilename]
					self.filename_next_set=int(filename[7:17])+10*value_set
					print "Setting next file",self.filename_next_set
					self.set=int(filename[7:17])
					if True:
						pass
					else:
						print "No existe el siguiente archivo"

	def __getFilenameList(self):
		dirList = [os.path.join(self.path,x) for x in self.dirnameList]
		self.filenameList= dirList

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

			if self.frequency<3:
				add_folder='sp'+str(self.code)+'1_f0'
				flag=True
			if self.frequency>=3:
				add_folder='sp'+str(self.code)+'1_f1'
				flag=True
			if not flag:
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

	def __setNextFileOnline(self):
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
		fp.close()
		self.__t0=epoc

		self.flagIsNewFile = True
		self.filename = filename

		print "Setting the file: %s for reading."%self.filename
		return 1

	### Offline Methods
	def __findDataForDates(self,online=False):
		if not(self.status):
			return

		dirList=[]
		for thisPath in os.listdir(self.path):
			if not os.path.isdir(os.path.join(self.path,thisPath)):
				continue
			if not isDoyFolder(thisPath):
				continue

			dirList.append(thisPath)

		if not(dirList):
			return
		thisDate=self.startDate

		pathList = []
		while(thisDate <= self.endDate):
				year = thisDate.timetuple().tm_year
				doy = thisDate.timetuple().tm_yday
				#Why not glob.glob
				matchlist = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy) + '*')
				if len(matchlist) == 0:
					thisDate += datetime.timedelta(1)
					continue
				for match in matchlist:
					pathList.append(os.path.join(self.path,match))

				thisDate += datetime.timedelta(1)

		if pathList == []:
			print "Any folder was found for the date range: %s-%s" %(self.startDate, self.endDate)
			return

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


		for i in range(len(pathList)):
			if isinstance(self, HFParamReader):# This is done so the 100 lines of code of this method can be reuse
				pathList[i] = pathList[i]+"/"
			else:
				pathList[i] = pathList[i]+"/"+add_folder

		for path in pathList:
			fileList = glob.glob1(path, "*%s" %self.ext)
			fileList.sort()

			##################### NEW - PART - OFF LINE ##############
			last_filename=os.path.join(path,fileList[-1])
			self.sizeofHF_File=os.path.getsize(last_filename)
			##################################################
			for file in fileList:
				filename = os.path.join(path,file)

				sizeoffile= verifyFile(filename,size=self.sizeofHF_File)#9650368 en 600
				#*************************************************************
				#if not (sizeoffile):
				#	continue

				#TODO by Jm: Verificar de otro modo si el archivo esta bien.
				# Porque puede ser un archivo de menos files.
				#**************************************************************

				thisDatetime = self.isFileInTimeRange(filename, self.startDate,self.endDate,self.startTime, self.endTime,self.timezone)

				if not(thisDatetime):
					continue

				filenameList.append(filename)
				datetimeList.append(thisDatetime)

		if not(filenameList):
			print "Any file was found for the time range %s - %s" %(self.startTime, self.endTime)
			return

		print "%d file(s) was(were) found for the time range: %s - %s\n" %(len(filenameList), self.startTime, self.endTime)

		for i in range(len(filenameList)):
			print "%s -> [%s]" %(filenameList[i], datetimeList[i].ctime())

		self.filenameList = filenameList
		self.datetimeList = datetimeList

	def searchFilesOffline(self,
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
		self.__findDataForDates()
		self.dataOut.last_block = len(self.filenameList)

	def __setNextFileOffline(self):

		if (self.fileIndex == (len(self.filenameList)-1) ):
			self.flagLastFile = True

			print "Last File, put flag."
		else:
			self.flagLastFile = False

		if not (self.fileIndex < len(self.filenameList)):
			self.flagNoMoreFiles = True
			print "No more Files - Last Update 8/03/19"
			return 0

		filename = self.filenameList[self.fileIndex]
		hfFilePointer =h5py.File(filename,'r')
		epoch=hfFilePointer['t'].value
		name_prof='pw0_C'+str(self.code)
		self.nProfiles= len((hfFilePointer[name_prof]))


		self.flagIsNewFile = True
		self.filename = filename
		hfFilePointer.close()
		self.__t0=epoch
		self.fileIndex += 1

		print "Setting the file: %s for reading"%self.filename
		return 1

	def __setNextFile(self,online=False):
		if not(online):
			newFile = self.__setNextFileOffline()
		else:
			newFile = self.__setNextFileOnline()

		if not(newFile):
			return 0
		return 1

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
		self.campaign = campaign

		if type(inc_int) == int:
			self.__inc_int= inc_int
		else:
			raise ValueError, "The number of incoherent integration should be an integer"

		if self.__inc_int>6:
			raise ValueError, "The number of incoherent integration should be between 0 and 6"

		self.timezone= timezone
		self.online= online
		self.all=all
		if not(online):
			print "Searching files in offline mode..."
			self.searchFilesOffline(path,frequency,startDate, endDate, ext, startTime, endTime, walk)
		else:
			print "Searching files in online mode..."
			self.__searchFilesOnline(path,frequency,startDate,endDate,ext,walk,set)
			if set!=None:
				self.set=set-10

		if not(self.filenameList):
			print "There  is no files into the folder: %s"%(path)
			sys.exit(-1)

		self.__setNextFile(online)
		self.setHeaderDO()

	def setHeaderDO(self):
		#No eliminar asi como asi
		'''Set Header for dataOut'''
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

		self.dataOut.data = None

		self.dataOut.dtype = numpy.dtype([('real','<f4'),('imag','<f4')])

		self.dataOut.nProfiles = 1

		self.dataOut.heightList = self.__firstHeigth + numpy.arange(self.__nSamples, dtype = numpy.float)*self.__deltaHeigth

		self.dataOut.channelList = range(self.nChannels)

		#self.dataOut.channelIndexList = None
		self.dataOut.flagNoData = True
		self.dataOut.flagLastFile = self.flagLastFile

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


		self.dataOut.frequency = None

		self.dataOut.nIncohInt = self.__inc_int

		#print "QUE INTERESANTE",self.dataOut.nIncohInt,self.__inc_int

		self.dataOut.realtime = False

		self.dataOut.last_block = len(self.filenameList)

	def __hasNotDataInBuffer(self):
		return self.profileIndex >= self.nProfiles

	def readNextBlock(self):
		if not(self.flagIsNewFile or (self.profileIndex < self.nProfiles)):
			self.__setNextFile(self.online)

		if not(self.readBlock()):
			return False

		return True

	def readBlock(self):
		try:
			fp=h5py.File(self.filename,'r')
		except IOError:
			print "Error reading file %s"%self.filename

		#TODO 2018: Si ya hay un try arriba, porque hay un for abajo?

		if self.online:
			for i in range(4): #TODO 2018 , no deberia ir hasta 4 si esta en offline mode
				sizeoffile=os.path.getsize(self.filename) #TODO: what happend when is in online mode?
				#TODO 2018 > esto va ha fallar cuando sea online, xq el peso siempre sera igual al peso del archivo en ese instante.
				if sizeoffile<self.sizeofHF_File:#1650368:#1622336
					delay=80#WTFP?
					print 'sizeofile less than 9650368'
					print 'waiting %d  more seconds for delay...'%(delay)
					time.sleep(delay)
					fp=h5py.File(self.filename,'r')


		if self.code==None:
			self.code=0
		name0='pw0_C'+str(self.code)
		name1='pw1_C'+str(self.code)
		name2='cspec01_C'+str(self.code)

		name3='image0_C'+str(self.code)
		name4='image1_C'+str(self.code)

		ch0=(fp[name0]).value	#Primer canal (100,1000)--(perfiles,alturas)
		ch1=(fp[name1]).value	#Segundo canal (100,1000)--(perfiles,alturas)
		cspc=(fp[name2]).value   #cross spectra data from ch0 and ch1
		ch0_image = (fp[name3]).value #Image information to make RGB
		ch1_image = (fp[name4]).value #Image information to make RGB
		fp.close()

		ch0= ch0.swapaxes(0,1)   #Primer canal (100,1000)--(alturas,perfiles)
		ch1= ch1.swapaxes(0,1)   #Segundo canal (100,1000)--(alturas,perfiles)
		self.datablock = numpy.array([ch0,ch1])
		self.datacspec = numpy.array(cspc)
		self.dataImage = numpy.array([ch0_image.transpose(),ch1_image.transpose()])
		self.flagIsNewFile=False

		self.profileIndex=0

		return 1

	def getData(self):

		if self.flagNoMoreFiles:
			self.dataOut.flagNoData = True
			print 'Process finished.'
			return 0
		elif self.flagLastFile:
			self.dataOut.flagLastFile = True
		else:
			self.dataOut.flagNoData = False

		if self.__hasNotDataInBuffer() or self.profileIndex == 0:
			if not(self.readNextBlock()):
				self.dataOut.flagNodata=True
				return 0

		##############################
		##############################
		self.dataOut.data = self.datablock[:,:,self.profileIndex]
		self.dataOut.data_cspec = self.datacspec[self.profileIndex,:]
		self.dataOut.utctime = self.__t0 + self.dataOut.ippSeconds*self.profileIndex
		#print self.dataOut.utctime, self.__t0
		self.dataOut.Image = self.dataImage
		self.dataOut.profileIndex= self.profileIndex
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
	#Los datos compaJRODataReader,rtidos pueden tener efectos inesperados que involucren objetos mutables como ser listas y diccionarios.
	def __init__(self):
		HFReader.__init__(self)
		self.optchar = "D"
		self.timezone = None
		self.utcList = None	  #To select data in the utctime list
		self.blockList = None	#List to blocks to be read from the file
		self.blocksPerFile = None	#Number of blocks to be read, it's fixed by user
		self.blockIndex = None
		self.dictMetadata = None
		self.dictData = None
		self.listShapes = None
		self.fp = None
		self.dataOut = Parameters()

		self.number_of_files = None
		self.blocks_in_File = None #It will contain the number of block that the current file contains
		self.fileIndex = 0

	def isFileInTimeRange(self,filename, startDate, endDate, startTime, endTime, timezone):
		"""
		Retorna 1 si el archivo de datos se encuentra dentro del rango de horas especificado.
		Inputs:
			filename			:	nombre completo del archivo de datos en formato Jicamarca (.r)
			startDate		  :	fecha inicial del rango seleccionado en formato datetime.date
			endDate			:	fecha final del rango seleccionado en formato datetime.date
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

			fp = h5py.File(filename,'r')
			grp1 = fp['Data']

		except IOError:
			traceback.print_exc()
			raise IOError("The file %s can't be opened" %(filename))

		grp2 = grp1['utctime']
		thisUtcTime = grp2.value[0]

		thisUtcTime_inicial = thisUtcTime[0]
		thisUtcTime_final = thisUtcTime[-1]

		fp.close()
		# if timezone == 'lt':
		# 	thisUtcTime -= 5*3600
		firstdatetime = datetime.datetime.utcfromtimestamp(thisUtcTime_inicial+timezone)
		finaldatetime = datetime.datetime.utcfromtimestamp(thisUtcTime_final+timezone)

		startUtcTime = datetime.datetime.combine(startDate,startTime)
		endUtcTime = datetime.datetime.combine(endDate,endTime)


		if ((firstdatetime > startUtcTime) and (firstdatetime < endUtcTime)) or \
			((finaldatetime > startUtcTime) and (finaldatetime < endUtcTime)):
			return firstdatetime
		else:
			return None
		return firstdatetime

	def __setNextFileOffline(self):
		# if not(self.fileIndex < len(self.filenameList)):
		# 	print("No more Files!")
		# 	return 0

		filename = self.filenameList[self.fileIndex]
		filePointer = h5py.File(filename,'r+')
		self.filename = filename
		self.fp = filePointer

		print("Setting the file %d / %d: %s"%(self.fileIndex,self.number_of_files, self.filename))
		self.__setBlockList()
		self.__readData()

		self.blockIndex = 0
		self.fileIndex += 1

		return 1

	def __setBlockList(self):
		'''
		Selects the data within the times defined
		'''

		grp = self.fp['Data']
		thisUtcTime = grp['utctime'].value.astype(numpy.float64)[0] + self.timezone

		startUtcTime = (datetime.datetime.combine(self.startDate, self.startTime) - datetime.datetime(1970, 1, 1)).total_seconds()
		endUtcTime = (datetime.datetime.combine(self.endDate, self.endTime) - datetime.datetime(1970, 1, 1)).total_seconds()

		# List of blocks that are actually inside the time range, is an additional checking of time inside range of experiment
		self.blockList =  numpy.where(numpy.logical_and(thisUtcTime >= startUtcTime, thisUtcTime < endUtcTime))[0]
		self.blocks_in_File = len(self.blockList)

	def __readMetadata(self):
		splitted_filename = self.filenameList[0].split('/')
		doy = splitted_filename[-2]
		epoch_name = splitted_filename[-1]
		filename = self.filenameList[0].replace(doy,'').replace('//','/')
		filename = filename.replace(epoch_name,'M' + doy[1:] + '.hdf5')
		print 'Metadata de ParamReader en : ',filename

		fp = h5py.File(filename,'r')
		gp = fp['Metadata']

		dictMetadata = {}
		for name, dataset in gp.items():
			if name == 'array dimensions':
				listShapes = {}
				for shapes in gp[name]:
					listShapes[shapes[0]] = numpy.array([shapes[1],shapes[2],shapes[3],shapes[4]])#Reconstructing nDims matrix
			else:
				data = gp[name].value #Saving the real metadata in the dictMetadata attribute
				dictMetadata[name] = data

		self.listShapes = listShapes
		self.dictMetadata = dictMetadata

		fp.close()

	def __readData(self):
		grp = self.fp['Data']
		dictData = {}

		for name, data in grp.items():
			array = self.__setDataArray(data,self.listShapes[name], name)
			dictData[name] = array

		self.dictData = dictData

	def __setDataArray(self, dataset, shapes, name):
		nDims = shapes[0]
		nDim2 = shapes[1]	  #Dimension 2
		nDim1 = shapes[2]	  #Dimension 1, number of Points or Parameters
		nDim0 = shapes[3]	  #Dimension 0, number of samples or ranges

		#	One dimension
		if nDims == 1:
			arrayData = dataset.value.astype(numpy.float64)[0][self.blockList]
		#Two dimensions : just for HF HDF5 compress data Format
		elif nDims == 2:
			arrayData = numpy.zeros((self.blocks_in_File, nDim1, nDim0))

			for i in range(nDim1):
				if name == "CrossData": #Exception to the rule
					strMode = "phase" if i else "amplitude"
					if i > 2:
						raise ValueError("CrossData implemented wrong")
				else:
					strMode = 'channel' + str(i)
				data = dataset[strMode].value

				arrayData[:,i,:] = data[self.blockList,:]
		#three dimensions
		else:
			arrayData = numpy.zeros((self.blocks_in_File, nDim2, nDim1, nDim0))

			for i in range(nDim2):
				data = dataset['channel' + str(i)].value
				for b in self.blockList.tolist():
					arrayData[b:,i,:,:] = data[:,:,b]

		return arrayData

	def __setDataOut(self):
		for metaname, metadata in self.dictMetadata.items():
			setattr(self.dataOut, metaname, metadata)

		for name, data in self.dictData.items():
			setattr(self.dataOut, name, data[self.blockIndex])

	def __setHeaderDO(self):
		super(HFParamReader,self).setHeaderDO()
		del self.dataOut.flagLastFile
		self.dataOut.type = "Parameters"
		self.dataOut.startTime = self.startTime
		self.dataOut.endTime = self.endTime

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
				ext = None,
				all=0,
				timezone=0,
				online = False,
				delay = 60,
				walk = True, **kwargs):
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

		if kwargs.has_key('blocksPerFile'):
			self.blocksPerFile = kwargs['blocksPerFile']

		try:
			self.__inc_int= int(inc_int)
		except:
			print "The number of incoherent integration should be an integer"
		if self.__inc_int>6:
			raise ValueError, "The number of incoherent integration should be between 0 and 6"

		self.timezone= timezone #Alejandro: No se a que se refiere Jm con argumento es con Z mayuscula
		self.online= online
		self.all=all
		if not online:
			print "Searching files in offline mode..."
			self.searchFilesOffline(path,frequency,startDate, endDate, ext, startTime, endTime, walk)
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


		self.startDate = startDate
		self.endDate = endDate
		self.startTime = startTime
		self.endTime = endTime
		self.__readMetadata()

		self.number_of_files = len(self.filenameList)
		self.__setNextFileOffline()
		self.__setHeaderDO()

	def getData(self):
		if self.blockIndex==self.blocksPerFile:
			self.__setNextFileOffline()

		self.__setDataOut()
		self.dataOut.flagNoData = False
		self.blockIndex += 1
		print "Leyendo parametros de espectrograma N %d"%((self.fileIndex-1)*10+self.blockIndex)
		if (self.fileIndex == self.number_of_files) and (self.blockIndex == self.blocks_in_File):
			self.dataOut.flagNoData = True
			return 0
