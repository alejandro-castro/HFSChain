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
import cSchainNoise
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
parser.add_argument('-show',action='store',dest='show',help='Mostrar Grafico',default=1)

########################## LOCATION AND ORIENTATION ####################################################################################################
parser.add_argument('-lo',action='store',dest='lo_seleccionado',type=int,help='Parametro para establecer la ubicacion de la estacion de Rx y su orientacion.\
                                        Example: XA   ----- X: Es el primer valor determina la ubicacion de la estacion. A: Es \
                                                  el segundo valor determina la orientacion N45O o N45E.  \
                                                    11: JRO-N450, 12: JRO-N45E \
                                                        21: HYO-N45O, 22: HYO-N45E',default=11)

########################## CHANNEL ########################################################################################################
parser.add_argument('-ch',action='store',dest='ch_seleccionado',type=int,help=' Seleccion de Canal entre 0 y 1',default=0)
###########################################################################################################################################

results    = parser.parse_args()
pathin       = str(results.path_lectura)
pathout     = str(results.path_escritura)
pathout=pathout[0:-1]

freq       = results.f_freq
if freq == 2.72 :
    freqstr= 272
    freqidx=0
else :
    freqstr= 364
    freqidx=1

code       = int(results.code_seleccionado)
date       = results.date_seleccionado
time_start = results.time_start
time_end   = results.time_end
zerodatatime = time.strptime(date,"%Y/%m/%d")
datatime   = time.strptime(date+' '+time_start,"%Y/%m/%d %H:%M:%S")
lastdatatime = time.strptime(date+' '+time_end,"%Y/%m/%d %H:%M:%S")
xticksSperation = results.xticksSperation
maxHeight = results.maxHeight
show = results.show
#


lo         = results.lo_seleccionado
channel    = results.ch_seleccionado

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

doypath=pathin+'d'+str(datatime.tm_year) +doystr+'/'#doypath='/media/ci-81/062717d4-e7c7-4462-9365-08418e5483b2/d2018076/'

PLOT_Spectras = 0
queue=[0,0,0,0,0,32655,32655]
tmp=[0,0,0,0,0,0,0]
icount=0
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
nFFTPoints = 600#Depende si es campign o normal
deltav = 2*vmax/ (nFFTPoints)# agregar comentario
extrapoints=1
velrange = deltav*(numpy.arange(nFFTPoints+extrapoints)-nFFTPoints/2.)- (deltav/2)*extrapoints

NRANGE= 1000
nSamples=1000
profile = range(nSamples)
dr=1.5
rango=range(1000)
#for i in range(NRANGE):
#    rango[i]=float(i*dr)
def GetMoments(spec,absc,n):
        '''
        Function GetMoments()

        Input:
            spec: spectrogram
            absc: abscissaList
            n : noise

        Output:
            params : -Radial velocity(DOPPLER)
                     -power
                     -spectralwidth
        '''
        #data_param = numpy.zeros((data.shape[0], 4, data.shape[2]))
        #This change has been done for HF processing
        data_param = numpy.zeros((spec.shape[0], 6, spec.shape[1])) # Jm : harcoded to show the limits frequencies
        data_param = CalculateMoments(spec, absc, n)

        return data_param

def CalculateMoments(oldspec, oldfreq, n0, nicoh = None, graph = None, smooth = None, type1 = None, fwindow = None, snrth = None, dc = None, aliasing = None, oldfd = None, wwauto = None):

    if (nicoh == None): nicoh = 1
    if (graph == None): graph = 0
    if (smooth == None): smooth = 0
    elif (smooth < 3): smooth = 0

    if (type1 == None): type1 = 0
    if (fwindow == None): fwindow = numpy.zeros(oldfreq.size) + 1 #abscissaList
    if (snrth == None): snrth = -3
    if (dc == None): dc = 0
    if (aliasing == None): aliasing = 0
    if (oldfd == None): oldfd = 0
    if (wwauto == None): wwauto = 0

    if (n0 < 1.e-20):   n0 = 1.e-20

    freq = oldfreq # Doppler velocity values
    vec_power = numpy.zeros(oldspec.shape[1])
    vec_fd = numpy.zeros(oldspec.shape[1])
    vec_w = numpy.zeros(oldspec.shape[1])
    vec_snr = numpy.zeros(oldspec.shape[1])
    vec_fv = numpy.zeros(oldspec.shape[1])#First Valid frequency
    vec_lv = numpy.zeros(oldspec.shape[1])#Last Valid Frequency

    for ind in range(oldspec.shape[1]):

        spec = oldspec[:,ind]
        #TODO : if snr = (spec2.mean()-n0)/n0 SNR es menor que 0.3dB no hagas el resto.
        #TODO : hacer un noise special para el slice metodo privado de ParametersProc
        aux = spec*fwindow[0:len(spec)] #Jm:hardcoded to match with lenghts
        max_spec = aux.max()
        m = list(aux).index(max_spec)

        #Smooth
        #TODO : probar el whitenning smooth que dio Juha
        if (smooth == 0):   spec2 = spec
        else:   spec2 = scipy.ndimage.filters.uniform_filter1d(spec,size=smooth)

        #    Calculo de Momentos
        bb = spec2[range(m,spec2.size)]
        bb = (bb<n0).nonzero()
        bb = bb[0]

        ss = spec2[range(0,m + 1)]
        ss = (ss<n0).nonzero()
        ss = ss[0]

        if (bb.size == 0):
            bb0 = spec.size - 1 - m
        else:
            bb0 = bb[0] - 1
            if (bb0 < 0):
                bb0 = 0

        if (ss.size == 0):   ss1 = 1
        else: ss1 = max(ss) + 1

        if (ss1 > m):   ss1 = m

        valid = numpy.asarray(range(int(m + bb0 - ss1 + 1))) + ss1
        #print 'valid[0]:',freq[valid[0]]
        #print 'valid[-1]:',freq[valid[-1]]
        power = ((spec2[valid] - n0)*fwindow[valid]).sum() # m_0 = first moments
        #TODO probar la estimacion de fd con el calculo de ruido por perfil.
        fd = ((spec2[valid]- n0)*freq[valid]*fwindow[valid]).sum()/power # m_1=radial velocity = frequecy doppler?
        w = math.sqrt((  (spec2[valid] - n0)*fwindow[valid]  *(freq[valid]- fd)**2   ).sum()/power)
        snr = (spec2.mean()-n0)/n0

        if (snr < 1.e-20) :
            snr = 1.e-20

        vec_power[ind] = power
        vec_fd[ind] = fd
        vec_w[ind] = w
        vec_snr[ind] = snr
        vec_fv[ind]=freq[valid[0]]
        vec_lv[ind]=freq[valid[-1]]
        #vec_sw[ind] = sw

        #else : vec_power[ind] = un numero x, fd , w y snr igual.
    moments = numpy.vstack((vec_snr, vec_power, vec_fd, vec_w,vec_fv,vec_lv))
    return moments


def hildebrand_sekhon(data, navg):
    '''
    Input : spectrogram like power-dopplerspectra, etc.
    Output: avg noise of spectrogram
    '''
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
print offsetValue
start=0

#sp21_f1 cambie para ver el otro tx
for each_ch in glob.glob(doypath+"sp%s1_f%s/"%(code,freqidx)):
    print each_ch

    files = []
    files = glob.glob("%s/*.hdf5"%(each_ch))
    files.sort()
    #files = files[837:-1]

    filesres = []
    filesres = glob.glob("%s/res-*.hdf5"%(each_ch))
    filesres.sort()


    filesspec = []
    filesspec = glob.glob("%s/spec-*.hdf5"%(each_ch))
    filesspec.sort()

    Ntime = len(files)-1 # Ideadly this number has to be 1440.

    Ntimeres = len(filesres)-1
    Ntimespec = len(filesspec)-1

    step=1
    #spc_db = numpy.empty((1000,Ntime//step,3))
    colmsnumber= 1+int(math.floor( (time.mktime(lastdatatime) - time.mktime(datatime)) / 60.0))
    #If colmsnumber is less than 5 hours
    if colmsnumber<=60*5:
        xticksSperation = 30
    #print 'colmsnumber>',colmsnumber
    spc_db = numpy.empty((1000,colmsnumber//step,3))
    spc_dop = numpy.empty((1000,1))
    count_filename=0
    XaxisValue=0
    setup = "doit"

    for filename in numpy.arange(0,Ntimespec//step):
        try:
            f = h5py.File(filesspec[filename*step], 'r')
            print "File %s %d of %d : %d "%(filesspec[filename*step],filename+1,Ntimespec//step,XaxisValue)
            time_key    = f.keys()[8]
            #data_a_matrix = numpy.array(list(filesspec[filename*step],f[a_group_key]))
            #data_a_matrix[0,:] = (data_a_matrix[-1,:] + data_a_matrix[1,:])/2.0 #RemoveDC mode 1
            #print f['t'].value # cOMES WITH DECIMAL.
            filedatatime=time.localtime(f['t'].value)
            #print 'datatime:',datatime
            #print 'initTimeXaxisValue:',initTimeXaxisValue
            #Time instances do not support the subtraction operation. Given that one way to solve this would be
            #to convert the time to seconds since epoch and then find the difference, use:
            XaxisValue= int(math.floor( (time.mktime(filedatatime) - time.mktime(datatime)) / 60.0))
            f.close()
            if filedatatime>=initTimeXaxisValue and filedatatime<=lastdatatime:
                #If data is on time, extract data
                f = h5py.File(filesspec[filename*step], 'r')
                #a_group_key = f.keys()[6] # ch 0? pw0
                #b_group_key = f.keys()[7] # ch 1? pw1
                #data_a_matrix = numpy.array(list(f[a_group_key]))
                name='pw0_C'+str(code)
                data_a_matrix = (f[name]).value
                data_a_matrix[0,:] = (data_a_matrix[-1,:] + data_a_matrix[1,:])/2.0 #RemoveDC mode 1
                data_a_matrix= data_a_matrix.swapaxes(0,1)
                data_a_matrix= data_a_matrix.real
                #data_a_matrix[:,0] = (data_a_matrix[:,0] + data_a_matrix[:,1])/2.0 #RemoveDC mode 1
                f.close()
                data_a_matrix = numpy.fft.fftshift(data_a_matrix,axes=(1,))
                data_a_matrix= data_a_matrix.transpose()
                #data_a_matrix = data_a_matrix.real
                if setup is not 'done':
                    nFFTPoints = data_a_matrix.shape[0]
                    deltav = 2.*vmax/(nFFTPoints)# agregar comentario
                    velrange = deltav*(numpy.arange(nFFTPoints+extrapoints)-nFFTPoints/2.)-(deltav/2.)*extrapoints
                    setup='done'

                #plt.imshow(10.0*numpy.log10(data_a_matrix),vmin=-110,vmax=-75,cmap='jet')
                #plt.show()
                noiselvl=hildebrand_sekhon(data_a_matrix,1)
                #print velrange
                #print 'len(velrange):',len(velrange)
                spc_dop=GetMoments(data_a_matrix,velrange,noiselvl)
                fig = plt.figure(figsize=(5,3))
                ax=fig.add_subplot(111)
                ax.plot(spc_dop[2],'r')
                ax2=ax.twinx()
                ax2.plot(10.0*numpy.log10(spc_dop[0]),'k')
                ax2.axis('auto')
                plt.show()
                threshv=0.1
                L= data_a_matrix.shape[0] # DECLARACION DE PERFILES 3 = 100
                linearfactor=L//100

                N= data_a_matrix.shape[1] #DECLARCION DE ALTURAS 1000 = 1000
                i0l=int(math.floor(L*threshv))*linearfactor #10 -> 60
                i0h=int(L-math.floor(L*threshv))*linearfactor #90 - > 540
                im=int(math.floor(L/2)) #50->300

                colm=numpy.zeros([N,3],dtype=numpy.float32)
                for ri in numpy.arange(N):
                    colm[ri,1]= numpy.sum(data_a_matrix[0:i0l,ri]) + numpy.sum(data_a_matrix[i0h:L,ri])
                    colm[ri,2]= numpy.sum(data_a_matrix[i0l:im,ri])
                    colm[ri,0]= numpy.sum(data_a_matrix[im:L,ri])

                noise=range(3)
                snr=range(3)
                sn1=-10.0
                sn2=20.0
                image=colm
                npy=image.shape[1]

                r2=min(nSamples,image.shape[0]-1)
                r1=int(r2*0.9)
                ncount=0.0
                noise[0]=noise[1]=noise[2]=0.0
                for i in range(r1,r2):
                    for j in range(0,npy):
                        if (j==0): ncount +=1
                        noise[j]+=image[i,j]

                for j in range(0,npy):
                    noise[j]/=ncount

                buffer2=numpy.zeros((1000,3),dtype='float')

                for i in range(r2):
                    for j in range(npy):
                        snr[j]=image[i,j]
                        snr[j]=(snr[j]-noise[j])/noise[j]
                        if (snr[j]>0.01):
                            snr[j]=(10.0*math.log10(snr[j])-sn1)/(sn2-sn1)
                        else:
                            snr[j]=0.0
                    #print "i",i,"snr",snr
                    buffer2[i]=snr
                #print "self.buffer2",self.buffer2
                data_img_snr=buffer2
                r2=data_img_snr.shape[0]-1 # = 999 o 1000
                RGB=data_img_snr

                for i in range(r2): #de 0 a 1000
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
                    profile[i]=data_img_snr[i][0]+data_img_snr[i][1]+data_img_snr[i][2]

                for i in range(NRANGE):
                    if (rango[i]>150/1.5 and rango[i]<600.0/1.5):
                        deriv=(-2.0*profile[i-2]-profile[i-1]+profile[i+1]+2.0*profile[i+2])/10.0
                        if (deriv>max_deriv):
                            max_deriv=deriv
                            layer=i

                queue[icount]=layer
                m=7
                for i in range(7):
                    tmp[i]=queue[i]
                bubbleSort(tmp)
                layer=tmp[m/2]
                icount=(icount+1)%m

                data_img_genaro = rango[layer]

                spc_db[data_img_genaro-2:data_img_genaro+2,XaxisValue-2:XaxisValue+2,:] =(211,211,211)
                contador+=1
                data_time_genaro= (int(filedatatime.tm_sec)/60.0 + filedatatime.tm_min)/60.0 + filedatatime.tm_hour  +0.000278
                # Extracting radialVelocity from spectral moments.
                #self.data_tmp_doppler=data_param[numpy.array(self.dataOut.channel_img),parameterIndex,:]
                #self.data_doppler=self.data_tmp_doppler[int(self.data_genaro/1.5)]# debe ser entre 1.5 porque los 1500 alturas e indices.
                #print 'int(data_img_genaro)>',int(data_img_genaro)
                #print 'spc_dop[int(data_img_genaro)]:',spc_dop[2,int(data_img_genaro)]
                #print 'what?'
                outd.append(spc_dop[2,int(data_img_genaro)])
                outt.append(data_time_genaro)
                outr.append(data_img_genaro*1.5)
            else:
                print 'Fuera de tiempo.'

        except:
            pass

    #plt.ioff()
    plt.clf()
    plt.imshow(spc_db.astype(numpy.uint8),origin='lower',aspect='auto',extent=[0+offsetValue,colmsnumber//step+offsetValue,0,maxHeight])#')#vmin=-10,vmax=30
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

    start+=1


    Out_filename = "%s/H%s%s%s%s%s%s%s.out"%(pathout,filedatatime.tm_year,doystr,lo,c_web,freqstr,code,channel)
    print 'grabando txt en > ', Out_filename
    f_out1 = open(Out_filename, 'w')
    #f_out1.write('time(s) rTEC(TECu) (T0 = %d  UT)\n'% t[0]) #For first line
    for ip in range(0,len(outt)):
        #write("%f %f  %f\n" %(data_timege,data_genaro,data_doppler))
        write_buf = "%f %f %f\n"%(outt[ip],outr[ip],outd[ip])
        f_out1.write(write_buf)
    f_out1.close
