import os
import datetime
import numpy

from figure import Figure, isRealtime

class MomentsPlot(Figure):
	def __init__(self):
		self.PREFIX = 'prm'

		self.isConfig = False
		self.__nsubplots = 1

		self.WIDTH = 380
		self.HEIGHT = 380
		self.WIDTHPROF = 300
		self.HEIGHTPROF = 20

		self.PLOT_CODE = 1

	def getSubplots(self):
		ncol = int(numpy.sqrt(self.nplots)+0.9)
		nrow = int(self.nplots*1./ncol + 0.9)

		return nrow, ncol

	def setup(self, id, nplots, wintitle, showprofile=True, show=True):
		self.__showprofile = showprofile
		self.nplots = nplots

		ncolspan = 1
		colspan = 1
		if showprofile:
			ncolspan = 3
			colspan = 2
			self.__nsubplots = 2

		self.createFigure(id = id,
						wintitle = wintitle,
						widthplot = self.WIDTH + (self.WIDTHPROF if showprofile else 0),
						heightplot = self.HEIGHT + (self.HEIGHTPROF if showprofile else 0),
						show=show)

		nrow, ncol = self.getSubplots()

		counter = 0
		for y in range(nrow):
			for x in range(ncol):

				if counter >= self.nplots:
					break

				self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)

				if showprofile:
					self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan+colspan, 1, 1)

				counter += 1

	def run(self, dataOut, id, wintitle="", channelList=None, showprofile=True,
			xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
			figpath='', save=False, figfile=None, show=True, realtime=False,
			showMeanDoppler=False, showSpectralWidth=False):

		if dataOut.flagNoData:
			return None

		if realtime:
			if not(isRealtime(utcdatatime = dataOut.utctime)):
				print 'Skipping this plot function'
				return

		if channelList == None:
			channelIndexList = dataOut.channelIndexList
		else:
			channelIndexList = []
			for channel in channelList:
				if channel not in dataOut.channelList:
					raise ValueError, "Channel %d is not in dataOut.channelList"
				channelIndexList.append(dataOut.channelList.index(channel))

		factor = dataOut.normFactor

		x = dataOut.abscissaList
		y = dataOut.heightList
		z = dataOut.data_pre[channelIndexList,:,:]/factor
		z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
		avg = numpy.average(z, axis=1)
		noise = dataOut.noise/factor

		zdB = 10*numpy.log10(z)
		avgdB = 10*numpy.log10(avg)
		noisedB = 10*numpy.log10(noise)

		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " Parameters"
		xlabel = "Velocity (m/s)"
		ylabel = "Range (Km)"

		if not self.isConfig:
			nplots = len(channelIndexList)
			self.setup(id=id,
						nplots=nplots,
						wintitle=wintitle,
						showprofile=showprofile,
						show=show)

			if xmin == None: xmin = numpy.nanmin(x)
			if xmax == None: xmax = numpy.nanmax(x)
			if ymin == None: ymin = numpy.nanmin(y)
			if ymax == None: ymax = numpy.nanmax(y)
			if zmin == None: zmin = numpy.nanmin(avgdB)*0.9
			if zmax == None: zmax = numpy.nanmax(avgdB)*0.9


			self.isConfig = True

		self.setWinTitle(title)

		for i in range(self.nplots):
			str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))
			title = "Channel %d: %4.2fdB: %s" %(dataOut.channelList[i]+1, numpy.mean(noisedB[i]), str_datetime)
			axes = self.axesList[i*self.__nsubplots]
			axes.pcolor(x, y, zdB[i,:,:],
						xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
						xlabel=xlabel, ylabel=ylabel, title=title,
						ticksize=9, cblabel='')

			id_line_counter = 0
			if showMeanDoppler:
				radialvelocity = dataOut.data_param[i, 1, :]
				axes.addpline(radialvelocity, y, idline=id_line_counter, color='black', linestyle="solid", lw=1)
				id_line_counter += 1

			if showSpectralWidth:
				radialvelocity = dataOut.data_param[i, 1, :]
				SpectralWidth = dataOut.data_param[i, 2, :]
				axes.addpline(SpectralWidth*3.0+radialvelocity, y, idline=id_line_counter, color="red", linestyle="solid", lw=1)
				axes.addpline(radialvelocity-SpectralWidth*3.0, y, idline=id_line_counter+1, color="red", linestyle="solid", lw=1)
				id_line_counter += 2


			if self.__showprofile:# Grafica la potencia maxima por altura en un subgrafico
				axes = self.axesList[i*self.__nsubplots +1]
				axes.pline(avgdB[i], y,
						xmin=zmin, xmax=zmax, ymin=ymin, ymax=ymax,
						xlabel='dB', ylabel='', title='',
						ytick_visible=False,
						grid='x')

				noiseline = numpy.repeat(numpy.mean(noisedB[i]), len(y))
				# print len(y), noiseline.shape, noisedB.shape
				axes.addpline(noiseline, y, idline=1, color="black", linestyle="solid", lw=2)
				if dataOut.noiseMode == 2:

					axes.addpline(noisedB[i], y, idline=2, color="red", linestyle="dashed", lw=1)

		self.draw()

		if figfile == None:
			str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
			figfile = self.getFilename(name = str_datetime)

		if figpath != '' and save:
			# store png plot to local folder
			self.saveFigure(figpath, figfile)


class SkyMapPlot(Figure):

	__isConfig = None
	__nsubplots = None

	WIDTHPROF = None
	HEIGHTPROF = None
	PREFIX = 'prm'

	def __init__(self):

		self.__isConfig = False
		self.__nsubplots = 1

		#self.WIDTH = 280
		#self.HEIGHT = 250
		self.WIDTH = 600
		self.HEIGHT = 600
		self.WIDTHPROF = 120
		self.HEIGHTPROF = 0
		self.counter_imagwr = 0

		self.PLOT_CODE = 1
		self.FTP_WEI = None
		self.EXP_CODE = None
		self.SUB_EXP_CODE = None
		self.PLOT_POS = None

	def getSubplots(self):

		ncol = int(numpy.sqrt(self.nplots)+0.9)
		nrow = int(self.nplots*1./ncol + 0.9)

		return nrow, ncol

	def setup(self, id, nplots, wintitle, showprofile=False, show=True):

		self.__showprofile = showprofile
		self.nplots = nplots

		ncolspan = 1
		colspan = 1

		self.createFigure(id = id,
						  wintitle = wintitle,
						  widthplot = self.WIDTH, #+ self.WIDTHPROF,
						  heightplot = self.HEIGHT,# + self.HEIGHTPROF,
						  show=show)

		nrow, ncol = 1,1
		counter = 0
		x = 0
		y = 0
		self.addAxes(1, 1, 0, 0, 1, 1, True)

	def run(self, dataOut, id, wintitle="", channelList=None, showprofile=False,
			xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
			save=False, figpath='./', figfile=None, show=True, ftp=False, wr_period=1,
			server=None, folder=None, username=None, password=None,
			ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0, realtime=False):

		"""

		Input:
			dataOut		 :
			id		:
			wintitle		:
			channelList	 :
			showProfile	 :
			xmin			:	None,
			xmax			:	None,
			ymin			:	None,
			ymax			:	None,
			zmin			:	None,
			zmax			:	None
		"""

		arrayParameters = dataOut.data_param
		error = arrayParameters[:,-1]
		indValid = numpy.where(error == 0)[0]
		finalMeteor = arrayParameters[indValid,:]
		finalAzimuth = finalMeteor[:,4]
		finalZenith = finalMeteor[:,5]

		x = finalAzimuth*numpy.pi/180
		y = finalZenith


		#thisDatetime = dataOut.datatime
		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " Parameters"
		xlabel = "Zonal Zenith Angle (deg) "
		ylabel = "Meridional Zenith Angle (deg)"

		if not self.__isConfig:

			nplots = 1

			self.setup(id=id,
						nplots=nplots,
						wintitle=wintitle,
						showprofile=showprofile,
						show=show)

			self.FTP_WEI = ftp_wei
			self.EXP_CODE = exp_code
			self.SUB_EXP_CODE = sub_exp_code
			self.PLOT_POS = plot_pos
			self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.firstdate = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))
			self.__isConfig = True

		self.setWinTitle(title)

		i = 0
		str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))

		axes = self.axesList[i*self.__nsubplots]
		nevents = axes.x_buffer.shape[0] + x.shape[0]
		title = "Meteor Detection Sky Map\n %s - %s \n Number of events: %5.0f\n" %(self.firstdate,str_datetime,nevents)
		axes.polar(x, y,
					title=title, xlabel=xlabel, ylabel=ylabel,
					ticksize=9, cblabel='')

		self.draw()

		if save:

			self.counter_imagwr += 1
			if (self.counter_imagwr==wr_period):

				if figfile == None:
					figfile = self.getFilename(name = self.name)
				self.saveFigure(figpath, figfile)

				if ftp:
					#provisionalmente envia archivos en el formato de la web en tiempo real
					name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
					path = '%s%03d' %(self.PREFIX, self.id)
					ftp_file = os.path.join(path,'ftp','%s.png'%name)
					self.saveFigure(figpath, ftp_file)
					ftp_filename = os.path.join(figpath,ftp_file)


					try:
						self.sendByFTP(ftp_filename, server, folder, username, password)
					except:
						self.counter_imagwr = 0
						raise ValueError, 'Error FTP'

				self.counter_imagwr = 0


class WindProfilerPlot(Figure):

	__isConfig = None
	__nsubplots = None

	WIDTHPROF = None
	HEIGHTPROF = None
	PREFIX = 'wind'

	def __init__(self):

		self.timerange = 2*60*60
		self.__isConfig = False
		self.__nsubplots = 1

		self.WIDTH = 800
		self.HEIGHT = 150
		self.WIDTHPROF = 120
		self.HEIGHTPROF = 0
		self.counter_imagwr = 0

		self.PLOT_CODE = 0
		self.FTP_WEI = None
		self.EXP_CODE = None
		self.SUB_EXP_CODE = None
		self.PLOT_POS = None
		self.tmin = None
		self.tmax = None

		self.xmin = None
		self.xmax = None

		self.figfile = None

	def getSubplots(self):
		ncol = 1
		nrow = self.nplots

		return nrow, ncol

	def setup(self, id, nplots, wintitle, showprofile=True, show=True):

		self.__showprofile = showprofile
		self.nplots = nplots

		ncolspan = 1
		colspan = 1

		self.createFigure(id = id,
						  wintitle = wintitle,
						  widthplot = self.WIDTH + self.WIDTHPROF,
						  heightplot = self.HEIGHT + self.HEIGHTPROF,
						  show=show)

		nrow, ncol = self.getSubplots()

		counter = 0
		for y in range(nrow):
			if counter >= self.nplots:
				break

			self.addAxes(nrow, ncol*ncolspan, y, 0, colspan, 1)
			counter += 1

	def run(self, dataOut, id, wintitle="", channelList=None,
			xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
			zmax_ver = None, zmin_ver = None, SNRmin = None, SNRmax = None,
			timerange=None, SNRthresh = None,
			save=False, figpath='', lastone=0,figfile=None, ftp=False, wr_period=1, show=True,
			server=None, folder=None, username=None, password=None,
			ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0):
		"""

		Input:
			dataOut		 :
			id		:
			wintitle		:
			channelList	 :
			showProfile	 :
			xmin			:	None,
			xmax			:	None,
			ymin			:	None,
			ymax			:	None,
			zmin			:	None,
			zmax			:	None
		"""

		if channelList == None:
			channelIndexList = dataOut.channelIndexList
		else:
			channelIndexList = []
			for channel in channelList:
				if channel not in dataOut.channelList:
					raise ValueError, "Channel %d is not in dataOut.channelList"
				channelIndexList.append(dataOut.channelList.index(channel))

		if timerange != None:
			self.timerange = timerange

		tmin = None
		tmax = None

		x = dataOut.getTimeRange1()
		y = dataOut.heightList

		z = dataOut.data_output.copy()
		nplots = z.shape[0]	#Number of wind dimensions estimated
		nplotsw = nplots

		#If there is a SNR function defined
		if dataOut.data_SNR != None:
			nplots += 1
			SNR = dataOut.data_SNR
			SNRavg = numpy.average(SNR, axis=0)

			SNRdB = 10*numpy.log10(SNR)
			SNRavgdB = 10*numpy.log10(SNRavg)

			if SNRthresh == None: SNRthresh = -5.0
			ind = numpy.where(SNRavg < 10**(SNRthresh/10))[0]

			for i in range(nplotsw):
				z[i,ind] = numpy.nan


		showprofile = False
		#thisDatetime = dataOut.datatime
		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + "Wind"
		xlabel = ""
		ylabel = "Range (Km)"

		if not self.__isConfig:

			self.setup(id=id,
					   nplots=nplots,
					   wintitle=wintitle,
					   showprofile=showprofile,
					   show=show)

			self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)

			if ymin == None: ymin = numpy.nanmin(y)
			if ymax == None: ymax = numpy.nanmax(y)

			if zmax == None: zmax = numpy.nanmax(abs(z[range(2),:]))
			#if numpy.isnan(zmax): zmax = 50
			if zmin == None: zmin = -zmax

			if nplotsw == 3:
				if zmax_ver == None: zmax_ver = numpy.nanmax(abs(z[2,:]))
				if zmin_ver == None: zmin_ver = -zmax_ver

			if dataOut.data_SNR != None:
				if SNRmin == None:  SNRmin = numpy.nanmin(SNRavgdB)
				if SNRmax == None:  SNRmax = numpy.nanmax(SNRavgdB)

			self.FTP_WEI = ftp_wei
			self.EXP_CODE = exp_code
			self.SUB_EXP_CODE = sub_exp_code
			self.PLOT_POS = plot_pos

			self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.__isConfig = True


		self.setWinTitle(title)

		if ((self.xmax - x[1]) < (x[1]-x[0])):
			x[1] = self.xmax

		strWind = ['Zonal', 'Meridional', 'Vertical']
		strCb = ['Velocity (m/s)','Velocity (m/s)','Velocity (cm/s)']
		zmaxVector = [zmax, zmax, zmax_ver]
		zminVector = [zmin, zmin, zmin_ver]
		windFactor = [1,1,100]

		for i in range(nplotsw):

			title = "%s Wind: %s" %(strWind[i], thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
			axes = self.axesList[i*self.__nsubplots]

			z1 = z[i,:].reshape((1,-1))*windFactor[i]

			axes.pcolorbuffer(x, y, z1,
						xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zminVector[i], zmax=zmaxVector[i],
						xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
						ticksize=9, cblabel=strCb[i], cbsize="1%", colormap="RdBu_r" )

		if dataOut.data_SNR != None:
			i += 1
			title = "Signal Noise Ratio (SNR): %s" %(thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
			axes = self.axesList[i*self.__nsubplots]

			SNRavgdB = SNRavgdB.reshape((1,-1))

			axes.pcolorbuffer(x, y, SNRavgdB,
						xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=SNRmin, zmax=SNRmax,
						xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
						ticksize=9, cblabel='', cbsize="1%", colormap="jet")

		self.draw()

		if self.figfile == None:
			str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.figfile = self.getFilename(name = str_datetime)

		if figpath != '':

			self.counter_imagwr += 1
			if (self.counter_imagwr>=wr_period):
				# store png plot to local folder
				self.saveFigure(figpath, self.figfile)
				# store png plot to FTP server according to RT-Web format
				name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
				ftp_filename = os.path.join(figpath, name)
				self.saveFigure(figpath, ftp_filename)

				self.counter_imagwr = 0

		if x[1] >= self.axesList[0].xmax:
			self.counter_imagwr = wr_period
			self.__isConfig = False
			self.figfile = None


class SpectralFittingPlot(Figure):

	__isConfig = None
	__nsubplots = None

	WIDTHPROF = None
	HEIGHTPROF = None
	PREFIX = 'prm'


	N = None
	ippSeconds = None

	def __init__(self):
		self.__isConfig = False
		self.__nsubplots = 1

		self.WIDTH = 450
		self.HEIGHT = 250
		self.WIDTHPROF = 0
		self.HEIGHTPROF = 0

	def getSubplots(self):
		ncol = int(numpy.sqrt(self.nplots)+0.9)
		nrow = int(self.nplots*1./ncol + 0.9)

		return nrow, ncol

	def setup(self, id, nplots, wintitle, showprofile=False, show=True):

		showprofile = False
		self.__showprofile = showprofile
		self.nplots = nplots

		ncolspan = 5
		colspan = 4
		if showprofile:
			ncolspan = 5
			colspan = 4
			self.__nsubplots = 2

		self.createFigure(id = id,
						  wintitle = wintitle,
						  widthplot = self.WIDTH + self.WIDTHPROF,
						  heightplot = self.HEIGHT + self.HEIGHTPROF,
						  show=show)

		nrow, ncol = self.getSubplots()

		counter = 0
		for y in range(nrow):
			for x in range(ncol):

				if counter >= self.nplots:
					break

				self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)

				if showprofile:
					self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan+colspan, 1, 1)

				counter += 1

	def run(self, dataOut, id, cutHeight=None, fit=False, wintitle="", channelList=None, showprofile=True,
			xmin=None, xmax=None, ymin=None, ymax=None,
			save=False, figpath='./', figfile=None, show=True):

		"""

		Input:
			dataOut		 :
			id		:
			wintitle		:
			channelList	 :
			showProfile	 :
			xmin			:	None,
			xmax			:	None,
			zmin			:	None,
			zmax			:	None
		"""

		if cutHeight==None:
			h=270
		heightindex = numpy.abs(cutHeight - dataOut.heightList).argmin()
		cutHeight = dataOut.heightList[heightindex]

		factor = dataOut.normFactor
		x = dataOut.abscissaList[:-1]
		#y = dataOut.getHeiRange()

		z = dataOut.data_pre[:,:,heightindex]/factor
		z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
		avg = numpy.average(z, axis=1)
		listChannels = z.shape[0]

		#Reconstruct Function
		if fit==True:
			groupArray = dataOut.groupList
			listChannels = groupArray.reshape((groupArray.size))
			listChannels.sort()
			spcFitLine = numpy.zeros(z.shape)
			constants = dataOut.constants

			nGroups = groupArray.shape[0]
			nChannels = groupArray.shape[1]
			nProfiles = z.shape[1]

			for f in range(nGroups):
				groupChann = groupArray[f,:]
				p = dataOut.data_param[f,:,heightindex]
				#p = numpy.array([ 89.343967,0.14036615,0.17086219,18.89835291,1.58388365,1.55099167])
				fitLineAux = dataOut.library.modelFunction(p, constants)*nProfiles
				fitLineAux = fitLineAux.reshape((nChannels,nProfiles))
				spcFitLine[groupChann,:] = fitLineAux
			#spcFitLine = spcFitLine/factor

			z = z[listChannels,:]
			spcFitLine = spcFitLine[listChannels,:]
			spcFitLinedB = 10*numpy.log10(spcFitLine)

		zdB = 10*numpy.log10(z)
		#thisDatetime = dataOut.datatime
		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " Doppler Spectra: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
		xlabel = "Velocity (m/s)"
		ylabel = "Spectrum"

		if not self.__isConfig:

			nplots = listChannels.size

			self.setup(id=id,
					   nplots=nplots,
					   wintitle=wintitle,
					   showprofile=showprofile,
					   show=show)

			if xmin == None: xmin = numpy.nanmin(x)
			if xmax == None: xmax = numpy.nanmax(x)
			if ymin == None: ymin = numpy.nanmin(zdB)
			if ymax == None: ymax = numpy.nanmax(zdB)+2

			self.__isConfig = True

		self.setWinTitle(title)
		for i in range(self.nplots):
			#title = "Channel %d: %4.2fdB" %(dataOut.channelList[i]+1, noisedB[i])
			title = "Height %4.1f km\nChannel %d:" %(cutHeight, listChannels[i]+1)
			axes = self.axesList[i*self.__nsubplots]
			if fit == False:
				axes.pline(x, zdB[i,:],
							xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
							xlabel=xlabel, ylabel=ylabel, title=title
							)
			if fit == True:
				fitline=spcFitLinedB[i,:]
				y=numpy.vstack([zdB[i,:],fitline] )
				legendlabels=['Data','Fitting']
				axes.pmultilineyaxis(x, y,
							xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
							xlabel=xlabel, ylabel=ylabel, title=title,
							legendlabels=legendlabels, marker=None,
							linestyle='solid', grid='both')

		self.draw()

		if save:
			date = thisDatetime.strftime("%Y%m%d_%H%M%S")
			if figfile == None:
				figfile = self.getFilename(name = date)

			self.saveFigure(figpath, figfile)


class EWDriftsPlot(Figure):

	__isConfig = None
	__nsubplots = None

	WIDTHPROF = None
	HEIGHTPROF = None
	PREFIX = 'drift'

	def __init__(self):

		self.timerange = 2*60*60
		self.isConfig = False
		self.__nsubplots = 1

		self.WIDTH = 800
		self.HEIGHT = 150
		self.WIDTHPROF = 120
		self.HEIGHTPROF = 0
		self.counter_imagwr = 0

		self.PLOT_CODE = 0
		self.FTP_WEI = None
		self.EXP_CODE = None
		self.SUB_EXP_CODE = None
		self.PLOT_POS = None
		self.tmin = None
		self.tmax = None

		self.xmin = None
		self.xmax = None

		self.figfile = None

	def getSubplots(self):

		ncol = 1
		nrow = self.nplots

		return nrow, ncol

	def setup(self, id, nplots, wintitle, showprofile=True, show=True):

		self.__showprofile = showprofile
		self.nplots = nplots

		ncolspan = 1
		colspan = 1

		self.createFigure(id = id,
						  wintitle = wintitle,
						  widthplot = self.WIDTH + self.WIDTHPROF,
						  heightplot = self.HEIGHT + self.HEIGHTPROF,
						  show=show)

		nrow, ncol = self.getSubplots()

		counter = 0
		for y in range(nrow):
			if counter >= self.nplots:
				break

			self.addAxes(nrow, ncol*ncolspan, y, 0, colspan, 1)
			counter += 1

	def run(self, dataOut, id, wintitle="", channelList=None,
			xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
			zmaxVertical = None, zminVertical = None, zmaxZonal = None, zminZonal = None,
			timerange=None, SNRthresh = -numpy.inf, SNRmin = None, SNRmax = None, SNR_1 = False,
			save=False, figpath='', lastone=0,figfile=None, ftp=False, wr_period=1, show=True,
			server=None, folder=None, username=None, password=None,
			ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0):
		"""

		Input:
			dataOut		 :
			id		:
			wintitle		:
			channelList	 :
			showProfile	 :
			xmin			:	None,
			xmax			:	None,
			ymin			:	None,
			ymax			:	None,
			zmin			:	None,
			zmax			:	None
		"""

		if timerange != None:
			self.timerange = timerange

		tmin = None
		tmax = None

		x = dataOut.getTimeRange1()
		#y = dataOut.heightList
		y = dataOut.heightList

		z = dataOut.data_output
		nplots = z.shape[0]	#Number of wind dimensions estimated
		nplotsw = nplots

		#If there is a SNR function defined
		if dataOut.data_SNR != None:
			nplots += 1
			SNR = dataOut.data_SNR

			if SNR_1:
				SNR += 1

			SNRavg = numpy.average(SNR, axis=0)

			SNRdB = 10*numpy.log10(SNR)
			SNRavgdB = 10*numpy.log10(SNRavg)

			ind = numpy.where(SNRavg < 10**(SNRthresh/10))[0]

			for i in range(nplotsw):
				z[i,ind] = numpy.nan


		showprofile = False
		#thisDatetime = dataOut.datatime
		thisDatetime = datetime.datetime.utcfromtimestamp(x[1])
		title = wintitle + " EW Drifts"
		xlabel = ""
		ylabel = "Height (Km)"

		if not self.__isConfig:

			self.setup(id=id,
					   nplots=nplots,
					   wintitle=wintitle,
					   showprofile=showprofile,
					   show=show)

			self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)

			if ymin == None: ymin = numpy.nanmin(y)
			if ymax == None: ymax = numpy.nanmax(y)

			if zmaxZonal == None: zmaxZonal = numpy.nanmax(abs(z[0,:]))
			if zminZonal == None: zminZonal = -zmaxZonal
			if zmaxVertical == None: zmaxVertical = numpy.nanmax(abs(z[1,:]))
			if zminVertical == None: zminVertical = -zmaxVertical

			if dataOut.data_SNR != None:
				if SNRmin == None:  SNRmin = numpy.nanmin(SNRavgdB)
				if SNRmax == None:  SNRmax = numpy.nanmax(SNRavgdB)

			self.FTP_WEI = ftp_wei
			self.EXP_CODE = exp_code
			self.SUB_EXP_CODE = sub_exp_code
			self.PLOT_POS = plot_pos

			self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.__isConfig = True


		self.setWinTitle(title)

		if ((self.xmax - x[1]) < (x[1]-x[0])):
			x[1] = self.xmax

		strWind = ['Zonal','Vertical']
		strCb = 'Velocity (m/s)'
		zmaxVector = [zmaxZonal, zmaxVertical]
		zminVector = [zminZonal, zminVertical]

		for i in range(nplotsw):

			title = "%s Drifts: %s" %(strWind[i], thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
			axes = self.axesList[i*self.__nsubplots]

			z1 = z[i,:].reshape((1,-1))

			axes.pcolorbuffer(x, y, z1,
						xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zminVector[i], zmax=zmaxVector[i],
						xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
						ticksize=9, cblabel=strCb, cbsize="1%", colormap="RdBu_r")

		if dataOut.data_SNR != None:
			i += 1
			if SNR_1:
				title = "Signal Noise Ratio + 1 (SNR+1): %s" %(thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
			else:
				title = "Signal Noise Ratio (SNR): %s" %(thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
			axes = self.axesList[i*self.__nsubplots]
			SNRavgdB = SNRavgdB.reshape((1,-1))

			axes.pcolorbuffer(x, y, SNRavgdB,
						xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=SNRmin, zmax=SNRmax,
						xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
						ticksize=9, cblabel='', cbsize="1%", colormap="jet")

		self.draw()

		if self.figfile == None:
			str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.figfile = self.getFilename(name = str_datetime)

		if figpath != '':

			self.counter_imagwr += 1
			if (self.counter_imagwr>=wr_period):
				# store png plot to local folder
				self.saveFigure(figpath, self.figfile)
				# store png plot to FTP server according to RT-Web format
				name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
				ftp_filename = os.path.join(figpath, name)
				self.saveFigure(figpath, ftp_filename)

				self.counter_imagwr = 0

		if x[1] >= self.axesList[0].xmax:
			self.counter_imagwr = wr_period
			self.__isConfig = False
			self.figfile = None


class ParametersPlot(Figure):
	def __init__(self):
		self.PREFIX = 'prm'

		self.timerange = 2*60*60
		self.__isConfig = False
		self.__nsubplots = 1

		self.WIDTH = 420
		self.HEIGHT = 320
		self.WIDTHPROF = 120
		self.HEIGHTPROF = 0

		self.tmin = None
		self.tmax = None

		self.xmin = None
		self.xmax = None

		self.figfile = None

	def getSubplots(self,factor=1):
		ncol = 1
		nrow = int(self.nplots*factor)
		return nrow, ncol

	def setup(self, id, nplots, wintitle, showprofile=True, show=True,COH=True,PHASE=True):

		self.__showprofile = showprofile
		self.nplots = nplots

		ncolspan = 1
		colspan = 1

		self.createFigure(id = id,
						  wintitle = wintitle,
						  widthplot = self.WIDTH + self.WIDTHPROF,
						  heightplot = self.HEIGHT + self.HEIGHTPROF,
						  show=show)

		if COH & PHASE:
			factor=1
		else:
			factor=.5

		nrow, ncol = self.getSubplots(factor=factor)

		counter = 0
		for y in range(nrow):
			for x in range(ncol):

				if counter >= self.nplots:
					break

				self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)

				if showprofile:
					self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan+colspan, 1, 1)

				counter += 1

	def run(self, dataOut, id, wintitle="", channelList=None, showprofile=False,
			xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,timerange=None,
			parameterIndex = None, onlyPositive = False, SNRthresh = -numpy.inf, DOP=True,
			SNR = True, SNRdBmin = None, SNRdBmax = None, zlabel = "",save=False, figpath='',
			figfile=None, show=True, folder=None, ext='.png',data_time_save=False, pairsList=""):


		# Reading the data to be plotted
		#here we extract the data passed through dataOut.data_param that content the moments: snr,power,radialVelocity that is called fd
		#Not sure if exists dataOut.data_param from the new HDF5 format.
		#try to fix and read to plot it.
		if dataOut.type == "Parameters":
			data_param = getattr(dataOut, "data_param")
		else:
			pass
		#Initializing variables
		self.timerange = timerange if timerange != None else None
		parameterIndex = 1 if parameterIndex == None else parameterIndex
		SNRmin= SNRdBmin
		SNRmax= SNRdBmax
		# if timerange != None:
		# 	self.timerange = timerange
		# if parameterIndex == None:
		# 	parameterIndex = 1
		if channelList == None:
			channelIndexList = numpy.arange(data_param.shape[0])
		else:
			channelIndexList = numpy.array(channelList)

		nchan = len(channelIndexList) #Number of channels being plotted


		#Creating the exact data to be plotted
		x = dataOut.getTimeRange1()
		y = dataOut.heightList
		z = data_param[channelIndexList,parameterIndex,:].copy()
		#Se esta asumiendo que entra abscissaList en el dataout. vamos a recontruirlo.
		zRange = dataOut.abscissaList
		nplots = z.shape[0]

		if (dataOut.data_SNR != None).any():
			SNRarray = dataOut.data_SNR[channelIndexList,:] # This line extract snr from diferent channels

			SNRdB = 10*numpy.log10(SNRarray)
			#print SNRarray
			ind = numpy.where(SNRarray < SNRthresh)
			z[ind] = numpy.nan

		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " Parameters Plot" #: %s" %(thisDatetime.strftime("%d-%b-%Y"))
		xlabel = ""
		ylabel = "Range (Km)"

		if DOP and SNR:
			factor=1
		else:
			factor=.5


		if SNR: nplots = int(2*nplots*factor)


		if onlyPositive:
			colormap = "jet"
			zmin = 0
		else: colormap = "RdBu_r"

		if not self.__isConfig:

			self.setup(id=id,
						nplots=nplots,
						wintitle=wintitle,
						showprofile=showprofile,
						show=show)

			self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)

			if ymin == None: ymin = numpy.nanmin(y)
			if ymax == None: ymax = numpy.nanmax(y)
			if zmin == None: zmin = numpy.nanmin(zRange)
			if zmax == None: zmax = numpy.nanmax(zRange)

			if SNR != None:
				if SNRmin == None:  SNRmin = numpy.nanmin(SNRdB)
				if SNRmax == None:  SNRmax = numpy.nanmax(SNRdB)


			self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.__isConfig = True
			self.figfile = figfile
			self.data_time_save=data_time_save

		self.setWinTitle(title)

		if ((self.xmax - x[1]) < (x[1]-x[0])):
			x[1] = self.xmax

		for i in range(nchan):
			if SNR: j = 2*i
			if not DOP:
				j=i

			else: j = i

			if DOP: # by default radial velocity
				title = "Channel %d: %s" %(channelIndexList[i]+1, thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))

				if ((dataOut.azimuth!=None) and (dataOut.zenith!=None)):
					title = title + '_' + 'azimuth,zenith=%2.2f,%2.2f'%(dataOut.azimuth, dataOut.zenith)

				axes = self.axesList[j*self.__nsubplots]

				z1 = z[i,:].reshape((1,-1))

				axes.pcolorbuffer(x, y, z1,
							xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
							xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,colormap=colormap,
							ticksize=9, cblabel=zlabel, cbsize="1%")
			else:
				j=-1

			if SNR:
				title = "Channel %d Signal Noise Ratio (SNR): %s" %(channelIndexList[i]+1, thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
				axes = self.axesList[(j + 1)*self.__nsubplots]
				z1 = SNRdB[i,:].reshape((1,-1))
				axes.pcolorbuffer(x, y, z1,
						xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=SNRmin, zmax=SNRmax,
						xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,colormap="jet",
						ticksize=9, cblabel=zlabel, cbsize="1%")



		self.draw()

		if self.figfile == None:
			str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.figfile = self.getFilename(name = str_datetime,ext=ext)

		if figpath != '':
			# store png plot to local folder
			if self.data_time_save:
				str_doy=thisDatetime.strftime("%Y%j")
				figpath=figpath+"/d%s"%str_doy
			if save:
				self.saveFigure(figpath, self.figfile)

		if x[1] >= self.axesList[0].xmax:
			self.__isConfig = False
			self.figfile = None
