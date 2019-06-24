'''
Rewritten on May, 2019
The plotting library changed from plplot to pyplot because pyplot
is easier to use and much faster.
@author: Alejandro Castro
'''
import os
import datetime
import numpy
import math

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from model.proc.jroproc_base import Operation

def fmtsec(x,pos):
	return "{:02d}:{:02d}".format(int(x//60), int(x%60))


class RTDIPlot(Operation):
	__isConfig = None
	PREFIX = 'rtdi'
	WSCREEN_SPEC = 400
	HSCREEN_SPEC = 620

	def __init__(self):
		self.isConfig = False
		self.WIDTH = 800 #No se elimina porque puede servir en un futuro
		self.HEIGHT = 180
		#######################
		self.NRANGE=1000
		self.dr=1.5
		self.dt=20/3600.
		self.rango=range(self.NRANGE)
		for i in range(self.NRANGE):
			self.rango[i]=float(i*self.dr)
		##########PLOTEO####################
		self.spc_db=numpy.empty((1000,1440,3))


	def getFilename(self, name, ext='.png'):
		path = '%s%03d' %(self.PREFIX, self.id)
		filename = '%s_%s%s' %(self.PREFIX, name, ext)
		return os.path.join(path, filename)


	def getNameToStandard(self, thisDatetime, c_station_o,c_web,c_freq,c_cod_Tx,c_ch,ext='.png'):
		YEAR_STR = '%4.4d'%thisDatetime.timetuple().tm_year
		DOY_STR = '%3.3d'%thisDatetime.timetuple().tm_yday
		c_Station_o = c_station_o
		c_web=c_web
		c_freq = c_freq
		c_cod_tx = c_cod_Tx
		c_ch = c_ch

		name = YEAR_STR + DOY_STR +c_station_o+c_web+c_freq+c_cod_Tx+c_ch+ext
		return name


	def run(self, dataOut, id, wintitle="", xmin=0, xmax=24, ymin=0, ymax=1500,
			save=False, figpath='./', figfile=None, show=False, ext='.jpeg', standard=False,
			c_station_o=None,c_web=None,c_freq=None,c_cod_Tx=None,c_ch=None):

		self.id =id

		#Offset due to startTime of Reader Unit different than 00:00:00
		startTime_minutes = dataOut.startTime.hour*60 + dataOut.startTime.minute + dataOut.startTime.second/60.0
		offsetValue=int(math.floor(startTime_minutes))

		#Getting actual time and img_snr from jroproc_image
		thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
		RGB=dataOut.data_img_snr#array
		thistime = thisDatetime.time()
		XaxisValue = int(thistime.hour*60 + thistime.minute + thistime.second/60.0)

		#Normalizing the img_snr to real RGB
		r2=RGB.shape[0] # 1000
		for i in range(r2): #de 0 a 1000
			ir=max(min(int(RGB[i][0]*255),255),0)
			ig=max(min(int(RGB[i][1]*255),255),0)
			ib=max(min(int(RGB[i][2]*255),255),0)
			if (ir+ig+ib)>0: # aqui podemos insertar un filtro de color
				self.spc_db[i,XaxisValue,:] =(ir,ig,ib)

		#Doppler plot in white lines
		for i in range(len(dataOut.data_time_genaro)):# Could be data from F Region or and Region too
			time_minutes=int(dataOut.data_time_genaro[i]*60)#escalar
			rango_layer=int(dataOut.data_img_genaro[i]/1.5)#escalar
			xticksSperation = 120 # was 120hardcoded

			#Position where the maximum reflection happens
			height_high = min(999,rango_layer+2)
			height_low =  max(0,rango_layer-2)
			time_high = min(time_minutes+2, 1439)
			time_low = max(0, time_minutes-2)

			#Plotting the start of regions of interest that represents the maximum reflection
			self.spc_db[height_low:height_high,time_low:time_high,:] =(211,211,211)

		#Actual limits to the plot
		t_start = max(offsetValue, xmin*60)
		t_end = min(offsetValue+1440, xmax*60)

		plt.clf()
		plt.rcParams['figure.dpi'] = 100

		lim1 = max(1, xmin*60)
		lim2 = min(self.spc_db.shape[1]-1,xmax*60-2 )
		aux = numpy.zeros((int(ymax/1.5)-1-int(ymin/1.5),xmax*60-1 -  xmin*60, 3))


		plt.imshow(self.spc_db[int(ymin/1.5):int(ymax/1.5)-1, xmin*60: xmax*60-1,:].astype(numpy.uint8),origin='lower',
		aspect='auto',extent=[t_start, t_end, ymin,ymax])#')

		plt.gca().xaxis.set_major_formatter(mticker.FuncFormatter(fmtsec))
		plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(int(xticksSperation)))
		plt.xlabel("Local Time (hr)",color="k")
		plt.ylabel("Range (km)",color="k")
		plt.yticks(range(ymin,ymax+1,100))


		#Customizing the figure and its saving
		if wintitle != "":
			plt.title(wintitle)
		else:
			plt.title("RTDI %s"%(thisDatetime.strftime("%Y-%m-%d %H:%M:%S")))

		if figpath != '':
			figpath=figpath+"/d%s"%thisDatetime.strftime("%Y%j")

		if show:
			plt.ion()
			plt.pause(0.0001)
			plt.show()

		if save:
			if standard:
				name = self.getNameToStandard(thisDatetime,c_station_o, c_web, c_freq, c_cod_Tx, c_ch,ext=ext)
				Standard_filename = os.path.join(figpath, name)
				plt.savefig(Standard_filename)
			else:
				if figfile != None:
					plt.savefig("%s/%s%s"%(figpath, figfile, ext))
				else:
					plt.savefig("%s/%s%s"%(figpath,thisDatetime.date(),ext))


	def LookForNearestPoint(self, x, y):
		for i in range(x,x-2, -1):
			for j in range(y, y-5, -1):
				if self.spc_db[i][j][1]>250:
					print "gg"
					return (self.spc_db[i][j][0],self.spc_db[i][j][1],self.spc_db[i][j][2])
		return (0,0,0)
