'''

$Author: murco $
$Id: JROData.py 173 2012-11-20 15:06:21Z murco $
Modified by Alejandro, some methods and attributes were redefined or rewriten
'''

import copy
import numpy
import datetime

from jroheaderIO import SystemHeader, RadarControllerHeader
# pero si tengo schainpy
import cSchainNoise
#return cSchainNoise.hildebrand_sekhon(sortdata, navg)
#from cSchainNoise import hildebrand_sekhon

def getNumpyDtype(dataTypeCode):

	if dataTypeCode == 0:
		numpyDtype = numpy.dtype([('real','<i1'),('imag','<i1')])
	elif dataTypeCode == 1:
		numpyDtype = numpy.dtype([('real','<i2'),('imag','<i2')])
	elif dataTypeCode == 2:
		numpyDtype = numpy.dtype([('real','<i4'),('imag','<i4')])
	elif dataTypeCode == 3:
		numpyDtype = numpy.dtype([('real','<i8'),('imag','<i8')])
	elif dataTypeCode == 4:
		numpyDtype = numpy.dtype([('real','<f4'),('imag','<f4')])
	elif dataTypeCode == 5:
		numpyDtype = numpy.dtype([('real','<f8'),('imag','<f8')])
	else:
		raise ValueError, 'dataTypeCode was not defined'

	return numpyDtype

def getDataTypeCode(numpyDtype):

	if numpyDtype == numpy.dtype([('real','<i1'),('imag','<i1')]):
		datatype = 0
	elif numpyDtype == numpy.dtype([('real','<i2'),('imag','<i2')]):
		datatype = 1
	elif numpyDtype == numpy.dtype([('real','<i4'),('imag','<i4')]):
		datatype = 2
	elif numpyDtype == numpy.dtype([('real','<i8'),('imag','<i8')]):
		datatype = 3
	elif numpyDtype == numpy.dtype([('real','<f4'),('imag','<f4')]):
		datatype = 4
	elif numpyDtype == numpy.dtype([('real','<f8'),('imag','<f8')]):
		datatype = 5
	else:
		datatype = None

	return datatype

def hildebrand_sekhon(data, navg):

	data = data.copy()
	sortdata = numpy.sort(data,axis=None)
	'''
	lenOfData = len(sortdata)
	nums_min = lenOfData/10
	if (lenOfData/10) > 2:
		nums_min = lenOfData/10
	else:
		nums_min = 2
	sump = 0.
	sumq = 0.
	j = 0
	cont = 1
	while((cont==1)and(j<lenOfData)):
		sump += sortdata[j]
		sumq += sortdata[j]**2
		j += 1
		if j > nums_min:
			rtest = float(j)/(j-1) + 1.0/navg
			if ((sumq*j) > (rtest*sump**2)):
				j = j - 1
				sump  = sump - sortdata[j]
				sumq =  sumq - sortdata[j]**2
				cont = 0
	lnoise = sump /j
	stdv = numpy.sqrt((sumq - lnoise**2)/(j - 1))
	return lnoise
	'''
	return cSchainNoise.hildebrand_sekhon(sortdata, navg)

class Beam:
	def __init__(self):
		self.codeList = []
		self.azimuthList = []
		self.zenithList = []

class GenericData(object):
	flagNoData = True
	def __init__(self):
		raise ValueError, "This class has not been implemented"

	def copy(self, inputObj=None):

		if inputObj == None:
			return copy.deepcopy(self)

		for key in inputObj.__dict__.keys():
			self.__dict__[key] = inputObj.__dict__[key]

	def isEmpty(self):
		return self.flagNoData


class JROData(GenericData):
	#m_BasicHeader = BasicHeader()
	#m_ProcessingHeader = ProcessingHeader()

	systemHeaderObj = SystemHeader()

	radarControllerHeaderObj = RadarControllerHeader()

	#data = None

	type = None

	datatype = None #dtype but in string

	#dtype = None

	#nChannels = None

	#nHeights = None

	nProfiles = None

	heightList = None

	channelList = None

	flagTimeBlock = False

	useLocalTime = False

	utctime = None

	timeZone = None

	dstFlag = None

	errorCount = None

	blocksize = None

	nCode = None

	nBaud = None

	code = None

	flagDecodeData = False #asumo q la data no esta decodificada

	flagDeflipData = False #asumo q la data no esta sin flip

	flagShiftFFT = False

	#ippSeconds = None

	#timeInterval = None

	nCohInt = None

	noise = None

	windowOfFilter = 1

	#Speed of ligth
	C = 3e8

	frequency = 49.92e6

	realtime = False

	beacon_heiIndexList = None

	last_block = None

	blocknow = None

	azimuth = None

	zenith = None

	beam = Beam()

	profileIndex = None

	def __init__(self):
		raise ValueError, "This class has not been implemented"

	def getNoise(self):
		raise ValueError, "Not implemented"

	def getNChannels(self):
		return len(self.channelList)

	def getChannelIndexList(self):
		return range(self.nChannels)

	def getNHeights(self):
		return len(self.heightList)

	def getHeiRange(self, extrapoints=0):
		heis = self.heightList
		#deltah = self.heightList[1] - self.heightList[0]
		#heis.append(self.heightList[-1])
		return heis

	def getltctime(self):
		if self.useLocalTime:
			return self.utctime - 5*3600
		return self.utctime

	def getDatatime(self):
		datatimeValue = datetime.datetime.utcfromtimestamp(self.ltctime)
		return datatimeValue

	def getTimeRange(self):
		datatime = []
		datatime.append(self.ltctime)
		datatime.append(self.ltctime + self.timeInterval)
		datatime = numpy.array(datatime)
		return datatime

	def getFmax(self):
		PRF = 1./(self.ippSeconds * self.nCohInt*self.ippFactor) #AGREGARCOMENTARIO
		fmax = PRF/2.
		return fmax

	def getVmax(self):
		_lambda = self.C/self.frequency
		vmax = self.getFmax() * _lambda/2
		return vmax

	def get_ippSeconds(self):
		return self.radarControllerHeaderObj.ippSeconds

	def set_ippSeconds(self, ippSeconds):
		self.radarControllerHeaderObj.ippSeconds = ippSeconds

	def get_dtype(self):
		return getNumpyDtype(self.datatype)

	def set_dtype(self, numpyDtype):
		self.datatype = getDataTypeCode(numpyDtype)

	#def getTimeInterval(self):
		#raise IOError, "This method should be implemented inside each Class"

	nChannels = property(getNChannels, "I'm the 'nChannel' property.")
	channelIndexList = property(getChannelIndexList, "I'm the 'channelIndexList' property.")
	nHeights = property(getNHeights, "I'm the 'nHeights' property.")
	#noise = property(getNoise, "I'm the 'nHeights' property.")
	datatime = property(getDatatime, "I'm the 'datatime' property")
	ltctime = property(getltctime, "I'm the 'ltctime' property")
	ippSeconds = property(get_ippSeconds, set_ippSeconds)
	dtype = property(get_dtype, set_dtype)
	#timeInterval = property(getTimeInterval, "I'm the 'timeInterval' property")

class Voltage(JROData):

	#data es un numpy array de 2 dmensiones (canales, alturas)
	data = None

	def __init__(self):
		'''
		Constructor
		'''
		self.radarControllerHeaderObj = RadarControllerHeader()

		self.systemHeaderObj = SystemHeader()

		self.type = "Voltage"

		self.data = None

		self.nProfiles = None

		self.heightList = None

		self.channelList = None

		self.flagNoData = True

		self.flagTimeBlock = False

		self.utctime = None

		self.timeZone = None

		self.dstFlag = None

		self.errorCount = None

		self.nCohInt = None

		self.blocksize = None

		self.flagDecodeData = False #asumo q la data no esta decodificada

		self.flagDeflipData = False #asumo q la data no esta sin flip

		self.flagShiftFFT = False

		self.flagDataAsBlock = False	#Asumo que la data es leida perfil a perfil

		self.profileIndex = 0

	def getNoisebyHildebrand(self):
		"""
		Determino el nivel de ruido usando el metodo Hildebrand-Sekhon

		Return:
			noiselevel
		"""

		for channel in range(self.nChannels):
			daux = self.data_spc[channel,:,:]
			self.noise[channel] = hildebrand_sekhon(daux, self.nCohInt)

		return self.noise

	def getNoise(self, type = 1):

		self.noise = numpy.zeros(self.nChannels)

		if type == 1:
			noise = self.getNoisebyHildebrand()

		return 10*numpy.log10(noise)

	def getTimeInterval(self):

		timeInterval = self.ippSeconds * self.nCohInt

		return timeInterval

	noise = property(getNoise, "I'm the 'nHeights' property.")
	timeInterval = property(getTimeInterval, "I'm the 'timeInterval' property")

class Spectra(JROData):

	#data es un numpy array de 2 dmensiones (canales, perfiles, alturas)
	data_spc = None

	#data es un numpy array de 2 dmensiones (canales, pares, alturas)
	data_cspc = None

	#data es un numpy array de 2 dmensiones (canales, alturas)
	data_dc = None

	nFFTPoints = None

	pairsList = None

	nIncohInt = None

	wavelength = None #Necesario para cacular el rango de velocidad desde la frecuencia

	nCohInt = None #se requiere para determinar el valor de timeInterval

	ippFactor = None

	profileIndex = 0

	def __init__(self):
		'''
		Constructor
		'''

		self.radarControllerHeaderObj = RadarControllerHeader()

		self.systemHeaderObj = SystemHeader()

		self.type = "Spectra"

		self.nProfiles = None

		self.heightList = None

		self.channelList = None

		self.pairsList = None

		self.flagNoData = True

		self.flagTimeBlock = False

		self.utctime = None

		self.nCohInt = None

		self.nIncohInt = None

		self.blocksize = None

		self.nFFTPoints = None

		self.wavelength = None

		self.flagDecodeData = False #asumo q la data no esta decodificada

		self.flagDeflipData = False #asumo q la data no esta sin flip

		self.flagShiftFFT = False

		self.ippFactor = 1

		self.beacon_heiIndexList = []

		self.noise_estimation = None

	def getNoisebyHildebrand(self):
		"""
		Determino el nivel de ruido usando el metodo Hildebrand-Sekhon

		Return:
			noiselevel
		"""
		noise = numpy.zeros(self.nChannels)
		for channel in range(self.nChannels):
			daux = self.data_spc[channel,:,:]
			noise[channel] = hildebrand_sekhon(daux, self.nIncohInt)
		return noise

	def getNoisebyHeights(self):
		"""
		Determino el nivel de ruido usando el metodo Hildebrand-Sekhon
		Return:
			noiselevel pero Slice or height
		"""
		noise = numpy.zeros((self.nChannels,len(self.heightList)))
		for channel in range(self.nChannels):
			daux = self.data_spc[channel,:,:]
			for height in range(daux.shape[1]):
				noise[channel][height] = hildebrand_sekhon(daux[:,height], self.nCohInt)

		return noise

	def getNoise(self, mode = None):
		if self.noise_estimation != None:
			return self.noise_estimation #this was estimated by getNoise Operation defined in jroproc_spectra.py
		else:
			if mode == 1:
				noise = self.getNoisebyHildebrand()
			elif mode == 2:
				noise = self.getNoisebyHeights()
			else:
				message = "noiseMode es %s,deberia tomar solo los valores o 1 o 2."%(mode)
				raise ValueError, message
			return noise


	def getFreqRange(self, extrapoints=0):

		deltafreq = 2*self.getFmax() / (self.nFFTPoints)
		#print deltafreq,'Deltafreq TEST0'
		freqrange = deltafreq*(numpy.arange(self.nFFTPoints+extrapoints)-self.nFFTPoints/2.) - (deltafreq/2)*extrapoints

		return freqrange

	def getVelRange(self, extrapoints=0):
		#NO puede ser
		deltav = 2*self.getVmax() / (self.nFFTPoints)# agregar comentario
		velrange = deltav*(numpy.arange(self.nFFTPoints+extrapoints)-self.nFFTPoints/2.) - (deltav/2)*extrapoints

		return velrange

	def getNPairs(self):
		return len(self.pairsList)

	def getPairsIndexList(self):

		return range(self.nPairs)

	def getNormFactor(self):
		pwcode = 1
		if self.flagDecodeData:
			pwcode = numpy.sum(self.code[0]**2)
		#normFactor = min(self.nFFTPoints,self.nProfiles)*self.nIncohInt*self.nCohInt*pwcode*self.windowOfFilter
		normFactor = int(self.nProfiles*self.nIncohInt*self.nCohInt*pwcode*self.windowOfFilter)
		#normFactor = 1
		return normFactor

	def getFlagCspc(self):

		if self.data_cspc == None:
			return True

		return False

	def getFlagDc(self):

		if self.data_dc == None:
			return True

		return False

	def getTimeInterval(self):

		timeInterval = self.ippSeconds * self.nCohInt * self.nIncohInt * self.nProfiles

		return timeInterval

	nPairs = property(getNPairs, "I'm the 'nPairs' property.")
	pairsIndexList = property(getPairsIndexList, "I'm the 'pairsIndexList' property.")
	normFactor = property(getNormFactor, "I'm the 'getNormFactor' property.")
	flag_cspc = property(getFlagCspc)
	flag_dc = property(getFlagDc)
	noise = property(getNoise, "I'm the 'nHeights' property.")
	timeInterval = property(getTimeInterval, "I'm the 'timeInterval' property")

class SpectraHeis(Spectra):

	data_spc = None

	data_cspc = None

	data_dc = None

	nFFTPoints = None

	#nPairs = None

	pairsList = None

	nIncohInt = None

	def __init__(self):

		self.radarControllerHeaderObj = RadarControllerHeader()

		self.systemHeaderObj = SystemHeader()

		self.type = "SpectraHeis"

		#self.dtype = None

		#self.nChannels = 0

		#self.nHeights = 0

		self.nProfiles = None

		self.heightList = None

		self.channelList = None

		#self.channelIndexList = None

		self.flagNoData = True

		self.flagTimeBlock = False

		#self.nPairs = 0

		self.utctime = None

		self.blocksize = None

		self.profileIndex = 0

	def getNormFactor(self):
		pwcode = 1
		if self.flagDecodeData:
			pwcode = numpy.sum(self.code[0]**2)

		normFactor = self.nIncohInt*self.nCohInt*pwcode

		return normFactor

	def getTimeInterval(self):

		timeInterval = self.ippSeconds * self.nCohInt * self.nIncohInt

		return timeInterval

	normFactor = property(getNormFactor, "I'm the 'getNormFactor' property.")
	timeInterval = property(getTimeInterval, "I'm the 'timeInterval' property")

class Fits:

	heightList = None

	channelList = None

	flagNoData = True

	flagTimeBlock = False

	useLocalTime = False

	utctime = None

	timeZone = None

	#ippSeconds = None

	#timeInterval = None

	nCohInt = None

	nIncohInt = None

	noise = None

	windowOfFilter = 1

	#Speed of ligth
	C = 3e8

	frequency = 49.92e6

	realtime = False


	def __init__(self):

		self.type = "Fits"

		self.nProfiles = None

		self.heightList = None

		self.channelList = None

		#self.channelIndexList = None

		self.flagNoData = True

		self.utctime = None

		self.nCohInt = None

		self.nIncohInt = None

		self.useLocalTime = True

		self.profileIndex = 0

		#self.utctime = None
		#self.timeZone = None
		#self.ltctime = None
		#self.timeInterval = None
		#self.header = None
		#self.data_header = None
		#self.data = None
		#self.datatime = None
		#self.flagNoData = False
		#self.expName = ''
		#self.nChannels = None
		#self.nSamples = None
		#self.dataBlocksPerFile = None
		#self.comments = ''



	def getltctime(self):

		if self.useLocalTime:
			#print self.utctime,self.timeZone
			return self.utctime - self.timeZone*60

		return self.utctime

	def getDatatime(self):

		datatime = datetime.datetime.utcfromtimestamp(self.ltctime)
		return datatime

	def getTimeRange(self):

		datatime = []

		datatime.append(self.ltctime)
		datatime.append(self.ltctime + self.timeInterval)

		datatime = numpy.array(datatime)

		return datatime

	def getHeiRange(self):

		heis = self.heightList

		return heis

	def isEmpty(self):

		return self.flagNoData

	def getNHeights(self):

		return len(self.heightList)

	def getNChannels(self):

		return len(self.channelList)

	def getChannelIndexList(self):

		return range(self.nChannels)

	def getNoise(self, type = 1):

		self.noise = numpy.zeros(self.nChannels)

		if type == 1:
			noise = self.getNoisebyHildebrand()

		if type == 2:
			noise = self.getNoisebySort()

		if type == 3:
			noise = self.getNoisebyWindow()

		return noise

	def getTimeInterval(self):

		raise ValueError, "This method is not implemented yet"

	datatime = property(getDatatime, "I'm the 'datatime' property")
	nHeights = property(getNHeights, "I'm the 'nHeights' property.")
	nChannels = property(getNChannels, "I'm the 'nChannel' property.")
	channelIndexList = property(getChannelIndexList, "I'm the 'channelIndexList' property.")
	noise = property(getNoise, "I'm the 'nHeights' property.")
	datatime = property(getDatatime, "I'm the 'datatime' property")
	ltctime = property(getltctime, "I'm the 'ltctime' property")
	timeInterval = property(getTimeInterval, "I'm the 'timeInterval' property")

class Correlation(JROData):

	noise = None

	SNR = None

	pairsAutoCorr = None	#Pairs of Autocorrelation

	#--------------------------------------------------

	data_corr = None

	data_volt = None

	lagT = None # each element value is a profileIndex

	lagR = None # each element value is in km

	pairsList = None

	calculateVelocity = None

	nPoints = None

	nAvg = None

	bufferSize = None

	def __init__(self):
		'''
		Constructor
		'''
		self.radarControllerHeaderObj = RadarControllerHeader()

		self.systemHeaderObj = SystemHeader()

		self.type = "Correlation"

		self.data = None

		self.dtype = None

		self.nProfiles = None

		self.heightList = None

		self.channelList = None

		self.flagNoData = True

		self.flagTimeBlock = False

		self.utctime = None

		self.timeZone = None

		self.dstFlag = None

		self.errorCount = None

		self.blocksize = None

		self.flagDecodeData = False #asumo q la data no esta decodificada

		self.flagDeflipData = False #asumo q la data no esta sin flip

		self.pairsList = None

		self.nPoints = None

	def getLagTRange(self, extrapoints=0):

		lagTRange = self.lagT
		diff = lagTRange[1] - lagTRange[0]
		extra = numpy.arange(1,extrapoints + 1)*diff + lagTRange[-1]
		lagTRange = numpy.hstack((lagTRange, extra))

		return lagTRange

	def getLagRRange(self, extrapoints=0):

		return self.lagR

	def getPairsList(self):

		return self.pairsList

	def getCalculateVelocity(self):

		return self.calculateVelocity

	def getNPoints(self):

		return self.nPoints

	def getNAvg(self):

		return self.nAvg

	def getBufferSize(self):

		return self.bufferSize

	def getPairsAutoCorr(self):
		pairsList = self.pairsList
		pairsAutoCorr = numpy.zeros(self.nChannels, dtype = 'int')*numpy.nan

		for l in range(len(pairsList)):
			firstChannel = pairsList[l][0]
			secondChannel = pairsList[l][1]

			#Obteniendo pares de Autocorrelacion
			if firstChannel == secondChannel:
				pairsAutoCorr[firstChannel] = int(l)

		pairsAutoCorr = pairsAutoCorr.astype(int)

		return pairsAutoCorr

	def getNoise(self, mode = 2):

		indR = numpy.where(self.lagR == 0)[0][0]
		indT = numpy.where(self.lagT == 0)[0][0]

		jspectra0 = self.data_corr[:,:,indR,:]
		jspectra = copy.copy(jspectra0)

		num_chan = jspectra.shape[0]
		num_hei = jspectra.shape[2]

		freq_dc = jspectra.shape[1]/2
		ind_vel = numpy.array([-2,-1,1,2]) + freq_dc

		if ind_vel[0]<0:
			ind_vel[range(0,1)] = ind_vel[range(0,1)] + self.num_prof

		if mode == 1:
			jspectra[:,freq_dc,:] = (jspectra[:,ind_vel[1],:] + jspectra[:,ind_vel[2],:])/2 #CORRECCION

		if mode == 2:

			vel = numpy.array([-2,-1,1,2])
			xx = numpy.zeros([4,4])

			for fil in range(4):
				xx[fil,:] = vel[fil]**numpy.asarray(range(4))

			xx_inv = numpy.linalg.inv(xx)
			xx_aux = xx_inv[0,:]

			for ich in range(num_chan):
				yy = jspectra[ich,ind_vel,:]
				jspectra[ich,freq_dc,:] = numpy.dot(xx_aux,yy)

				junkid = jspectra[ich,freq_dc,:]<=0
				cjunkid = sum(junkid)

				if cjunkid.any():
					jspectra[ich,freq_dc,junkid.nonzero()] = (jspectra[ich,ind_vel[1],junkid] + jspectra[ich,ind_vel[2],junkid])/2

		noise = jspectra0[:,freq_dc,:] - jspectra[:,freq_dc,:]

		return noise

	#pairsList = property(getPairsList, "I'm the 'pairsList' property.")
	#nPoints = property(getNPoints, "I'm the 'nPoints' property.")
	calculateVelocity = property(getCalculateVelocity, "I'm the 'calculateVelocity' property.")
	nAvg = property(getNAvg, "I'm the 'nAvg' property.")
	bufferSize = property(getBufferSize, "I'm the 'bufferSize' property.")


class Parameters(JROData): #parameter hereda de spectra

	#Information from previous data

	inputUnit = None		#Type of data to be processed

	operation = None		#Type of operation to parametrize

	normFactor = None	   #Normalization Factor

	groupList = None		#List of Pairs, Groups, etc

	#Parameters

	data_param = None	   #Parameters obtained

	data_pre = None		 #Data Pre Parametrization

	data_SNR = None		 #Signal to Noise Ratio

	heightRange = None	  #Heights

	abscissaRange = None	#Abscissa, can be velocities, lags or time

	noise = None			#Noise Potency

	utctimeInit = None	  #Initial UTC time

	paramInterval = None	#Time interval to calculate Parameters in seconds

	#Fitting

	data_error = None	   #Error of the estimation

	constants = None

	library = None

	#Output signal

	outputInterval = None	 #Time interval to calculate output signal in seconds


	def __init__(self):
		'''
		Constructor
		'''
		self.radarControllerHeaderObj = RadarControllerHeader()

		self.systemHeaderObj = SystemHeader()

		self.type = "Parameters"
		#TODO esto no deberia venir harcoded ... 2019 arreglar.

		self.useLocalTime = True

	def getTimeRange1(self):

		datatime = []
		datatime.append(self.ltctime, )
		datatime.append(self.ltctime + self.outputInterval - 1)

		datatime = numpy.array(datatime)

		return datatime

	def getVelRange(self, extrapoints=0):
		#deltafreq = 2*self.getFmax() / (self.nFFTPoints)
		#print deltafreq,'Deltafreq TEST1'
		deltav = 2*self.getVmax() / (self.nFFTPoints)# agregar comentario

		velrange = deltav*(numpy.arange(self.nFFTPoints+extrapoints)-self.nFFTPoints/2.) - (deltav/2)*extrapoints

		return velrange


class Image(JROData):

	#data es un numpy array de 2 dmensiones (canales, perfiles, alturas)
	data_spc = None

	data_img = None

	data_img_genaro=None

	#data_time_genaro = None			 # User1 was here

	nFFTPoints = None

	#nPairs = None

	pairsList = None

	nIncohInt = None

	wavelength = None #Necesario para cacular el rango de velocidad desde la frecuencia

	nCohInt = None #se requiere para determinar el valor de timeInterval

	ippFactor = None



	profileIndex = 0

	plotting = "image"


	def __init__(self):

		self.useLocalTime = True

		self.radarControllerHeaderObj = RadarControllerHeader()

		self.systemHeaderObj = SystemHeader()

		self.type = "Image"

		self.nProfiles = None

		self.heightList = None

		self.channelList = None

		self.flagNoData = True

		self.flagDiscontinuousBlock = False

		self.utctime = None

		self.nCohInt = None

		self.nIncohInt = None

		self.blocksize = None

		self.nFFTPoints = None

		self.wavelength = None

		self.flagDecodeData = False #asumo q la data no esta decodificada

		self.flagDeflipData = False #asumo q la data no esta sin flip

		self.flagShiftFFT = False

		self.ippFactor = 1

		#self.noise = None

		self.beacon_heiIndexList = []

		self.noise_estimation = None

		#def getTimeInterval(self):
			 #timeInterval = self.ippSeconds * self.nCohInt
			 #return timeInterval



	def getTimeInterval(self):
		timeInterval = self.ippSeconds * self.nCohInt * self.nIncohInt * self.nProfiles
		return timeInterval

	def setValue(self, value):
		raise ValueError, "This property should not be initialized"

	timeInterval = property(getTimeInterval, setValue, "I'm the 'timeInterval' property")
