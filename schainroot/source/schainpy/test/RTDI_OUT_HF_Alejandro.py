#!/usr/bin/env python
import h5py
import os
import glob
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy
import math
import argparse
#
"""
python RTDI_OUT_HF.py -path '/media/ci-81/062717d4-e7c7-4462-9365-08418e5483b2/' -C 0 -ii 6 -f 2.72216796875 -code 0 -lo 11 -date "2018/03/20" -ch 0 # modo normal
python RTDI_OUT_HF.py -path '/home/jm/Documents/2018.HF/' -C 0 -ii 6 -f 2.72216796875 -code 0 -lo 11 -date "2018/01/08" -ch 0 # modo normal
/home/jm/Documents/2018.HF/
"""
#################
parser = argparse.ArgumentParser()

parser.add_argument('-pathin',action='store',dest='path_lectura',help='Directorio de Datos \
					.Por defecto, se esta ingresando entre comillas /home/hfuser1204/HFA/',default='/home/jm/Documents/2018.HF/')

parser.add_argument('-pathout',action='store',dest='path_escritura',help='Directorio de Datos \
					.Por defecto, se esta ingresando entre comillas /home/hfuser1204/HFA/',default='/home/jm/Pictures/')
########################## FRECUENCIA ####################################################################################################
parser.add_argument('-f',action='store',dest='f_freq',type=float,help='Frecuencia en Mhz 2.72 y 3.64. Por defecto, se esta ingresando 2.72 ',default=2.72)
########################## CODIGO - INPUT ################################################################################################
parser.add_argument('-code',action='store',dest='code_seleccionado',type=int,help='Code de Tx para generar en estacion \
											de Rx Spectro 0,1,2. Por defecto, se esta ingresando 0(Ancon)',default=0)
########################## DIA CONFIG ################################################################################################
yesterday=time.localtime(time.time() - 86400)
str_yesterday=("%d/%d/%d")%(yesterday.tm_year,yesterday.tm_mon,yesterday.tm_mday)
parser.add_argument('-date',action='store',dest='date_seleccionado',help='Seleccionar fecha si es OFFLINE se ingresa \
							la fecha con el dia deseado. Por defecto, considera el dia anterior',default=str_yesterday)
######################### TIME- SELECCION ################################################################################################
parser.add_argument('-startTime',action='store',dest='time_start',help='Ingresar tiempo de inicio, formato 00:00:00 entre comillas',default="00:00:00")
parser.add_argument('-endTime',action='store',dest='time_end',help='Ingresar tiempo de fin, formato 23:59:59 entre comillas',default="23:59:59")
parser.add_argument('-xTickSpace',action='store',dest='xticksSperation',help='Ingresar la separacion de tiempo',default=120)
parser.add_argument('-maxHeight',action='store',dest='maxHeight',help='Ingresar altura maxima',default=1500)
parser.add_argument('-show',action='store',dest='show',help='Mostrar Grafico',default=0)

########################## LOCATION AND ORIENTATION ####################################################################################################
parser.add_argument('-lo',action='store',dest='lo_seleccionado',type=int,help='Parametro para establecer la ubicacion de la estacion de Rx y su orientacion.\
										Example: XA   ----- X: Es el primer valor determina la ubicacion de la estacion. A: Es \
												  el segundo valor determina la orientacion N45O o N45E.  \
													11: JRO-N450, 12: JRO-N45E \
														21: HYO-N45O, 22: HYO-N45E',default=11)

########################## CHANNEL ########################################################################################################
parser.add_argument('-ch',action='store',dest='ch_seleccionado',type=int,help=' Seleccion de Canal entre 0 y 1',default=0)
###########################################################################################################################################

results	= parser.parse_args()
pathin	   = str(results.path_lectura)
pathout	 = str(results.path_escritura)
pathout=pathout[0:-1]

freq	   = results.f_freq
if freq < 3 :
	freqstr= 272
	freqidx=0
else :
	freqstr= 364
	freqidx=1

code	   = int(results.code_seleccionado)
date	   = results.date_seleccionado
time_start = results.time_start
time_end   = results.time_end
zerodatatime = time.strptime(date,"%Y/%m/%d")
datatime   = time.strptime(date+' '+time_start,"%Y/%m/%d %H:%M:%S")
lastdatatime = time.strptime(date+' '+time_end,"%Y/%m/%d %H:%M:%S")
xticksSperation = results.xticksSperation
maxHeight = results.maxHeight
show = results.show
#


lo		 = results.lo_seleccionado
channel	= results.ch_seleccionado

ngraph= 1
if channel==0:
	c_web=6
else:
	c_web=8

if freq <3:
	ngraph= 0
	if channel==0:
		c_web=5
	else:
		c_web=7

if lo%10==1:
	status_figpath= True
else:
	status_figpath= False

if len(str(datatime.tm_yday))==2:
	doystr = '0'+str(datatime.tm_yday)
elif len(str(datatime.tm_yday))==1:
	doystr = '00'+str(datatime.tm_yday)
else :
	doystr = str(datatime.tm_yday)

pathout=    '/home/ci-81/Documents/JRO_CAMPAIGN_ALEJANDRO/Refactor/sp'+str(code)+'1_f'+str(ngraph)+'/'
parampath = '/home/ci-81/Documents/JRO_CAMPAIGN_ALEJANDRO/Refactor/sp'+str(code)+'1_f'+str(ngraph)+'/param/'

doypath=parampath+'d'+str(datatime.tm_year) +doystr+'/'#doypath='/media/ci-81/062717d4-e7c7-4462-9365-08418e5483b2/d2018076/'



PLOT_Spectras = 0
MEDIAN_FILTER_SIZE = 4
queue = [0]*MEDIAN_FILTER_SIZE
tmp = [0]*MEDIAN_FILTER_SIZE
MEDIAN_FILTER_SIZE2=3
queue2 = [0]*MEDIAN_FILTER_SIZE2
tmp2 = [0]*MEDIAN_FILTER_SIZE2
#queue[-2]=32655
#queue[-1]=32655

icount=0
icount2=0
contador=0
outr=[]
outt=[]
outd=[]
ippSeconds=0.1
nCohInt=1
ippFactor = 1
PRF = 1./(ippSeconds*nCohInt*ippFactor) #AGREGARCOMENTARIO
fmax = PRF/2.
C = 3e8
frequency = freq*1e6
_lambda = C/frequency
vmax = fmax*_lambda/2
extrapoints=1

NRANGE= 1000
nSamples=1000
profile = range(nSamples)
dr=1.5
rango=range(1000)



def bubbleSort(alist):
	for passnum in range(len(alist)-1,0,-1):
		for i in range(passnum):
			if alist[i]>alist[i+1]:
				temp=alist[i]
				alist[i]=alist[i+1]
				alist[i+1]=temp


# Format the seconds on the axis as min:sec
def fmtsec(x,pos):
	return "{:02d}:{:02d}".format(int(x//60), int(x%60))



#1) all plots are going to be from 00:00 to 23:59:59
#2) In this case the resolution is for every minute, so 1440 colms.
#3) firtstime is equal to 1, convert the first time.timelocal time to 1, them rest the same for all the times.
#4) the value to rest is comming from the date data.
initTimeXaxisValue=datatime
#5) Add starttime to init value and limit data.
#print 'time.strptime(date,time_start):',time.strptime(time_start,"%H:%M:%S")
#6) time end will reduce the colmsnumber
offsetValue=int(math.floor( (time.mktime(datatime) - time.mktime(zerodatatime)) / 60.0))

#sp21_f1 cambie para ver el otro tx

each_ch = doypath#+"sp%s1_f%s/"%(code,freqidx)
print each_ch

hdf5files = glob.glob("%s/D*.hdf5"%(each_ch))
hdf5files.sort()

Ntime = len(hdf5files)-1

colmsnumber= 1+int(math.floor( (time.mktime(lastdatatime) - time.mktime(datatime)) / 60.0))
#If colmsnumber is less than 5 hours
if colmsnumber<=60*5:
	xticksSperation = 30

spc_db = numpy.empty((1000,colmsnumber,3))

XaxisValue=0
for filename in numpy.arange(0,Ntime):
	#try:
	with h5py.File(hdf5files[filename], 'r') as fmoments:
		print "File %s %d of %d : %d "%(hdf5files[filename],filename+1,Ntime,XaxisValue)

		Data = fmoments["Data"]
		totalblocks = len(Data["utctime"][0])
		for nblock in numpy.arange(0,totalblocks):
			filedatatime=time.localtime(Data["utctime"][0][nblock])
			#Time instances do not support the subtraction operation. Given that one way to solve this would be
			#to convert the time to seconds since epoch and then find the difference, use:
			XaxisValue= int(math.floor( (time.mktime(filedatatime) - time.mktime(datatime)) / 60.0))
			if filedatatime>=initTimeXaxisValue and filedatatime<=lastdatatime:
				#If data is on time, extract data

				r2=999 # = 999 o 1000
				colm = Data["data_RGB"]["channel%d"%channel][:,:,nblock].transpose()


				##Added May 22, 2019
				sn1=-10.0
				sn2=20.0
				image=colm

				snr=range(3)


				noise=range(3)
				npy=image.shape[1]
				r2=min(nSamples,image.shape[0]-1)
				r1=int(r2*0.9)
				ncount=0.0
				noise[0]=noise[1]=noise[2]=0.0
				for i in range(r1,r2):
					ncount +=1
					for j in range(npy):
						noise[j]+=image[i,j]

				for j in range(npy):
					noise[j]/=ncount

				buffer2=numpy.zeros((1000,3),dtype='float')

				for i in range(r2):
					for j in range(npy):
						snr[j]=image[i,j]
						#print i, image[i][j]
						snr[j]=(snr[j]-noise[j])/noise[j]
						if snr[j]>200*0.01: #and image[i][j]> 1e-11*(i0h-i0l):#(image[i][j]> 1e-13) and (snr[j]>100):#snr[j]>0.1):
							snr[j]=(10.0*math.log10(snr[j])-sn1)/(sn2-sn1)
						else:
							snr[j]=0.0
					#print "i",i,"snr",snr
					buffer2[i]=snr
				#print "self.buffer2",self.buffer2
				data_img_snr=buffer2
				r2=data_img_snr.shape[0]-1 # = 999 o 1000
				RGB=data_img_snr
				## End of Added May 22, 2019




				for i in range(r2): #de 0 a 1000 Dice de 0 1000 pero siempre r2 valio 999, chequear eso ALEJANDRO
					ir=max(min(int(RGB[i][0]*255),255),0)
					ig=max(min(int(RGB[i][1]*255),255),0)
					ib=max(min(int(RGB[i][2]*255),255),0)
					#print i,filename,ir,ig,ib
					if (ir+ig+ib)>0: # aqui podemos insertar un filtro de color
						spc_db[i,XaxisValue,:] =(ir,ig,ib)
				# PART III - Getting Reflexions.

				max_deriv=0
				npy=3

				for i in range(NRANGE):
					profile[i]=RGB[i][0]+RGB[i][1]+RGB[i][2]

				layers = []
				SIZE_LIST_DERIV = 170
				list_deriv = [0]*SIZE_LIST_DERIV
				for i in range(NRANGE):

					if (rango[i]>=200/1.5 and rango[i]<600.0/1.5):
						if (i%SIZE_LIST_DERIV == 0):
							if i > 100:
								if max(list_deriv)>4*10**-9:
									pos_0 = list_deriv.index(max(list_deriv))
									layers.append(i-SIZE_LIST_DERIV+pos_0)

							#print "gg"
							list_deriv = [0]*SIZE_LIST_DERIV
						deriv=(-2.0*profile[i-2]-profile[i-1]+profile[i+1]+2.0*profile[i+2])/10.0
						list_deriv[i%SIZE_LIST_DERIV] = deriv

						# if (deriv>max_deriv):
						# 	max_deriv=deriv
						# 	layer=i

				for layer in layers:
					queue[icount]=layer

					for i in range(MEDIAN_FILTER_SIZE):
						tmp[i]=queue[i]
					bubbleSort(tmp)
					layer=tmp[MEDIAN_FILTER_SIZE/2]
					icount=(icount+1)%MEDIAN_FILTER_SIZE



					# queue2[icount2]=layer
					#
					# for i in range(MEDIAN_FILTER_SIZE2):
					# 	tmp2[i]=queue2[i]
					# bubbleSort(tmp2)
					# layer=tmp2[MEDIAN_FILTER_SIZE2/2]
					# icount2=(icount2+1)%MEDIAN_FILTER_SIZE2


					data_img_genaro = rango[layer]

					spc_db[data_img_genaro-2:data_img_genaro+2,XaxisValue-2:XaxisValue+2,:] =(211,211,211)
					contador+=1
					data_time_genaro= (int(filedatatime.tm_sec)/60.0 + filedatatime.tm_min)/60.0 + \
					filedatatime.tm_hour  + 0.000278


					outd.append(Data["data_param"]["channel%s"%channel][1, int(data_img_genaro), nblock] )
					outt.append(data_time_genaro)
					outr.append(data_img_genaro*1.5)
			else:
				print 'Fuera de tiempo.'

	#except:
	#	import sys
	#	print "Fallo el software", sys.exc_info()[0]
	#	pass

#plt.ioff()
spc_db2 = numpy.zeros((1000,colmsnumber,3))
for i in range(1000):
	for j in range(1440):
		if i> 3 and j >3 and j<1437 and i<997 and tuple(spc_db[i][j])==(211, 211, 211):
			rgb= []
			rgb.append(spc_db[i-3][j-3])
			rgb.append(spc_db[i-3][j+3])
			rgb.append(spc_db[i+3][j-3])
			rgb.append(spc_db[i+3][j+3])

			count=0
			for elem in rgb:
				if tuple(elem)==(211,211,211):
					count+=1
					pass
			if count >= 1 :
				spc_db2[i,j,:]=(211,211,211)

plt.clf()
plt.imshow(spc_db2.astype(numpy.uint8),origin='lower',aspect='auto',
extent=[0+offsetValue,colmsnumber+offsetValue,0,maxHeight])#')#vmin=-10,vmax=30

#offsetValue , este valor es e, offset value para la hora.
plt.gca().xaxis.set_major_formatter(mticker.FuncFormatter(fmtsec))
# Use nice tick positions as multiples of 30 seconds
plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(int(xticksSperation)))
#plt.gcf().autofmt_xdate()
plt.xlabel("Local Time",color="k")
plt.ylabel("Virtual Range (km)",color="k")
#plt.axis([0,24,0,1500],color="blue")#plt.plot(numpy.log10(numpy.real(power))*10.0,'--r')
#plt.xticks(range(0,24,1))
plt.yticks(range(0,1500,100))
plt.title("RTDI %s-%s-%s"%(filedatatime.tm_year,filedatatime.tm_mon,filedatatime.tm_mday))
plt.savefig("%s/%s%s%s%s%s%s%s.jpeg"%(pathout,filedatatime.tm_year,doystr,lo,c_web,freqstr,code,channel))
if show is 1:
	plt.show()



Out_filename = "%s/H%s%s%s%s%s%s%s.out"%(pathout,filedatatime.tm_year,doystr,lo,c_web,freqstr,code,channel)
print 'grabando txt en > ', Out_filename
f_out1 = open(Out_filename, 'w')
#f_out1.write('time(s) rTEC(TECu) (T0 = %d  UT)\n'% t[0]) #For first line
for ip in range(0,len(outt)):
	#write("%f %f  %f\n" %(data_timege,data_genaro,data_doppler))
	write_buf = "%f %f %f\n"%(outt[ip],outr[ip],outd[ip])
	f_out1.write(write_buf)
f_out1.close()
