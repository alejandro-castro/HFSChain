import numpy

from jroproc_base import ProcessingUnit, Operation
from model.data.jrodata import Voltage


class VoltageProc(ProcessingUnit):

	def __init__(self):
		ProcessingUnit.__init__(self)
		#self.objectDict = {}
		self.dataOut = Voltage()
		self.flip = 1

	def run(self):
		if self.dataIn.type == 'AMISR':
			self.__updateObjFromAmisrInput()

		if self.dataIn.type == 'Voltage':
			self.dataOut.copy(self.dataIn)

		#self.dataOut.copy(self.dataIn)

	def __updateObjFromAmisrInput(self):

		self.dataOut.timeZone = self.dataIn.timeZone
		self.dataOut.dstFlag = self.dataIn.dstFlag
		self.dataOut.errorCount = self.dataIn.errorCount
		self.dataOut.useLocalTime = self.dataIn.useLocalTime

		self.dataOut.flagNoData = self.dataIn.flagNoData
		self.dataOut.data = self.dataIn.data
		self.dataOut.utctime = self.dataIn.utctime
		self.dataOut.channelList = self.dataIn.channelList
		self.dataOut.timeInterval = self.dataIn.timeInterval
		self.dataOut.heightList = self.dataIn.heightList
		self.dataOut.nProfiles = self.dataIn.nProfiles

		self.dataOut.nCohInt = self.dataIn.nCohInt
		self.dataOut.ippSeconds = self.dataIn.ippSeconds
		self.dataOut.frequency = self.dataIn.frequency

		self.dataOut.azimuth = self.dataIn.azimuth
		self.dataOut.zenith = self.dataIn.zenith

		self.dataOut.beam.codeList = self.dataIn.beam.codeList
		self.dataOut.beam.azimuthList = self.dataIn.beam.azimuthList
		self.dataOut.beam.zenithList = self.dataIn.beam.zenithList
#
#		pass#
#
#	def init(self):
#
#
#		if self.dataIn.type == 'AMISR':
#			self.__updateObjFromAmisrInput()
#
#		if self.dataIn.type == 'Voltage':
#			self.dataOut.copy(self.dataIn)
#		# No necesita copiar en cada init() los atributos de dataIn
#		# la copia deberia hacerse por cada nuevo bloque de datos

	def selectChannels(self, channelList):

		channelIndexList = []

		for channel in channelList:
			index = self.dataOut.channelList.index(channel)
			channelIndexList.append(index)

		self.selectChannelsByIndex(channelIndexList)

	def selectChannelsByIndex(self, channelIndexList):
		"""
		Selecciona un bloque de datos en base a canales segun el channelIndexList

		Input:
			channelIndexList	:	lista sencilla de canales a seleccionar por ej. [2,3,7]

		Affected:
			self.dataOut.data
			self.dataOut.channelIndexList
			self.dataOut.nChannels
			self.dataOut.m_ProcessingHeader.totalSpectra
			self.dataOut.systemHeaderObj.numChannels
			self.dataOut.m_ProcessingHeader.blockSize

		Return:
			None
		"""

		for channelIndex in channelIndexList:
			if channelIndex not in self.dataOut.channelIndexList:
				print channelIndexList
				raise ValueError, "The value %d in channelIndexList is not valid" %channelIndex

#		 nChannels = len(channelIndexList)
		if self.dataOut.flagDataAsBlock:
			"""
			Si la data es obtenida por bloques, dimension = [nChannels, nProfiles, nHeis]
			"""
			data = self.dataOut.data[channelIndexList,:,:]
		else:
			data = self.dataOut.data[channelIndexList,:]

		self.dataOut.data = data
		self.dataOut.channelList = [self.dataOut.channelList[i] for i in channelIndexList]
#		self.dataOut.nChannels = nChannels

		return 1

	def selectHeights(self, minHei=None, maxHei=None):
		"""
		Selecciona un bloque de datos en base a un grupo de valores de alturas segun el rango
		minHei <= height <= maxHei

		Input:
			minHei	:	valor minimo de altura a considerar
			maxHei	:	valor maximo de altura a considerar

		Affected:
			Indirectamente son cambiados varios valores a travez del metodo selectHeightsByIndex

		Return:
			1 si el metodo se ejecuto con exito caso contrario devuelve 0
		"""

		if minHei == None:
			minHei = self.dataOut.heightList[0]

		if maxHei == None:
			maxHei = self.dataOut.heightList[-1]

		if (minHei < self.dataOut.heightList[0]) or (minHei > maxHei):
			raise ValueError, "some value in (%d,%d) is not valid" % (minHei, maxHei)


		if (maxHei > self.dataOut.heightList[-1]):
			maxHei = self.dataOut.heightList[-1]
#			raise ValueError, "some value in (%d,%d) is not valid" % (minHei, maxHei)

		minIndex = 0
		maxIndex = 0
		heights = self.dataOut.heightList

		inda = numpy.where(heights >= minHei)
		indb = numpy.where(heights <= maxHei)

		try:
			minIndex = inda[0][0]
		except:
			minIndex = 0

		try:
			maxIndex = indb[0][-1]
		except:
			maxIndex = len(heights)

		self.selectHeightsByIndex(minIndex, maxIndex)

		return 1


	def selectHeightsByIndex(self, minIndex, maxIndex):
		"""
		Selecciona un bloque de datos en base a un grupo indices de alturas segun el rango
		minIndex <= index <= maxIndex

		Input:
			minIndex	:	valor de indice minimo de altura a considerar
			maxIndex	:	valor de indice maximo de altura a considerar

		Affected:
			self.dataOut.data
			self.dataOut.heightList

		Return:
			1 si el metodo se ejecuto con exito caso contrario devuelve 0
		"""

		if (minIndex < 0) or (minIndex > maxIndex):
			raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)

		if (maxIndex >= self.dataOut.nHeights):
			maxIndex = self.dataOut.nHeights
#			raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)

#		 nHeights = maxIndex - minIndex + 1

		#voltage
		if self.dataOut.flagDataAsBlock:
			"""
			Si la data es obtenida por bloques, dimension = [nChannels, nProfiles, nHeis]
			"""
			data = self.dataOut.data[:,minIndex:maxIndex,:]
		else:
			data = self.dataOut.data[:,minIndex:maxIndex]

#		 firstHeight = self.dataOut.heightList[minIndex]

		self.dataOut.data = data
		self.dataOut.heightList = self.dataOut.heightList[minIndex:maxIndex]

		return 1


	def filterByHeights(self, window, axis=1):

		deltaHeight = self.dataOut.heightList[1] - self.dataOut.heightList[0]

		if window == None:
			window = (self.dataOut.radarControllerHeaderObj.txA/self.dataOut.radarControllerHeaderObj.nBaud) / deltaHeight

		newdelta = deltaHeight * window
		r = self.dataOut.nHeights % window

		if self.dataOut.flagDataAsBlock:
			"""
			Si la data es obtenida por bloques, dimension = [nChannels, nProfiles, nHeis]
			"""
			buffer = self.dataOut.data[:, :, 0:self.dataOut.nHeights-r]
			buffer = buffer.reshape(self.dataOut.nChannels,self.dataOut.nHeights,self.dataOut.nHeights/window,window)
			buffer = numpy.sum(buffer,3)

		else:
			buffer = self.dataOut.data[:,0:self.dataOut.nHeights-r]
			buffer = buffer.reshape(self.dataOut.nChannels,self.dataOut.nHeights/window,window)
			buffer = numpy.sum(buffer,2)

		self.dataOut.data = buffer.copy()
		self.dataOut.heightList = numpy.arange(self.dataOut.heightList[0],newdelta*(self.dataOut.nHeights-r)/window,newdelta)
		self.dataOut.windowOfFilter = window

		return 1

	def deFlip(self, channelList = []):

		data = self.dataOut.data.copy()

		if self.dataOut.flagDataAsBlock:
			flip = self.flip
			profileList = range(self.dataOut.nProfiles)

			if channelList == []:
				for thisProfile in profileList:
					data[:,thisProfile,:] = data[:,thisProfile,:]*flip
					flip *= -1.0
			else:
				for thisChannel in channelList:
					for thisProfile in profileList:
						data[thisChannel,thisProfile,:] = data[thisChannel,thisProfile,:]*flip
						flip *= -1.0

			self.flip = flip

		else:
			if channelList == []:
				data[:,:] = data[:,:]*self.flip
			else:
				for thisChannel in channelList:
					data[thisChannel,:] = data[thisChannel,:]*self.flip

			self.flip *= -1.

		self.dataOut.data = data


	def setRadarFrequency(self, frequency=None):
		if frequency != None:
			self.dataOut.frequency = frequency

		return 1


class CohInt(Operation):

	isConfig = False

	__profIndex = 0
	__withOverapping  = False

	__byTime = False
	__initime = None
	__lastdatatime = None
	__integrationtime = None

	__buffer = None

	__dataReady = False

	n = None


	def __init__(self):

		Operation.__init__(self)

#		 self.isConfig = False

	def setup(self, n=None, timeInterval=None, overlapping=False, byblock=False):
		"""
		Set the parameters of the integration class.

		Inputs:

			n		:	Number of coherent integrations
			timeInterval   :	Time of integration. If the parameter "n" is selected this one does not work
			overlapping	:

		"""

		self.__initime = None
		self.__lastdatatime = 0
		self.__buffer = None
		self.__dataReady = False
		self.byblock = byblock

		if n == None and timeInterval == None:
			raise ValueError, "n or timeInterval should be specified ..."

		if n != None:
			self.n = n
			self.__byTime = False
		else:
			self.__integrationtime = timeInterval #* 60. #if (type(timeInterval)!=integer) -> change this line
			self.n = 9999
			self.__byTime = True

		if overlapping:
			self.__withOverapping = True
			self.__buffer = None
		else:
			self.__withOverapping = False
			self.__buffer = 0

		self.__profIndex = 0

	def putData(self, data):

		"""
		Add a profile to the __buffer and increase in one the __profileIndex

		"""

		if not self.__withOverapping:
			self.__buffer += data.copy()
			self.__profIndex += 1
			return

		#Overlapping data
		nChannels, nHeis = data.shape
		data = numpy.reshape(data, (1, nChannels, nHeis))

		#If the buffer is empty then it takes the data value
		if self.__buffer == None:
			self.__buffer = data
			self.__profIndex += 1
			return

		#If the buffer length is lower than n then stakcing the data value
		if self.__profIndex < self.n:
			self.__buffer = numpy.vstack((self.__buffer, data))
			self.__profIndex += 1
			return

		#If the buffer length is equal to n then replacing the last buffer value with the data value
		self.__buffer = numpy.roll(self.__buffer, -1, axis=0)
		self.__buffer[self.n-1] = data
		self.__profIndex = self.n
		return


	def pushData(self):
		"""
		Return the sum of the last profiles and the profiles used in the sum.

		Affected:

		self.__profileIndex

		"""

		if not self.__withOverapping:
			data = self.__buffer
			n = self.__profIndex

			self.__buffer = 0
			self.__profIndex = 0

			return data, n

		#Integration with Overlapping
		data = numpy.sum(self.__buffer, axis=0)
		n = self.__profIndex

		return data, n

	def byProfiles(self, data):

		self.__dataReady = False
		avgdata = None
#		 n = None

		self.putData(data)

		if self.__profIndex == self.n:

			avgdata, n = self.pushData()
			self.__dataReady = True

		return avgdata

	def byTime(self, data, datatime):

		self.__dataReady = False
		avgdata = None
		n = None

		self.putData(data)

		if (datatime - self.__initime) >= self.__integrationtime:
			avgdata, n = self.pushData()
			self.n = n
			self.__dataReady = True

		return avgdata

	def integrate(self, data, datatime=None):

		if self.__initime == None:
			self.__initime = datatime

		if self.__byTime:
			avgdata = self.byTime(data, datatime)
		else:
			avgdata = self.byProfiles(data)


		self.__lastdatatime = datatime

		if avgdata == None:
			return None, None

		avgdatatime = self.__initime

		deltatime = datatime -self.__lastdatatime

		if not self.__withOverapping:
			self.__initime = datatime
		else:
			self.__initime += deltatime

		return avgdata, avgdatatime

	def integrateByBlock(self, dataOut):

		times = int(dataOut.data.shape[1]/self.n)
		avgdata = numpy.zeros((dataOut.nChannels, times, dataOut.nHeights), dtype=numpy.complex)

		id_min = 0
		id_max = self.n

		for i in range(times):
			junk = dataOut.data[:,id_min:id_max,:]
			avgdata[:,i,:] = junk.sum(axis=1)
			id_min += self.n
			id_max += self.n

		timeInterval = dataOut.ippSeconds*self.n
		avgdatatime = (times - 1) * timeInterval + dataOut.utctime
		self.__dataReady = True
		return avgdata, avgdatatime

	def run(self, dataOut, **kwargs):

		if not self.isConfig:
			self.setup(**kwargs)
			self.isConfig = True

		if dataOut.flagDataAsBlock:
			"""
			Si la data es leida por bloques, dimension = [nChannels, nProfiles, nHeis]
			"""
			avgdata, avgdatatime = self.integrateByBlock(dataOut)
		else:
			avgdata, avgdatatime = self.integrate(dataOut.data, dataOut.utctime)

#		dataOut.timeInterval *= n
		dataOut.flagNoData = True

		if self.__dataReady:
			dataOut.data = avgdata
			dataOut.nCohInt *= self.n
			dataOut.utctime = avgdatatime
#			 dataOut.timeInterval = dataOut.ippSeconds * dataOut.nCohInt
			dataOut.flagNoData = False

class Decoder(Operation):

	isConfig = False
	__profIndex = 0

	code = None

	nCode = None
	nBaud = None


	def __init__(self):

		Operation.__init__(self)

		self.times = None
		self.osamp = None
#		 self.__setValues = False
		self.isConfig = False

	def setup(self, code, osamp, dataOut):

		self.__profIndex = 0

		self.code = code

		self.nCode = len(code)
		self.nBaud = len(code[0])

		if (osamp != None) and (osamp >1):
			self.osamp = osamp
			self.code = numpy.repeat(code, repeats=self.osamp, axis=1)
			self.nBaud = self.nBaud*self.osamp

		self.__nChannels = dataOut.nChannels
		self.__nProfiles = dataOut.nProfiles
		self.__nHeis = dataOut.nHeights

		if dataOut.flagDataAsBlock:

			self.ndatadec = self.__nHeis #- self.nBaud + 1

			self.datadecTime = numpy.zeros((self.__nChannels, self.__nProfiles, self.ndatadec), dtype=numpy.complex)

		else:

			__codeBuffer = numpy.zeros((self.nCode, self.__nHeis), dtype=numpy.complex)

			__codeBuffer[:,0:self.nBaud] = self.code

			self.fft_code = numpy.conj(numpy.fft.fft(__codeBuffer, axis=1))

			self.ndatadec = self.__nHeis #- self.nBaud + 1

			self.datadecTime = numpy.zeros((self.__nChannels, self.ndatadec), dtype=numpy.complex)

	def convolutionInFreq(self, data):

		fft_code = self.fft_code[self.__profIndex].reshape(1,-1)

		fft_data = numpy.fft.fft(data, axis=1)

		conv = fft_data*fft_code

		data = numpy.fft.ifft(conv,axis=1)

		datadec = data#[:,:]

		return datadec

	def convolutionInFreqOpt(self, data):

		fft_code = self.fft_code[self.__profIndex].reshape(1,-1)

		data = cfunctions.decoder(fft_code, data)

		datadec = data#[:,:]

		return datadec

	def convolutionInTime(self, data):

		code = self.code[self.__profIndex]

		for i in range(self.__nChannels):
			self.datadecTime[i,:] = numpy.correlate(data[i,:], code, mode='same')

		return self.datadecTime

	def convolutionByBlockInTime(self, data):

		repetitions = self.__nProfiles / self.nCode

		junk = numpy.lib.stride_tricks.as_strided(self.code, (repetitions, self.code.size), (0, self.code.itemsize))
		junk = junk.flatten()
		code_block = numpy.reshape(junk, (self.nCode*repetitions, self.nBaud))

		for i in range(self.__nChannels):
			for j in range(self.__nProfiles):
				self.datadecTime[i,j,:] = numpy.correlate(data[i,j,:], code_block[j,:], mode='same')

		return self.datadecTime

	def run(self, dataOut, code=None, nCode=None, nBaud=None, mode = 0, times=None, osamp=None):

		if not self.isConfig:

			if code == None:
				code = dataOut.code
			else:
				code = numpy.array(code).reshape(nCode,nBaud)

			self.setup(code, osamp, dataOut)

			self.isConfig = True

		if dataOut.flagDataAsBlock:
			"""
			Decoding when data have been read as block,
			"""
			datadec = self.convolutionByBlockInTime(dataOut.data)

		else:
			"""
			Decoding when data have been read profile by profile
			"""
			if mode == 0:
				datadec = self.convolutionInTime(dataOut.data)

			if mode == 1:
				datadec = self.convolutionInFreq(dataOut.data)

			if mode == 2:
				datadec = self.convolutionInFreqOpt(dataOut.data)

		dataOut.code = self.code
		dataOut.nCode = self.nCode
		dataOut.nBaud = self.nBaud
		dataOut.radarControllerHeaderObj.code = self.code
		dataOut.radarControllerHeaderObj.nCode = self.nCode
		dataOut.radarControllerHeaderObj.nBaud = self.nBaud

		dataOut.data = datadec

		dataOut.heightList = dataOut.heightList[0:self.ndatadec]

		dataOut.flagDecodeData = True #asumo q la data esta decodificada

		if self.__profIndex == self.nCode-1:
			self.__profIndex = 0
			return 1

		self.__profIndex += 1

		return 1
#		dataOut.flagDeflipData = True #asumo q la data no esta sin flip


class ProfileConcat(Operation):

	isConfig = False
	buffer = None

	def __init__(self):

		Operation.__init__(self)
		self.profileIndex = 0

	def reset(self):
		self.buffer = numpy.zeros_like(self.buffer)
		self.start_index = 0
		self.times = 1

	def setup(self, data, m, n=1):
		self.buffer = numpy.zeros((data.shape[0],data.shape[1]*m),dtype=type(data[0,0]))
		self.nHeights = data.nHeights
		self.start_index = 0
		self.times = 1

	def concat(self, data):

		self.buffer[:,self.start_index:self.profiles*self.times] = data.copy()
		self.start_index = self.start_index + self.nHeights

	def run(self, dataOut, m):

		dataOut.flagNoData = True

		if not self.isConfig:
			self.setup(dataOut.data, m, 1)
			self.isConfig = True

		if dataOut.flagDataAsBlock:

			raise ValueError, "ProfileConcat can only be used when voltage have been read profile by profile, getBlock = False"

		else:
			self.concat(dataOut.data)
			self.times += 1
			if self.times > m:
				dataOut.data = self.buffer
				self.reset()
				dataOut.flagNoData = False
				# se deben actualizar mas propiedades del header y del objeto dataOut, por ejemplo, las alturas
				deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]
				xf = dataOut.heightList[0] + dataOut.nHeights * deltaHeight * m
				dataOut.heightList = numpy.arange(dataOut.heightList[0], xf, deltaHeight)
				dataOut.ippSeconds *= m

class ProfileSelector(Operation):

	profileIndex = None
	# Tamanho total de los perfiles
	nProfiles = None

	def __init__(self):

		Operation.__init__(self)
		self.profileIndex = 0

	def incIndex(self):

		self.profileIndex += 1

		if self.profileIndex >= self.nProfiles:
			self.profileIndex = 0

	def isThisProfileInRange(self, profileIndex, minIndex, maxIndex):

		if profileIndex < minIndex:
			return False

		if profileIndex > maxIndex:
			return False

		return True

	def isThisProfileInList(self, profileIndex, profileList):

		if profileIndex not in profileList:
			return False

		return True

	def run(self, dataOut, profileList=None, profileRangeList=None, beam=None, byblock=False, rangeList = None):

		"""
		ProfileSelector:

		Inputs:
			profileList		:	Index of profiles selected. Example: profileList = (0,1,2,7,8)

			profileRangeList	:	Minimum and maximum profile indexes. Example: profileRangeList = (4, 30)

			rangeList			:	List of profile ranges. Example: rangeList = ((4, 30), (32, 64), (128, 256))

		"""

		dataOut.flagNoData = True
		self.nProfiles = dataOut.nProfiles

		if dataOut.flagDataAsBlock:
			"""
			data dimension  = [nChannels, nProfiles, nHeis]
			"""
			if profileList != None:
				dataOut.data = dataOut.data[:,profileList,:]
				dataOut.nProfiles = len(profileList)
				dataOut.profileIndex = dataOut.nProfiles - 1
			else:
				minIndex = profileRangeList[0]
				maxIndex = profileRangeList[1]

				dataOut.data = dataOut.data[:,minIndex:maxIndex+1,:]
				dataOut.nProfiles = maxIndex - minIndex + 1
				dataOut.profileIndex = dataOut.nProfiles - 1

			dataOut.flagNoData = False

			return True

		else:
			"""
			data dimension  = [nChannels, nHeis]

			"""
			if profileList != None:

				dataOut.nProfiles = len(profileList)

				if self.isThisProfileInList(dataOut.profileIndex, profileList):
					dataOut.flagNoData = False
					dataOut.profileIndex = self.profileIndex

					self.incIndex()
				return True


			if profileRangeList != None:

				minIndex = profileRangeList[0]
				maxIndex = profileRangeList[1]

				dataOut.nProfiles = maxIndex - minIndex + 1

				if self.isThisProfileInRange(dataOut.profileIndex, minIndex, maxIndex):
					dataOut.flagNoData = False
					dataOut.profileIndex = self.profileIndex

					self.incIndex()
				return True

			if rangeList != None:

				nProfiles = 0

				for thisRange in rangeList:
					minIndex = thisRange[0]
					maxIndex = thisRange[1]

					nProfiles += maxIndex - minIndex + 1

				dataOut.nProfiles = nProfiles

				for thisRange in rangeList:

					minIndex = thisRange[0]
					maxIndex = thisRange[1]

					if self.isThisProfileInRange(dataOut.profileIndex, minIndex, maxIndex):

#						 print "profileIndex = ", dataOut.profileIndex

						dataOut.flagNoData = False
						dataOut.profileIndex = self.profileIndex

						self.incIndex()
						break
				return True


			if beam != None: #beam is only for AMISR data
				if self.isThisProfileInList(dataOut.profileIndex, dataOut.beamRangeDict[beam]):
					dataOut.flagNoData = False
					dataOut.profileIndex = self.profileIndex

					self.incIndex()
				return 1

		raise ValueError, "ProfileSelector needs profileList or profileRangeList"

		return 0



class Reshaper(Operation):

	def __init__(self):

		Operation.__init__(self)
		self.updateNewHeights = True

	def run(self, dataOut, shape):

		if not dataOut.flagDataAsBlock:
			raise ValueError, "Reshaper can only be used when voltage have been read as Block, getBlock = True"

		if len(shape) != 3:
			raise ValueError, "shape len should be equal to 3, (nChannels, nProfiles, nHeis)"

		shape_tuple = tuple(shape)
		dataOut.data = numpy.reshape(dataOut.data, shape_tuple)
		dataOut.flagNoData = False

		if self.updateNewHeights:

			old_nheights = dataOut.nHeights
			new_nheights = dataOut.data.shape[2]
			factor = 1.0*new_nheights / old_nheights

			deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]

			xf = dataOut.heightList[0] + dataOut.nHeights * deltaHeight * factor

			dataOut.heightList = numpy.arange(dataOut.heightList[0], xf, deltaHeight)

			dataOut.nProfiles = dataOut.data.shape[1]

			dataOut.ippSeconds *= factor
