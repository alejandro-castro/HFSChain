'''
@author: Daniel Suarez
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
			ext='.png',data_time_save=False):

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

		#tmin = None
		#tmax = None
		x = dataOut.getTimeRange()
		y = dataOut.getHeiRange()

		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		title = wintitle + " CoherenceMap" #: %s" %(thisDatetime.strftime("%d-%b-%Y"))
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

			#tmin, tmax = self.getTimeLim(x, xmin, xmax)

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
			'''
			from pprint import pprint
			print 'dataOut objects:'
			pprint(dataOut.__dict__)
			'''
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

			#print "coherencia y fase", coherence, phase
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
			self.isConfig = False
			self.figfile=None
