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
        self.max_deriv=None
        self.profile=range(1000)
        self.NRANGE=1000
        self.layer=None
        self.rango=range(self.NRANGE)
        self.dr=1.5
        for i in range(self.NRANGE):
            self.rango[i]=float(i*self.dr)
        self.queue=[0,0,0,0,0,32655,32655]
        self.tmp=[0,0,0,0,0,0,0]
        self.icount=0
        self.contador=0
        self.RTDIMatrix = numpy.empty((1440,1000,3))



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
        """
        Convierte valores de Spectra a RGB
        """
        t=self.dataOut.utctime
        ch= self.dataOut.channel_img#ch es desde 0 a 5 si hubieran 6 canales
        #print 'mira humano: ',t
        s=self.data_spc[ch]
        s=numpy.fft.fftshift(s,axes=0)
        #plt.set_cmap('seismic')
        #plt.pcolormesh(10.0*numpy.log10(s))
        #plt.colorbar()
        #plt.show()
        threshv=self.dataOut.threshv
        #/g/b/r/g
        #con shift r/g/b
        L= s.shape[0] # DECLARACION DE PERFILES 3 = 100
        N= s.shape[1] #DECLARCION DE ALTURAS 1000 = 1000
        i0l=int(math.floor(L*threshv)) #10
        i0h=int(L-math.floor(L*threshv)) #90
        im=int(math.floor(L/2)) #50
        """
        print i0l
        print i0h
        print im
        print L
        print N
        """
        colm=numpy.zeros([N,3],dtype=numpy.float32)
        for ri in numpy.arange(N):
            colm[ri,1]= numpy.sum(s[0:i0l,ri]) + numpy.sum(s[i0h:L,ri])
            colm[ri,2]= numpy.sum(s[i0l:im,ri])
            colm[ri,0]= numpy.sum(s[im:L,ri])
        self.dataOut.data_img=colm
        #plt.set_cmap('seismic')
        #plt.pcolormesh(10.0*numpy.log10(colm))
        #plt.colorbar()
        #plt.show()

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
            for j in range(0,npy):
                if (j==0): ncount +=1
                noise[j]+=image[i,j]

        for j in range(0,npy):
            noise[j]/=ncount
        #print noise
        self.buffer2=numpy.zeros((1000,3),dtype='float')

        for i in range(r2):
            for j in range(npy):
                snr[j]=image[i,j]
                snr[j]=(snr[j]-noise[j])/noise[j]
                if (snr[j]>0.01):
                    snr[j]=(10.0*math.log10(snr[j])-sn1)/(sn2-sn1)
                else:
                    snr[j]=0.0
            #print "i",i,"snr",snr
            self.buffer2[i]=snr
        #print "self.buffer2",self.buffer2
        self.dataOut.data_img_snr=self.buffer2

        self.RTDIMatrix[0,0,:]=(0,0,0)
        #raw_input("Harcoded Stop")
        #plt.pcolormesh(self.buffer2)
        #plt.colorbar()
        #plt.show()

    def getImageReflexion(self):
        self.max_deriv=0
        npy=3
       #****declarar el icount, el queue ,tmp y bubble sort en otro lado
        for i in range(self.NRANGE):
            self.profile[i]=self.dataOut.data_img_snr[i][0]+self.dataOut.data_img_snr[i][1]+self.dataOut.data_img_snr[i][2]
        #print "self.profile:",self.profile[999]
        for i in range(self.NRANGE):
            if (self.rango[i]>200.0 and self.rango[i]<600.0):
                self.deriv=(-2.0*self.profile[i-2]-self.profile[i-1]+self.profile[i+1]+2.0*self.profile[i+2])/10.0
                if (self.deriv>self.max_deriv):
                    self.max_deriv=self.deriv
                    self.layer=i
        self.queue[self.icount]=self.layer
        m=7
        #print "icount: ",self.icount
        for i in range(7):
            self.tmp[i]=self.queue[i]
        self.bubbleSort(self.tmp)
        self.layer=self.tmp[m/2] # this has a value from sorting 7 values.
        self.icount=(self.icount+1)%m

        #print self.contador,self.rango[self.layer]
        self.dataOut.data_img_genaro= self.rango[self.layer] # how to know that is value is also int? from 0 to 1000?
        self.contador+=1
        self.dataOut.data_time_genaro= (int(self.dataOut.datatime.second)/60.0 + self.dataOut.datatime.minute)/60.0 + self.dataOut.datatime.hour  +0.000278   #User1 was here
        #print 'Buenos dias humano, quieres conocer la verdad tras el tiempo?:',self.dataOut.data_time_genaro         #User1 was here
        #plt.plot(self.dataOut.data_time_genaro)
        #plt.show()


    def bubbleSort(self,alist):
        for passnum in range(len(alist)-1,0,-1):
            for i in range(passnum):
                if alist[i]>alist[i+1]:
                    temp=alist[i]
                    alist[i]=alist[i+1]
                    alist[i+1]=temp


    def run(self,threshv=None,channel=None):

        self.dataOut.flagNoData= True

        if self.dataIn.type == "Parameters":
            self.dataOut.copy(self.dataIn)
            if threshv==None:
                raise ValueError,"This ImageProc.run() need THRESHV Variable"
            self.dataOut.threshv=threshv
            ##print self.dataOut.last_block,'parameter'
            self.dataOut.channel_img=channel
            self.data_spc=self.dataOut.data_pre
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
