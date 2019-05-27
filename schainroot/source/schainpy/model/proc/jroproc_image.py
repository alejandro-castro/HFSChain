import numpy
import math
import time,datetime
import matplotlib.pyplot as plt

from jroproc_base import ProcessingUnit, Operation
from model.data.jrodata import Image
from model.data.jrodata import hildebrand_sekhon


class ImageProc(ProcessingUnit):

	def __init__(self):

		ProcessingUnit.__init__(self)

		self.buffer= None
		self.data_spc=None
		self.buffer2=None
		self.firstdatatime= None
		self.profIndex=0
		self.dataOut=Image()
		self.id_min=None
		self.id_max= None
		self.profile=range(1000)
		self.NRANGE=1000
		self.layer1=None
		self.layer2=None
		self.rango=range(self.NRANGE)
		self.dr=1.5
		for i in range(self.NRANGE):
			self.rango[i]=float(i*self.dr)
		self.queue1=[0,0,0,0,0,32655,32655]
		self.queue2=[0,0,0,0,0,32655,32655]

		self.tmp=[0,0,0,0,0,0,0]
		self.icount1=0
		self.icount2=0

	def __updateObjFromInput(self):
		self.dataOut.timeZone=self.dataIn.timeZone
		self.dataOut.dstFlag = self.dataIn.dstFlag
		self.dataOut.errorCount =self.dataIn.errorCount
		self.dataOut.useLocalTime = self.dataIn.useLocalTime

		self.dataOut.radarControllerHeaderobj=self.dataIn.radarControllerHeaderObj.copy()
		self.dataOut.systemHeaderObj=self.dataIn.systemHeaderObj.copy()
		self.dataOut.channelList=self.dataIn.channelList
		self.dataOut.heightList= self.dataIn.heightList
		self.dataOut.nProfiles=self.dataIn.nProfiles
		self.dataOut.nCohInt =self.dataIn.nCohInt
		self.dataOut.flagTimeBlock = self.dataIn.flagTimeBlock
		self.dataOut.utctime = self.firstdatatime
		self.dataOut.flagDecodeData = self.dataIn.flagDecodeData #asumo q la data esta decodificada
		self.dataOut.flagDeflipData = self.dataIn.flagDeflipData
		self.dataOut.nIncohInt= self.dataIn.nIncohInt
		self.dataOut.frequency = self.dataIn.frequency
		self.dataOut.realtime = self.dataIn.realtime


	def __getImageRGB(self):
		if hasattr(self.dataOut, "data_RGB"):
			self.dataOut.data_img=self.dataOut.data_RGB[self.dataOut.channel_img].transpose()
		else:# for using with the normal data
			raise ValueError, "Not implemented yet"

	def getImageSNR(self):
		noise=range(3)
		snr=range(3)
		sn1=-10.0
		sn2=20.0
		image=self.dataOut.data_img
		npy=image.shape[1]
		nSamples=1000.0
		r2=min(nSamples,image.shape[0]-1)
		#print r2
		r1=int(r2*0.9)
		ncount=0.0
		noise[0]=noise[1]=noise[2]=0.0
		for i in range(r1,r2):
			ncount += 1
			for j in range(npy):
				noise[j]+=image[i,j]

		for j in range(npy):
			noise[j]/=ncount
		#print noise
		buffer2=numpy.zeros((1000,3),dtype='float')

		for i in range(r2):
			for j in range(npy):
				snr[j]=(image[i,j]-noise[j])/noise[j]
				if (snr[j]>3):
					snr[j]=(10.0*math.log10(snr[j])-sn1)/(sn2-sn1)
				else:
					snr[j]=0.0
			#print "i",i,"snr",snr
			buffer2[i]=snr[:]
		#print "self.buffer2",self.buffer2
		self.dataOut.data_img_snr=buffer2
		#print "data_img", buffer2

		#raw_input("Harcoded Stop")
		#plt.pcolormesh(self.buffer2)
		#plt.colorbar()
		#plt.show()

	def getImageReflexion(self):
		self.dataOut.data_img_genaro = []
		self.dataOut.data_time_genaro = []

		# F Region
		max_deriv=0
		for i in range(self.NRANGE):
			self.profile[i]=self.dataOut.data_img_snr[i][0]+self.dataOut.data_img_snr[i][1]+self.dataOut.data_img_snr[i][2]
		#print "self.profile:",self.profile[999]
		for i in range(self.NRANGE):
			if (self.rango[i]>=200.0 and self.rango[i]<600.0):
				deriv=(-2.0*self.profile[i-2]-self.profile[i-1]+self.profile[i+1]+2.0*self.profile[i+2])/10.0
				if (deriv>max_deriv):
					max_deriv=deriv
					self.layer1=i


		self.queue1[self.icount1]=self.layer1
		m=7
		for i in range(7):
			self.tmp[i]=self.queue1[i]
		self.bubbleSort(self.tmp)
		self.layer1=self.tmp[m/2] # this has a value from sorting 7 values.
		self.icount1=(self.icount1+1)%m

		self.dataOut.data_img_genaro.append(self.rango[self.layer1]) # how to know that is value is also int? from 0 to 1000?
		self.dataOut.data_time_genaro.append( (int(self.dataOut.datatime.second)/60.0 + self.dataOut.datatime.minute)/60.0 + self.dataOut.datatime.hour  +0.000278) #User1 was here

		#####

		# E Region
		if self.E_Region:
			max_deriv=0
			for i in range(self.NRANGE):
				if (self.rango[i]<200):
					deriv=(-2.0*self.profile[i-2]-self.profile[i-1]+self.profile[i+1]+2.0*self.profile[i+2])/10.0
					if (deriv>max_deriv):
						max_deriv=deriv
						self.layer2=i

			self.queue2[self.icount2]=self.layer2
			m=7
			for i in range(7):
				self.tmp[i]=self.queue2[i]
			self.bubbleSort(self.tmp)
			self.layer2 = self.tmp[m/2]
			self.icount2=(self.icount2+1)%m

			self.dataOut.data_img_genaro.append(self.rango[self.layer2]) # how to know that is value is also int? from 0 to 1000?
			self.dataOut.data_time_genaro.append( (int(self.dataOut.datatime.second)/60.0 + self.dataOut.datatime.minute)/60.0 + self.dataOut.datatime.hour  +0.000278) #User1 was here

		####

	def bubbleSort(self,alist):
		for passnum in range(len(alist)-1,0,-1):
			for i in range(passnum):
				if alist[i]>alist[i+1]:
					temp=alist[i]
					alist[i]=alist[i+1]
					alist[i+1]=temp


	def run(self,threshv=None,channel=None, E_Region = False):

		self.dataOut.flagNoData= True
		self.E_Region = E_Region

		if self.dataIn.type == "Parameters":
			self.dataOut.copy(self.dataIn)
			# if threshv==None:
			# 	raise ValueError,"This ImageProc.run() need THRESHV Variable"
			# self.dataOut.threshv=threshv
			##print self.dataOut.last_block,'parameter'
			self.dataOut.channel_img=channel
			# self.data_spc=self.dataOut.data_pre
			self.__getImageRGB()
			self.getImageSNR()
			self.getImageReflexion()


			return True

		if self.dataIn.type== "Spectra":
			self.dataOut.copy(self.dataIn)
			if threshv==None:
				raise ValueError,"This ImageProc.run() need THRESHV Variable"
			self.dataOut.threshv=threshv
			self.dataOut.channel_img=channel
			#self.buffer= numpy.zeros((self.dataIn.nChannels,3,self.dataIn.nHeights),dtype='complex')

			self.__getImageRGB()
			self.getImageSNR()
			self.getImageReflexion()


			return True
		if self.dataIn.type =="Voltage":
			pass
