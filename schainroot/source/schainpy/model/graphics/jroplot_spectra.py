'''
@author: Daniel Suarez
Modified by Alejandro, some methods and attributes were redefined or rewriten

'''
import os
import datetime
import numpy

from figure import Figure, isRealtime

class CoherenceMap(Figure):
	isConfig = None
	__nsubplots = None

	WIDTHPROF = None
	HEIGHTPROF = None
	PREFIX = 'cmap'

	def __init__(self):
		self.timerange = 2*60*60
		self.isConfig = False
		self.__nsubplots = 1

		self.WIDTH = 480
		self.HEIGHT = 150
		self.WIDTHPROF = 120
		self.HEIGHTPROF = 0


		self.xmin = None
		self.xmax = None
		self.figfile= None
		self.PLOT_CODE = "03"

	def getSubplots(self,factor=1):
		ncol = 1
		nrow = int(self.nplots*2*factor)
		return nrow, ncol


	def setup(self, id, nplots, wintitle, showprofile=True, show=True,COH=True,PHASE=True):
		self.__showprofile = showprofile
		self.nplots = nplots

		ncolspan = 1
		colspan = 1
		if showprofile:
			ncolspan = 7
			colspan = 6
			self.__nsubplots = 2

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

		for y in range(nrow):
			for x in range(ncol):

				self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)

				if showprofile:
					self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan+colspan, 1, 1)


	def run(self, dataOut, id, wintitle="", pairsList=None, showprofile='True',
			xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
			timerange=None,COH=True,PHASE=True, save=False, figpath='', figfile=None,
			coherence_cmap='jet', phase_cmap='RdBu_r', show=True, folder=None,
			ext='.png',data_time_save=False, location=None, cod_param=None, f_number=None):

		if pairsList == None:
			pairsIndexList = dataOut.pairsIndexList
		else:
			pairsIndexList = []
			for pair in pairsList:
				if pair not in dataOut.pairsList:
					raise ValueError, "Pair %s is not in dataOut.pairsList" %(pair)
				pairsIndexList.append(dataOut.pairsList.index(pair))

		if timerange != None:
			self.timerange = timerange

		if pairsIndexList == []:
			return

		if len(pairsIndexList) > 4:
			pairsIndexList = pairsIndexList[0:4]


		x = dataOut.getTimeRange()
		y = dataOut.getHeiRange()

		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " CoherenceMap"
		xlabel = ""
		ylabel = "Range (Km)"

		if not self.isConfig:
			nplots = len(pairsIndexList)
			self.setup(id=id,
						nplots=nplots,
						wintitle=wintitle,
						showprofile=showprofile,
						show=show,
						COH=COH,
						PHASE=PHASE)


			self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)

			if ymin == None: ymin = numpy.nanmin(y)
			if ymax == None: ymax = numpy.nanmax(y)
			if zmin == None: zmin = 0.
			if zmax == None: zmax = 1.

			self.data_time_save=data_time_save
			self.figfile=figfile


			self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")

			self.isConfig = True

		self.setWinTitle(title)

		if ((self.xmax - x[1]) < (x[1]-x[0])):
			x[1] = self.xmax

		for i in range(self.nplots):

			pair = dataOut.pairsList[pairsIndexList[i]]
			#In this point dataout has crossdatainfo?

			#There was an option for ploting coherence map from spectra proc, but it was erased, it has more sense if it's plot from parameters proc
			# with a GetCrossData Operation

			coherence = dataOut.CrossData[0].transpose()

			z = coherence.reshape((1,-1))

			counter= 0

			if COH:
				title = "Coherence %d%d: %s" %(pair[0], pair[1], thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
				axes = self.axesList[i*self.__nsubplots*2]
				axes.pcolorbuffer(x, y, z,
							xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
							xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
							ticksize=9, cblabel='', colormap=coherence_cmap, cbsize="1%")

				if self.__showprofile:
					counter += 1
					axes = self.axesList[i*self.__nsubplots*2+counter]
					axes.pline(coherence, y,
							xmin=zmin, xmax=zmax, ymin=ymin, ymax=ymax,
							xlabel='', ylabel='', title='', ticksize=7,
							ytick_visible=False, nxticks=5,
							grid='x')



			phase = dataOut.CrossData[1].transpose()

			z = phase.reshape((1,-1))

			if PHASE:
				title = "Phase %d%d: %s" %(pair[0], pair[1], thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
				axes = self.axesList[i*self.__nsubplots*2 ]
				axes.pcolorbuffer(x, y, z,
							xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=-180, zmax=180,
							xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
							ticksize=9, cblabel='', colormap=phase_cmap, cbsize="1%")

				if self.__showprofile:
					counter += 1
					axes = self.axesList[i*self.__nsubplots*2 +counter]
					axes.pline(phase, y,
							xmin=-180, xmax=180, ymin=ymin, ymax=ymax,
							xlabel='', ylabel='', title='', ticksize=7,
							ytick_visible=False, nxticks=4,
							grid='x')

		self.draw()

		if self.figfile == None:
			str_datetime = thisDatetime.strftime("%Y%j")+location+cod_param+f_number+self.PLOT_CODE+"01"
			self.figfile = self.getFilename(name = str_datetime,ext=ext)

		if figpath != '':
			# store png plot to local folder
			if self.data_time_save:
				str_doy=thisDatetime.strftime("%Y%j")
				figpath=figpath+"/d%s"%str_doy
			if save:
				self.saveFigure(figpath, self.figfile)


		if x[1] >= self.axesList[0].xmax:
			self.isConfig = False
			self.figfile=None


# Not checked because they're not used in HF radar
class SpectraPlot(Figure):

	isConfig = None
	__nsubplots = None

	WIDTHPROF = None
	HEIGHTPROF = None
	PREFIX = 'spc'

	def __init__(self):

		self.isConfig = False
		self.__nsubplots = 1

		self.WIDTH = 380
		self.HEIGHT = 320
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

	def run(self, dataOut, id, wintitle="", channelList=None, showprofile=True,
			xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
			save=False,save_ftp = False, figpath='', figfile=None, show=True,data_time_save=False, ftp=False, wr_period=1,
			server=None, folder=None, username=None, password=None,
			ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0, realtime=False,ext='.png'):

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

		self.data_time_save=data_time_save
		self.figfile=figfile
		self.ftp=ftp

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

		x = dataOut.getVelRange(1)
		y = dataOut.getHeiRange()

		z = dataOut.data_spc[channelIndexList,:,:]/factor
		z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
		avg = numpy.average(z, axis=1)
		#avg = numpy.nanmean(z, axis=1)
		noise = dataOut.noise/factor

		zdB = 10*numpy.log10(z)
		avgdB = 10*numpy.log10(avg)
		noisedB = 10*numpy.log10(noise)

		#thisDatetime = dataOut.datatime
		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " Spectra"
		if ((dataOut.azimuth!=None) and (dataOut.zenith!=None)):
			title = title + '_' + 'azimuth,zenith=%2.2f,%2.2f'%(dataOut.azimuth, dataOut.zenith)

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

			self.FTP_WEI = ftp_wei
			self.EXP_CODE = exp_code
			self.SUB_EXP_CODE = sub_exp_code
			self.PLOT_POS = plot_pos

			self.isConfig = True

		self.setWinTitle(title)

		for i in range(self.nplots):
			str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))
			title = "Channel %d: %4.2fdB: %s" %(dataOut.channelList[i]+1, noisedB[i], str_datetime)
			if len(dataOut.beam.codeList) != 0:
				title = "Ch%d:%4.2fdB,%2.2f,%2.2f:%s" %(dataOut.channelList[i]+1, noisedB[i], dataOut.beam.azimuthList[i], dataOut.beam.zenithList[i], str_datetime)

			axes = self.axesList[i*self.__nsubplots]
			axes.pcolor(x, y, zdB[i,:,:],
						xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
						xlabel=xlabel, ylabel=ylabel, title=title,
						ticksize=9,cblabel='')

			if self.__showprofile:
				axes = self.axesList[i*self.__nsubplots +1]
				axes.pline(avgdB[i], y,
						xmin=zmin, xmax=zmax, ymin=ymin, ymax=ymax,
						xlabel='dB', ylabel='', title='',
						ytick_visible=False,
						grid='x')

				noiseline = numpy.repeat(noisedB[i], len(y))
				axes.addpline(noiseline, y, idline=1, color="black", linestyle="dashed", lw=2)

		self.draw()

		if self.figfile == None:
			str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.figfile = self.getFilename(name = str_datetime,ext=ext)

		if figpath != '':
			self.counter_imagwr += 1
			if (self.counter_imagwr>=wr_period):
				# store png plot to local folder
				if self.data_time_save:
					str_doy=thisDatetime.strftime("%Y%j")
					figpath=figpath+"/d%s"%str_doy
				if save:
					self.saveFigure(figpath, self.figfile)
				# store png plot to FTP server according to RT-Web format
				name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS,ext=ext)
				ftp_filename = os.path.join(figpath, name)
		if save_ftp:
				self.saveFigure(figpath, ftp_filename)
				self.counter_imagwr = 0
		if self.ftp:
			remote_folder='/home/wmaster/web2/web_signalchain/data/JRO/HF/'
			remote_folder=remote_folder+thisDatetime.strftime("%Y/%m/%d/figures/")
			print remote_folder
			command_1="mkdir -p %s"%(remote_folder)
			try:
				os.system("ssh wmaster@10.10.120.125 -p 6633 %s"%(command_1))
			except:
				print "Can't create the folder"
			files_to_send=figpath+"/*.jpeg"
			temp_command = "scp -P 6633 %s wmaster@10.10.120.125:%s"%(files_to_send,remote_folder)
			print temp_command
			try:
						os.system(temp_command)
			except:
					print "Error sending graphics"


class CrossSpectraPlot(Figure):

	isConfig = None
	__nsubplots = None

	WIDTH = None
	HEIGHT = None
	WIDTHPROF = None
	HEIGHTPROF = None
	PREFIX = 'cspc'

	def __init__(self):

		self.isConfig = False
		self.__nsubplots = 4
		self.counter_imagwr = 0
		self.WIDTH = 380
		self.HEIGHT = 250
		self.WIDTHPROF = 0
		self.HEIGHTPROF = 0

		self.PLOT_CODE = 1
		self.FTP_WEI = None
		self.EXP_CODE = None
		self.SUB_EXP_CODE = None
		self.PLOT_POS = None

	def getSubplots(self):

		ncol = 4
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
						  show=True)

		nrow, ncol = self.getSubplots()

		counter = 0
		for y in range(nrow):
			for x in range(ncol):
				self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)

				counter += 1

	def run(self, dataOut, id, wintitle="", pairsList=None,
			xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
			save=False, figpath='', figfile=None, ftp=False, wr_period=1,
			power_cmap='jet', coherence_cmap='jet', phase_cmap='RdBu_r', show=True,
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

		if pairsList == None:
			pairsIndexList = dataOut.pairsIndexList
		else:
			pairsIndexList = []
			for pair in pairsList:
				if pair not in dataOut.pairsList:
					raise ValueError, "Pair %s is not in dataOut.pairsList" %(pair)
				pairsIndexList.append(dataOut.pairsList.index(pair))

		if pairsIndexList == []:
			return

		if len(pairsIndexList) > 4:
			pairsIndexList = pairsIndexList[0:4]
		factor = dataOut.normFactor
		x = dataOut.getVelRange(1)
		y = dataOut.getHeiRange()
		z = dataOut.data_spc[:,:,:]/factor
#		z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
		avg = numpy.abs(numpy.average(z, axis=1))
		noise = dataOut.noise/factor

		zdB = 10*numpy.log10(z)
		avgdB = 10*numpy.log10(avg)
		noisedB = 10*numpy.log10(noise)


		#thisDatetime = dataOut.datatime
		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " Cross-Spectra: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
		xlabel = "Velocity (m/s)"
		ylabel = "Range (Km)"

		if not self.isConfig:

			nplots = len(pairsIndexList)

			self.setup(id=id,
					   nplots=nplots,
					   wintitle=wintitle,
					   showprofile=False,
					   show=show)

			if xmin == None: xmin = numpy.nanmin(x)
			if xmax == None: xmax = numpy.nanmax(x)
			if ymin == None: ymin = numpy.nanmin(y)
			if ymax == None: ymax = numpy.nanmax(y)
			if zmin == None: zmin = numpy.nanmin(avgdB)*0.9
			if zmax == None: zmax = numpy.nanmax(avgdB)*0.9

			self.FTP_WEI = ftp_wei
			self.EXP_CODE = exp_code
			self.SUB_EXP_CODE = sub_exp_code
			self.PLOT_POS = plot_pos

			self.isConfig = True

		self.setWinTitle(title)

		for i in range(self.nplots):
			pair = dataOut.pairsList[pairsIndexList[i]]
			str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))
			title = "Ch%d: %4.2fdB: %s" %(pair[0], noisedB[pair[0]], str_datetime)
			zdB = 10.*numpy.log10(dataOut.data_spc[pair[0],:,:]/factor)
			axes0 = self.axesList[i*self.__nsubplots]
			axes0.pcolor(x, y, zdB,
						xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
						xlabel=xlabel, ylabel=ylabel, title=title,
						ticksize=9, colormap=power_cmap, cblabel='')

			title = "Ch%d: %4.2fdB: %s" %(pair[1], noisedB[pair[1]], str_datetime)
			zdB = 10.*numpy.log10(dataOut.data_spc[pair[1],:,:]/factor)
			axes0 = self.axesList[i*self.__nsubplots+1]
			axes0.pcolor(x, y, zdB,
						xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
						xlabel=xlabel, ylabel=ylabel, title=title,
						ticksize=9, colormap=power_cmap, cblabel='')

			coherenceComplex = dataOut.data_cspc[pairsIndexList[i],:,:]/numpy.sqrt(dataOut.data_spc[pair[0],:,:]*dataOut.data_spc[pair[1],:,:])
			coherence = numpy.abs(coherenceComplex)
#			phase = numpy.arctan(-1*coherenceComplex.imag/coherenceComplex.real)*180/numpy.pi
			phase = numpy.arctan2(coherenceComplex.imag, coherenceComplex.real)*180/numpy.pi

			title = "Coherence %d%d" %(pair[0], pair[1])
			axes0 = self.axesList[i*self.__nsubplots+2]
			axes0.pcolor(x, y, coherence,
						xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=0, zmax=1,
						xlabel=xlabel, ylabel=ylabel, title=title,
						ticksize=9, colormap=coherence_cmap, cblabel='')

			title = "Phase %d%d" %(pair[0], pair[1])
			axes0 = self.axesList[i*self.__nsubplots+3]
			axes0.pcolor(x, y, phase,
						xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=-180, zmax=180,
						xlabel=xlabel, ylabel=ylabel, title=title,
						ticksize=9, colormap=phase_cmap, cblabel='')



		self.draw()

		if figfile == None:
			str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
			figfile = self.getFilename(name = str_datetime)

		if figpath != '':
			self.counter_imagwr += 1
			if (self.counter_imagwr>=wr_period):
				# store png plot to local folder
				self.saveFigure(figpath, figfile)
				# store png plot to FTP server according to RT-Web format
				name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
				ftp_filename = os.path.join(figpath, name)
				self.saveFigure(figpath, ftp_filename)
				self.counter_imagwr = 0


class RTIPlot(Figure):

	__isConfig = None
	__nsubplots = None

	WIDTHPROF = None
	HEIGHTPROF = None
	PREFIX = 'rti'

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
		if showprofile:
			ncolspan = 7
			colspan = 6
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

	def run(self, dataOut, id, wintitle="", channelList=None, showprofile='True',
			xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
			timerange=None,
			save=False, figpath='', lastone=0,figfile=None, ftp=False, wr_period=1, show=True,
			server=None, folder=None, username=None, password=None,
			ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0,data_time_save=False,ext='.png'):

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

		#tmin = None
		#tmax = None
		factor = dataOut.normFactor
		x = dataOut.getTimeRange()
		y = dataOut.getHeiRange()

		z = dataOut.data_spc[channelIndexList,:,:]/factor
		z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
		avg = numpy.average(z, axis=1)

		avgdB = 10.*numpy.log10(avg)


#		thisDatetime = dataOut.datatime
		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " RTI" #: %s" %(thisDatetime.strftime("%d-%b-%Y"))
		xlabel = ""
		ylabel = "Range (Km)"

		if not self.__isConfig:

			nplots = len(channelIndexList)

			self.setup(id=id,
					   nplots=nplots,
					   wintitle=wintitle,
					   showprofile=showprofile,
					   show=show)

			self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)

#			 if timerange != None:
#				 self.timerange = timerange
#				 self.xmin, self.tmax = self.getTimeLim(x, xmin, xmax, timerange)



			if ymin == None: ymin = numpy.nanmin(y)
			if ymax == None: ymax = numpy.nanmax(y)
			if zmin == None: zmin = numpy.nanmin(avgdB)*0.9
			if zmax == None: zmax = numpy.nanmax(avgdB)*0.9

			self.FTP_WEI = ftp_wei
			self.EXP_CODE = exp_code
			self.SUB_EXP_CODE = sub_exp_code
			self.PLOT_POS = plot_pos
			self.data_time_save=data_time_save
			self.ftp=ftp

			self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.__isConfig = True
			self.figfile = figfile
			self.counter_imagwr=wr_period

		self.setWinTitle(title)

		if ((self.xmax - x[1]) < (x[1]-x[0])):
			x[1] = self.xmax

		for i in range(self.nplots):
			title = "Channel %d: %s" %(dataOut.channelList[i]+1, thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
			if ((dataOut.azimuth!=None) and (dataOut.zenith!=None)):
				title = title + '_' + 'azimuth,zenith=%2.2f,%2.2f'%(dataOut.azimuth, dataOut.zenith)
			axes = self.axesList[i*self.__nsubplots]
			zdB = avgdB[i].reshape((1,-1))
			axes.pcolorbuffer(x, y, zdB,
						xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
						xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
						ticksize=9, cblabel='', cbsize="1%")

			if self.__showprofile:
				axes = self.axesList[i*self.__nsubplots +1]
				axes.pline(avgdB[i], y,
						xmin=zmin, xmax=zmax, ymin=ymin, ymax=ymax,
						xlabel='dB', ylabel='', title='',
						ytick_visible=False,
						grid='x')

		self.draw()

		if self.figfile == None:
			str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.figfile = self.getFilename(name = str_datetime,ext=ext)

		if figpath != '':
			self.counter_imagwr += 1
			if (self.counter_imagwr>=wr_period):
				# store png plot to local folder
				if self.data_time_save:
					str_doy=thisDatetime.strftime("%Y%j")
					figpath=figpath+"/d%s"%str_doy
				if save:
					self.saveFigure(figpath, self.figfile)
				# store png plot to FTP server according to RT-Web format
				name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS,ext=ext)
				ftp_filename = os.path.join(figpath, name)
				#self.saveFigure(figpath, ftp_filename)
				self.counter_imagwr = 0
		if self.ftp:
			remote_folder='/home/wmaster/web2/web_signalchain/data/JRO/HF/'
			remote_folder=remote_folder+thisDatetime.strftime("%Y/%m/%d/figures/")
			print remote_folder
			command_1="mkdir -p %s"%(remote_folder)
			try:
				os.system("ssh wmaster@10.10.120.125 -p 6633 %s"%(command_1))
			except:
				print "Can't create the folder"
			files_to_send=figpath+"/*.jpeg"
			temp_command = "scp -P 6633 %s wmaster@10.10.120.125:%s"%(files_to_send,remote_folder)
			print temp_command
			try:
						os.system(temp_command)
			except:
					print "Error sending graphics"

		if x[1] >= self.axesList[0].xmax:
			self.counter_imagwr = wr_period
			self.__isConfig = False
			self.figfile = None


class PowerProfile(Figure):
	isConfig = None
	__nsubplots = None

	WIDTHPROF = None
	HEIGHTPROF = None
	PREFIX = 'spcprofile'

	def __init__(self):
		self.isConfig = False
		self.__nsubplots = 1

		self.WIDTH = 300
		self.HEIGHT = 500
		self.counter_imagwr = 0

	def getSubplots(self):
		ncol = 1
		nrow = 1

		return nrow, ncol

	def setup(self, id, nplots, wintitle, show):

		self.nplots = nplots

		ncolspan = 1
		colspan = 1

		self.createFigure(id = id,
						  wintitle = wintitle,
						  widthplot = self.WIDTH,
						  heightplot = self.HEIGHT,
						  show=show)

		nrow, ncol = self.getSubplots()

		counter = 0
		for y in range(nrow):
			for x in range(ncol):
				self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)

	def run(self, dataOut, id, wintitle="", channelList=None,
			xmin=None, xmax=None, ymin=None, ymax=None,
			save=False, figpath='', figfile=None, show=True, wr_period=1,
			server=None, folder=None, username=None, password=None,):

		if dataOut.flagNoData:
			return None

		if channelList == None:
			channelIndexList = dataOut.channelIndexList
			channelList = dataOut.channelList
		else:
			channelIndexList = []
			for channel in channelList:
				if channel not in dataOut.channelList:
					raise ValueError, "Channel %d is not in dataOut.channelList"
				channelIndexList.append(dataOut.channelList.index(channel))

		try:
			factor = dataOut.normFactor
		except:
			factor = 1

		y = dataOut.getHeiRange()

		#for voltage
		if dataOut.type == 'Voltage':
			x = dataOut.data[channelIndexList,:] * numpy.conjugate(dataOut.data[channelIndexList,:])
			x = x.real
			x = numpy.where(numpy.isfinite(x), x, numpy.NAN)

		#for spectra
		if dataOut.type == 'Spectra':
			x = dataOut.data_spc[channelIndexList,:,:]/factor
			x = numpy.where(numpy.isfinite(x), x, numpy.NAN)
			x = numpy.average(x, axis=1)


		xdB = 10*numpy.log10(x)

		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " Power Profile %s" %(thisDatetime.strftime("%d-%b-%Y"))
		xlabel = "dB"
		ylabel = "Range (Km)"

		if not self.isConfig:

			nplots = 1

			self.setup(id=id,
					   nplots=nplots,
					   wintitle=wintitle,
					   show=show)

			if ymin == None: ymin = numpy.nanmin(y)
			if ymax == None: ymax = numpy.nanmax(y)
			if xmin == None: xmin = numpy.nanmin(xdB)*0.9
			if xmax == None: xmax = numpy.nanmax(xdB)*0.9

			self.__isConfig = True

		self.setWinTitle(title)

		title = "Power Profile: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
		axes = self.axesList[0]

		legendlabels = ["channel %d"%x for x in channelList]
		axes.pmultiline(xdB, y,
				xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
				xlabel=xlabel, ylabel=ylabel, title=title, legendlabels=legendlabels,
				ytick_visible=True, nxticks=5,
				grid='x')

		self.draw()

		if figfile == None:
			str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
			figfile = self.getFilename(name = str_datetime)

		if figpath != '':
			self.counter_imagwr += 1
			if (self.counter_imagwr>=wr_period):
				# store png plot to local folder
				self.saveFigure(figpath, figfile)
				# store png plot to FTP server according to RT-Web format
				#name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
				#ftp_filename = os.path.join(figpath, name)
				#self.saveFigure(figpath, ftp_filename)
				self.counter_imagwr = 0

class SpectraCutPlot(Figure):

	isConfig = None
	__nsubplots = None

	WIDTHPROF = None
	HEIGHTPROF = None
	PREFIX = 'spc_cut'

	def __init__(self):
		self.isConfig = False
		self.__nsubplots = 1

		self.WIDTH = 480
		self.HEIGHT = 400
		self.WIDTHPROF = 120
		self.HEIGHTPROF = 0
		self.counter_imagwr = 0

		self.PLOT_CODE = 1
		self.FTP_WEI = None
		self.EXP_CODE = None
		self.SUB_EXP_CODE = None
		self.PLOT_POS = None
		'''
		self.isConfig = False
		self.__nsubplots = 1

		self.PLOT_CODE = POWER_CODE

		self.WIDTH = 700
		self.HEIGHT = 500
		self.counter_imagwr = 0
		'''
	def getSubplots(self):
		ncol = 1
		nrow = 1

		return nrow, ncol

	def setup(self, id, nplots, wintitle, show):

		self.nplots = nplots

		ncolspan = 1
		colspan = 1

		self.createFigure(id = id,
						  wintitle = wintitle,
						  widthplot = self.WIDTH,
						  heightplot = self.HEIGHT,
						  show=show)

		nrow, ncol = self.getSubplots()

		counter = 0
		for y in range(nrow):
			for x in range(ncol):
				self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)

	def run(self, dataOut, id, wintitle="", channelList=None,
			xmin=None, xmax=None, ymin=None, ymax=None,
			save=False, figpath='./', figfile=None, show=True,
			ftp=False, wr_period=1, server=None,
			folder=None, username=None, password=None,
			xaxis="frequency"):

		if dataOut.flagNoData:
			return dataOut

		if channelList == None:
			channelIndexList = dataOut.channelIndexList
			channelList = dataOut.channelList
		else:
			channelIndexList = []
			for channel in channelList:
				if channel not in dataOut.channelList:
					raise ValueError("Channel %d is not in dataOut.channelList")
				channelIndexList.append(dataOut.channelList.index(channel))

		factor = dataOut.normFactor

		y = dataOut.getHeiRange()

		z = dataOut.data_spc/factor
		z = numpy.where(numpy.isfinite(z), z, numpy.NAN)

		hei_index = numpy.arange(25)*3 + 20 # ???

		if xaxis == "frequency":
			x = dataOut.getFreqRange()/1000.
			zdB = 10*numpy.log10(z[0,:,hei_index])
			xlabel = "Frequency (kHz)"
			ylabel = "Power (dB)"

		elif xaxis == "time":
			x = dataOut.getAcfRange()
			zdB = z[0,:,hei_index]
			xlabel = "Time (ms)"
			ylabel = "ACF"

		else:
			x = dataOut.getVelRange()
			zdB = 10*numpy.log10(z[0,:,hei_index])
			xlabel = "Velocity (m/s)"
			ylabel = "Power (dB)"

		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[0])
		title = wintitle + " Range Cuts %s" %(thisDatetime.strftime("%d-%b-%Y"))

		if not self.isConfig:

			nplots = 1

			self.setup(id=id,
					   nplots=nplots,
					   wintitle=wintitle,
					   show=show)

			if xmin == None: xmin = numpy.nanmin(x)*0.9
			if xmax == None: xmax = numpy.nanmax(x)*1.1
			if ymin == None: ymin = numpy.nanmin(zdB)
			if ymax == None: ymax = numpy.nanmax(zdB)

			self.isConfig = True

		self.setWinTitle(title)

		title = "Spectra Cuts: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
		axes = self.axesList[0]

		legendlabels = ["Range = %dKm" %y[i] for i in hei_index]

		axes.pmultilineyaxis( x, zdB,
				xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
				xlabel=xlabel, ylabel=ylabel, title=title, legendlabels=legendlabels,
				ytick_visible=True, nxticks=5,
				grid='x')

		self.draw()
		'''
		self.save(figpath=figpath,
				  figfile=figfile,
				  save=save,
				  ftp=ftp,
				  wr_period=wr_period,
				  thisDatetime=thisDatetime)
		'''
		return dataOut


class Noise(Figure):

	isConfig = None
	__nsubplots = None

	PREFIX = 'noise'

	def __init__(self):

		self.timerange = 24*60*60
		self.isConfig = False
		self.__nsubplots = 1
		self.counter_imagwr = 0
		self.WIDTH = 600
		self.HEIGHT = 300
		self.WIDTHPROF = 120
		self.HEIGHTPROF = 0
		self.xdata = None
		self.ydata = None

		self.PLOT_CODE = 17
		self.FTP_WEI = None
		self.EXP_CODE = None
		self.SUB_EXP_CODE = None
		self.PLOT_POS = None
		self.figfile = None

	def getSubplots(self):

		ncol = 1
		nrow = 1

		return nrow, ncol

	def openfile(self, filename):
		f = open(filename,'w+')
		f.write('\n\n')
		f.write('JICAMARCA RADIO OBSERVATORY - Noise \n')
		f.write('DD MM YYYY  HH MM SS   Channel0	Channel1	Channel2	Channel3\n\n' )
		f.close()

	def save_data(self, filename_phase, data, data_datetime):
		f=open(filename_phase,'a')
		timetuple_data = data_datetime.timetuple()
		day = str(timetuple_data.tm_mday)
		month = str(timetuple_data.tm_mon)
		year = str(timetuple_data.tm_year)
		hour = str(timetuple_data.tm_hour)
		minute = str(timetuple_data.tm_min)
		second = str(timetuple_data.tm_sec)
		f.write(day+' '+month+' '+year+'  '+hour+' '+minute+' '+second+'   '+str(data[0])+'   '+str(data[1])+'   '+str(data[2])+'   '+str(data[3])+'\n')
		f.close()


	def setup(self, id, nplots, wintitle, showprofile=True, show=True):

		self.__showprofile = showprofile
		self.nplots = nplots

		ncolspan = 7
		colspan = 6
		self.__nsubplots = 2

		self.createFigure(id = id,
						  wintitle = wintitle,
						  widthplot = self.WIDTH+self.WIDTHPROF,
						  heightplot = self.HEIGHT+self.HEIGHTPROF,
						  show=show)

		nrow, ncol = self.getSubplots()

		self.addAxes(nrow, ncol*ncolspan, 0, 0, colspan, 1)


	def run(self, dataOut, id, wintitle="", channelList=None, showprofile='True',
			xmin=None, xmax=None, ymin=None, ymax=None,
			timerange=None,
			save=False, figpath='', figfile=None, show=True, ftp=False, wr_period=1,
			server=None, folder=None, username=None, password=None,
			ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0):

		if channelList == None:
			channelIndexList = dataOut.channelIndexList
			channelList = dataOut.channelList
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
		x = dataOut.getTimeRange()
		y = dataOut.getHeiRange()
		factor = dataOut.normFactor
		noise = dataOut.noise/factor
		noisedB = 10*numpy.log10(noise)

		#thisDatetime = dataOut.datatime
		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " Noise" # : %s" %(thisDatetime.strftime("%d-%b-%Y"))
		xlabel = ""
		ylabel = "Intensity (dB)"

		if not self.isConfig:

			nplots = 1

			self.setup(id=id,
					   nplots=nplots,
					   wintitle=wintitle,
					   showprofile=showprofile,
					   show=show)

			tmin, tmax = self.getTimeLim(x, xmin, xmax)
			if ymin == None: ymin = numpy.nanmin(noisedB) - 10.0
			if ymax == None: ymax = numpy.nanmax(noisedB) + 10.0

			self.FTP_WEI = ftp_wei
			self.EXP_CODE = exp_code
			self.SUB_EXP_CODE = sub_exp_code
			self.PLOT_POS = plot_pos


			self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.isConfig = True
			self.figfile = figfile
			self.xdata = numpy.array([])
			self.ydata = numpy.array([])

			#open file beacon phase
			path = '%s%03d' %(self.PREFIX, self.id)
			noise_file = os.path.join(path,'%s.txt'%self.name)
			self.filename_noise = os.path.join(figpath,noise_file)
			self.openfile(self.filename_noise)


		#store data beacon phase
		self.save_data(self.filename_noise, noisedB, thisDatetime)


		self.setWinTitle(title)


		title = "Noise %s" %(thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))

		legendlabels = ["channel %d"%(idchannel+1) for idchannel in channelList]
		axes = self.axesList[0]

		self.xdata = numpy.hstack((self.xdata, x[0:1]))

		if len(self.ydata)==0:
			self.ydata = noisedB[channelIndexList].reshape(-1,1)
		else:
			self.ydata = numpy.hstack((self.ydata, noisedB[channelIndexList].reshape(-1,1)))


		axes.pmultilineyaxis(x=self.xdata, y=self.ydata,
					xmin=tmin, xmax=tmax, ymin=ymin, ymax=ymax,
					xlabel=xlabel, ylabel=ylabel, title=title, legendlabels=legendlabels, marker='x', markersize=8, linestyle="solid",
					XAxisAsTime=True, grid='both'
					)

		self.draw()

		if x[1] >= self.axesList[0].xmax:
			self.counter_imagwr = wr_period
			del self.xdata
			del self.ydata
			self.__isConfig = False

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


class BeaconPhase(Figure):

	__isConfig = None
	__nsubplots = None

	PREFIX = 'beacon_phase'

	def __init__(self):

		self.timerange = 24*60*60
		self.__isConfig = False
		self.__nsubplots = 1
		self.counter_imagwr = 0
		self.WIDTH = 600
		self.HEIGHT = 300
		self.WIDTHPROF = 120
		self.HEIGHTPROF = 0
		self.xdata = None
		self.ydata = None

		self.PLOT_CODE = 18
		self.FTP_WEI = None
		self.EXP_CODE = None
		self.SUB_EXP_CODE = None
		self.PLOT_POS = None

		self.filename_phase = None

		self.figfile = None

	def getSubplots(self):

		ncol = 1
		nrow = 1

		return nrow, ncol

	def setup(self, id, nplots, wintitle, showprofile=True, show=True):

		self.__showprofile = showprofile
		self.nplots = nplots

		ncolspan = 7
		colspan = 6
		self.__nsubplots = 2

		self.createFigure(id = id,
						  wintitle = wintitle,
						  widthplot = self.WIDTH+self.WIDTHPROF,
						  heightplot = self.HEIGHT+self.HEIGHTPROF,
						  show=show)

		nrow, ncol = self.getSubplots()

		self.addAxes(nrow, ncol*ncolspan, 0, 0, colspan, 1)

	def save_phase(self, filename_phase):
		f = open(filename_phase,'w+')
		f.write('\n\n')
		f.write('JICAMARCA RADIO OBSERVATORY - Beacon Phase \n')
		f.write('DD MM YYYY  HH MM SS   pair(2,0) pair(2,1) pair(2,3) pair(2,4)\n\n' )
		f.close()

	def save_data(self, filename_phase, data, data_datetime):
		f=open(filename_phase,'a')
		timetuple_data = data_datetime.timetuple()
		day = str(timetuple_data.tm_mday)
		month = str(timetuple_data.tm_mon)
		year = str(timetuple_data.tm_year)
		hour = str(timetuple_data.tm_hour)
		minute = str(timetuple_data.tm_min)
		second = str(timetuple_data.tm_sec)
		f.write(day+' '+month+' '+year+'  '+hour+' '+minute+' '+second+'   '+str(data[0])+'   '+str(data[1])+'   '+str(data[2])+'   '+str(data[3])+'\n')
		f.close()


	def run(self, dataOut, id, wintitle="", pairsList=None, showprofile='True',
			xmin=None, xmax=None, ymin=None, ymax=None,
			timerange=None,
			save=False, figpath='', figfile=None, show=True, ftp=False, wr_period=1,
			server=None, folder=None, username=None, password=None,
			ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0):

		if pairsList == None:
			pairsIndexList = dataOut.pairsIndexList
		else:
			pairsIndexList = []
			for pair in pairsList:
				if pair not in dataOut.pairsList:
					raise ValueError, "Pair %s is not in dataOut.pairsList" %(pair)
				pairsIndexList.append(dataOut.pairsList.index(pair))

		if pairsIndexList == []:
			return

#		 if len(pairsIndexList) > 4:
#			 pairsIndexList = pairsIndexList[0:4]

		if timerange != None:
			self.timerange = timerange

		tmin = None
		tmax = None
		x = dataOut.getTimeRange()
		y = dataOut.getHeiRange()


		#thisDatetime = dataOut.datatime
		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " Phase of Beacon Signal" # : %s" %(thisDatetime.strftime("%d-%b-%Y"))
		xlabel = "Local Time"
		ylabel = "Phase"

		nplots = len(pairsIndexList)
		#phase = numpy.zeros((len(pairsIndexList),len(dataOut.beacon_heiIndexList)))
		phase_beacon = numpy.zeros(len(pairsIndexList))
		for i in range(nplots):
			pair = dataOut.pairsList[pairsIndexList[i]]
			ccf = numpy.average(dataOut.data_cspc[pairsIndexList[i],:,:],axis=0)
			powa = numpy.average(dataOut.data_spc[pair[0],:,:],axis=0)
			powb = numpy.average(dataOut.data_spc[pair[1],:,:],axis=0)
			avgcoherenceComplex = ccf/numpy.sqrt(powa*powb)
			phase = numpy.arctan2(avgcoherenceComplex.imag, avgcoherenceComplex.real)*180/numpy.pi

			#print "Phase %d%d" %(pair[0], pair[1])
			#print phase[dataOut.beacon_heiIndexList]

			phase_beacon[i] = numpy.average(phase[dataOut.beacon_heiIndexList])

		if not self.__isConfig:

			nplots = len(pairsIndexList)

			self.setup(id=id,
					   nplots=nplots,
					   wintitle=wintitle,
					   showprofile=showprofile,
					   show=show)

			tmin, tmax = self.getTimeLim(x, xmin, xmax)
			if ymin == None: ymin = numpy.nanmin(phase_beacon) - 10.0
			if ymax == None: ymax = numpy.nanmax(phase_beacon) + 10.0

			self.FTP_WEI = ftp_wei
			self.EXP_CODE = exp_code
			self.SUB_EXP_CODE = sub_exp_code
			self.PLOT_POS = plot_pos

			self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
			self.__isConfig = True
			self.figfile = figfile
			self.xdata = numpy.array([])
			self.ydata = numpy.array([])

			#open file beacon phase
			path = '%s%03d' %(self.PREFIX, self.id)
			beacon_file = os.path.join(path,'%s.txt'%self.name)
			self.filename_phase = os.path.join(figpath,beacon_file)
			#self.save_phase(self.filename_phase)


		#store data beacon phase
		#self.save_data(self.filename_phase, phase_beacon, thisDatetime)

		self.setWinTitle(title)


		title = "Beacon Signal %s" %(thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))

		legendlabels = ["pairs %d%d"%(pair[0], pair[1]) for pair in dataOut.pairsList]

		axes = self.axesList[0]

		self.xdata = numpy.hstack((self.xdata, x[0:1]))

		if len(self.ydata)==0:
			self.ydata = phase_beacon.reshape(-1,1)
		else:
			self.ydata = numpy.hstack((self.ydata, phase_beacon.reshape(-1,1)))


		axes.pmultilineyaxis(x=self.xdata, y=self.ydata,
					xmin=tmin, xmax=tmax, ymin=ymin, ymax=ymax,
					xlabel=xlabel, ylabel=ylabel, title=title, legendlabels=legendlabels, marker='x', markersize=8, linestyle="solid",
					XAxisAsTime=True, grid='both'
					)

		self.draw()

		if x[1] >= self.axesList[0].xmax:
			self.counter_imagwr = wr_period
			del self.xdata
			del self.ydata
			self.__isConfig = False

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
