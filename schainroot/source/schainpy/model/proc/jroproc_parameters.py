import numpy
import math
#from scipy import optimize
#from scipy import interpolate
#from scipy import signal
#from scipy import stats
import re
import datetime
import copy
import sys
import importlib
import itertools

from jroproc_base import ProcessingUnit, Operation
from model.data.jrodata import Parameters
import matplotlib.pyplot


class ParametersProc(ProcessingUnit):

    nSeconds = None

    def __init__(self):
        ProcessingUnit.__init__(self)
#         self.objectDict = {}
        self.buffer = None
        self.firstdatatime = None
        self.profIndex = 0
        self.dataOut = Parameters()

    def __updateObjFromInput(self):

        self.dataOut.inputUnit = self.dataIn.type

        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.dstFlag = self.dataIn.dstFlag
        self.dataOut.errorCount = self.dataIn.errorCount
        self.dataOut.useLocalTime = self.dataIn.useLocalTime

        self.dataOut.radarControllerHeaderObj = self.dataIn.radarControllerHeaderObj.copy()
        self.dataOut.systemHeaderObj = self.dataIn.systemHeaderObj.copy()
        self.dataOut.channelList = self.dataIn.channelList
        self.dataOut.heightList = self.dataIn.heightList
        self.dataOut.dtype = numpy.dtype([('real','<f4'),('imag','<f4')])
#         self.dataOut.nHeights = self.dataIn.nHeights
#         self.dataOut.nChannels = self.dataIn.nChannels
        self.dataOut.nBaud = self.dataIn.nBaud
        self.dataOut.nCode = self.dataIn.nCode
        self.dataOut.code = self.dataIn.code
#        self.dataOut.nProfiles = self.dataOut.nFFTPoints
        self.dataOut.flagTimeBlock = self.dataIn.flagTimeBlock
        self.dataOut.utctime = self.firstdatatime
        self.dataOut.flagDecodeData = self.dataIn.flagDecodeData #asumo q la data esta decodificada
        self.dataOut.flagDeflipData = self.dataIn.flagDeflipData #asumo q la data esta sin flip
#        self.dataOut.nCohInt = self.dataIn.nCohInt
#        self.dataOut.nIncohInt = 1
        self.dataOut.ippSeconds = self.dataIn.ippSeconds
#        self.dataOut.windowOfFilter = self.dataIn.windowOfFilter
        self.dataOut.timeInterval = self.dataIn.timeInterval
        self.dataOut.heightList = self.dataIn.getHeiRange()
        self.dataOut.frequency = self.dataIn.frequency
        #Jm: TODO merge : This changes has been done for HF proccesing
        self.dataOut.data_RGB = self.dataIn.Image
        self.dataOut.CrossData = numpy.zeros((self.dataIn.nChannels,
                                                2,
                                                self.dataIn.nHeights),
                                                dtype='f')

    def run(self, nSeconds = None, nProfiles = None):
        #raw_input("self.dataIn.type: %s"%(self.dataIn.type))

        if self.firstdatatime == None:
            self.firstdatatime = self.dataIn.utctime

        #----------------------    Voltage Data    ---------------------------

        if self.dataIn.type == "Voltage":
            self.dataOut.flagNoData = True
            if nSeconds != None:
                self.nSeconds = nSeconds
                self.nProfiles= int(numpy.floor(nSeconds/(self.dataIn.ippSeconds*self.dataIn.nCohInt)))

            if self.buffer == None:
                    self.buffer = numpy.zeros((self.dataIn.nChannels,
                                               self.nProfiles,
                                               self.dataIn.nHeights),
                                               dtype='complex')

            self.buffer[:,self.profIndex,:] = self.dataIn.data.copy()
            self.profIndex += 1

            if self.profIndex == self.nProfiles:

                self.__updateObjFromInput()
                self.dataOut.data_pre = self.buffer.copy()
                self.dataOut.paramInterval = nSeconds
                self.dataOut.flagNoData = False

                self.buffer = None
                self.firstdatatime = None
                self.profIndex = 0
                return

        #----------------------    Spectra Data    ---------------------------

        if self.dataIn.type == "Spectra":
            self.dataOut.data_pre = self.dataIn.data_spc.copy()
            #self.dataOut.abscissaList = self.dataIn.getVelRange(0)
            self.dataOut.abscissaList = self.dataIn.getVelRange(1)
	    #print "CALCULO DEL RUIDO"
            self.dataOut.noise = self.dataIn.getNoise()
            self.dataOut.normFactor = self.dataIn.normFactor
            self.dataOut.groupList = self.dataIn.pairsList
            self.dataOut.flagNoData = False

        #----------------------    Correlation Data    ---------------------------
        if self.dataIn.type == "Correlation":
            lagRRange = self.dataIn.lagR
            indR = numpy.where(lagRRange == 0)[0][0]

            self.dataOut.data_pre = self.dataIn.data_corr.copy()[:,:,indR,:]
            self.dataOut.abscissaList = self.dataIn.getLagTRange(1)
            self.dataOut.noise = self.dataIn.noise
            self.dataOut.normFactor = self.dataIn.normFactor
            self.dataOut.data_SNR = self.dataIn.SNR
            self.dataOut.groupList = self.dataIn.pairsList
            self.dataOut.flagNoData = False

        #----------------------    Parameters Data    ---------------------------

        if self.dataIn.type == "Parameters":
            self.dataOut.copy(self.dataIn)
            self.dataOut.flagNoData = False

            #Just for HF - its hardcoded
            self.dataOut.outputInterval = 60
            self.dataOut.timeInterval = 60
            self.dataOut.ippSeconds= 0.1
            #self.dataOut.abscissaList = self.dataOut.getVelRange(1)

            return True

        self.__updateObjFromInput()
        self.firstdatatime = None
        self.dataOut.utctimeInit = self.dataIn.utctime
        self.dataOut.outputInterval = self.dataIn.timeInterval

    def GetCrossData(self):
        #Jm: TODO merge : This changes has been done for HF proccesing
        pairsIndexList = []

        for pair in self.dataIn.pairsList:
            pairsIndexList.append(self.dataIn.pairsList.index(pair))

        for i in range(0,len(pairsIndexList)):
            ccf = numpy.average(self.dataIn.data_cspc[pairsIndexList[i],:,:],axis=0)
            powa = numpy.average(self.dataIn.data_spc[0,:,:],axis=0)
            powb = numpy.average(self.dataIn.data_spc[1,:,:],axis=0)
            avgcoherenceComplex = ccf/numpy.sqrt(powa*powb)
            #Array dimensions fails when the array is 1x1000, why?
            self.dataOut.CrossData[:,0,:] = numpy.abs(avgcoherenceComplex)
            self.dataOut.CrossData[:,1,:] = numpy.arctan2(avgcoherenceComplex.imag, avgcoherenceComplex.real)*180/numpy.pi
            #self.dataOut.AvgCoh[0,:] = numpy.abs(avgcoherenceComplex)
            #self.dataOut.AvgCoh[1,:] = numpy.arctan2(avgcoherenceComplex.imag, avgcoherenceComplex.real)*180/numpy.pi
            #print 'self.dataOut.AvgCohModule.shape:',(numpy.abs(avgcoherenceComplex)).shape
            #print 'self.dataOut.AvgCohPhase.shape:',(self.dataOut.AvgCohPhase).shape
            #coherenceComplex = self.dataIn.data_cspc[pairsIndexList[i],:,:]/numpy.sqrt(self.dataIn.data_spc[0,:,:]*self.dataIn.data_spc[1,:,:])
            #self.dataOut.CohModule = numpy.abs(coherenceComplex)
            #phase = numpy.arctan(-1*coherenceComplex.imag/coherenceComplex.real)*180/numpy.pi
            #self.dataOut.CohPhase = numpy.arctan2(coherenceComplex.imag, coherenceComplex.real)*180/numpy.pi

    #Defini los argumentos de entrara para que sean posibles parametros de entrada.

    def GetRGBData(self):
        #TODO > any future operation do here
        #self.dataOut.data_RGB = self.dataIn.Image
        print "Getting RGB Data from Image dataset..."


    def GetVelData(self,nFFTPoints=None,nProfiles=None,ippFactor=None,pairsList=""):
        #TODO > any future operation do here
        #self.dataOut.data_RGB = self.dataIn.Image
        #raw_input("Calculando Velocidades.")

        if nFFTPoints == None:
            print "Ingresar numero de FFT"

        self.dataOut.ippFactor = 1
        self.dataOut.nFFTPoints = nFFTPoints
        #print 'self.dataOut.nFFTPoints:',self.dataOut.nFFTPoints
        self.dataOut.pairsList = pairsList
        self.dataOut.nCohInt = 6
        self.dataOut.abscissaList = self.dataOut.getVelRange(1)
    #-------------------    Get Moments    ----------------------------------
    def GetMoments(self, channelList = None):
        '''
        Function GetMoments()

        Input:
            channelList    :    simple channel list to select e.g. [2,3,7]
            self.dataOut.data_pre
            self.dataOut.abscissaList
            self.dataOut.noise

        Affected:
            self.dataOut.data_param
            self.dataOut.data_SNR

        '''
        data = self.dataOut.data_pre
        absc = self.dataOut.abscissaList#
        noise = self.dataOut.noise

        #data_param = numpy.zeros((data.shape[0], 4, data.shape[2]))
        #This change has been done for HF processing
        data_param = numpy.zeros((data.shape[0], 6, data.shape[2])) # Jm : harcoded to show the limits frequencies
        if channelList== None:
            channelList = self.dataIn.channelList
        self.dataOut.channelList = channelList

        #plt.plot(10.0*numpy.log10(data[0,:,:][500,:][-201:-1]))
        #plt.imshow(10.0*numpy.log10(data[0,:,:]),vmin=-110,vmax=-75,cmap='jet')
        #plt.show()

        for ind in channelList:
            data_param[ind,:,:] = self.__calculateMoments(data[ind,:,:], absc, noise[ind])

        #print 'spc_dop>',data_param[0,0,:]
        print 'noises:',10.0*numpy.log10(noise[0])
        #print 'absc:',absc

        #import matplotlib.pyplot as plt
        #plt.imshow(10.0*numpy.log10(data[0,:,:]),vmin=-110,vmax=-75,cmap='jet')
        #plt.show()
        #plt.plot(data_param[0,2,:],'g')
        #raw_input("testing")
        self.dataOut.data_param = data_param[:,1:,:]#drop first colm
        self.dataOut.data_SNR = data_param[:,0]
        return

    def __calculateMoments(self, oldspec, oldfreq, n0, nicoh = None, graph = None, smooth = None, type1 = None, fwindow = None, snrth = None, dc = None, aliasing = None, oldfd = None, wwauto = None):

        if (nicoh == None): nicoh = 1
        if (graph == None): graph = 0
        if (smooth == None): smooth = 0
        elif (self.smooth < 3): smooth = 0

        if (type1 == None): type1 = 0
        if (fwindow == None): fwindow = numpy.zeros(oldfreq.size) + 1
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

    #------------------    Get SA Parameters    --------------------------
    def GetSAParameters(self):
        data = self.dataOut.data_pre
        crossdata = self.dataIn.data_cspc
        a = 1

    #-------------------    Get Lags    ----------------------------------

    def GetLags(self):
        '''
        Function GetMoments()

        Input:
            self.dataOut.data_pre
            self.dataOut.abscissaList
            self.dataOut.noise
            self.dataOut.normFactor
            self.dataOut.data_SNR
            self.dataOut.groupList
            self.dataOut.nChannels

        Affected:
            self.dataOut.data_param

        '''

        data = self.dataOut.data_pre
        normFactor = self.dataOut.normFactor
        nHeights = self.dataOut.nHeights
        absc = self.dataOut.abscissaList[:-1]
        noise = self.dataOut.noise
        SNR = self.dataOut.data_SNR
        pairsList = self.dataOut.groupList
        nChannels = self.dataOut.nChannels
        pairsAutoCorr, pairsCrossCorr = self.__getPairsAutoCorr(pairsList, nChannels)
        self.dataOut.data_param = numpy.zeros((len(pairsCrossCorr)*2 + 1, nHeights))

        dataNorm = numpy.abs(data)
        for l in range(len(pairsList)):
            dataNorm[l,:,:] = dataNorm[l,:,:]/normFactor[l,:]

        self.dataOut.data_param[:-1,:] = self.__calculateTaus(dataNorm, pairsCrossCorr, pairsAutoCorr, absc)
        self.dataOut.data_param[-1,:] = self.__calculateLag1Phase(data, pairsAutoCorr, absc)
        return

    def __getPairsAutoCorr(self, pairsList, nChannels):

        pairsAutoCorr = numpy.zeros(nChannels, dtype = 'int')*numpy.nan

        for l in range(len(pairsList)):
            firstChannel = pairsList[l][0]
            secondChannel = pairsList[l][1]

            #Obteniendo pares de Autocorrelacion
            if firstChannel == secondChannel:
                pairsAutoCorr[firstChannel] = int(l)

        pairsAutoCorr = pairsAutoCorr.astype(int)

        pairsCrossCorr = range(len(pairsList))
        pairsCrossCorr = numpy.delete(pairsCrossCorr,pairsAutoCorr)

        return pairsAutoCorr, pairsCrossCorr

    def __calculateTaus(self, data, pairsCrossCorr, pairsAutoCorr, lagTRange):

        Pt0 = data.shape[1]/2
        #Funcion de Autocorrelacion
        dataAutoCorr = stats.nanmean(data[pairsAutoCorr,:,:], axis = 0)

        #Obtencion Indice de TauCross
        indCross = data[pairsCrossCorr,:,:].argmax(axis = 1)
        #Obtencion Indice de TauAuto
        indAuto = numpy.zeros(indCross.shape,dtype = 'int')
        CCValue = data[pairsCrossCorr,Pt0,:]
        for i in range(pairsCrossCorr.size):
            indAuto[i,:] = numpy.abs(dataAutoCorr - CCValue[i,:]).argmin(axis = 0)

        #Obtencion de TauCross y TauAuto
        tauCross = lagTRange[indCross]
        tauAuto  = lagTRange[indAuto]

        Nan1, Nan2 = numpy.where(tauCross == lagTRange[0])

        tauCross[Nan1,Nan2] = numpy.nan
        tauAuto[Nan1,Nan2] = numpy.nan
        tau = numpy.vstack((tauCross,tauAuto))

        return tau

    def __calculateLag1Phase(self, data, pairs, lagTRange):
        data1 = stats.nanmean(data[pairs,:,:], axis = 0)
        lag1 = numpy.where(lagTRange == 0)[0][0] + 1

        phase = numpy.angle(data1[lag1,:])

        return phase
        #-------------------    Detect Meteors  ------------------------------

    def DetectMeteors(self, hei_ref = None, tauindex = 0,
                      predefinedPhaseShifts = None, centerReceiverIndex = 2,
                      cohDetection = False, cohDet_timeStep = 1, cohDet_thresh = 25,
                      noise_timeStep = 4, noise_multiple = 4,
                      multDet_timeLimit = 1, multDet_rangeLimit = 3,
                      phaseThresh = 20, SNRThresh = 8,
                      hmin = 70, hmax=110, azimuth = 0) :

        '''
        Function DetectMeteors()
            Project developed with paper:
            HOLDSWORTH ET AL. 2004

        Input:
            self.dataOut.data_pre

            centerReceiverIndex:      From the channels, which is the center receiver

            hei_ref:                  Height reference for the Beacon signal extraction
            tauindex:
            predefinedPhaseShifts:    Predefined phase offset for the voltge signals

            cohDetection:             Whether to user Coherent detection or not
            cohDet_timeStep:          Coherent Detection calculation time step
            cohDet_thresh:            Coherent Detection phase threshold to correct phases

            noise_timeStep:           Noise calculation time step
            noise_multiple:           Noise multiple to define signal threshold

            multDet_timeLimit:        Multiple Detection Removal time limit in seconds
            multDet_rangeLimit:       Multiple Detection Removal range limit in km

            phaseThresh:              Maximum phase difference between receiver to be consider a meteor
            SNRThresh:                Minimum SNR threshold of the meteor signal to be consider a meteor

            hmin:                     Minimum Height of the meteor to use it in the further wind estimations
            hmax:                     Maximum Height of the meteor to use it in the further wind estimations
            azimuth:                  Azimuth angle correction

        Affected:
            self.dataOut.data_param

        Rejection Criteria (Errors):
            0: No error; analysis OK
            1: SNR < SNR threshold
            2: angle of arrival (AOA) ambiguously determined
            3: AOA estimate not feasible
            4: Large difference in AOAs obtained from different antenna baselines
            5: echo at start or end of time series
            6: echo less than 5 examples long; too short for analysis
            7: echo rise exceeds 0.3s
            8: echo decay time less than twice rise time
            9: large power level before echo
            10: large power level after echo
            11: poor fit to amplitude for estimation of decay time
            12: poor fit to CCF phase variation for estimation of radial drift velocity
            13: height unresolvable echo: not valid height within 70 to 110 km
            14: height ambiguous echo: more then one possible height within 70 to 110 km
            15: radial drift velocity or projected horizontal velocity exceeds 200 m/s
            16: oscilatory echo, indicating event most likely not an underdense echo

            17: phase difference in meteor Reestimation

        Data Storage:
            Meteors for Wind Estimation   (8):
            Day    Hour    |    Range    Height
            Azimuth    Zenith    errorCosDir
            VelRad    errorVelRad
            TypeError

         '''
        #Get Beacon signal
        newheis = numpy.where(self.dataOut.heightList>self.dataOut.radarControllerHeaderObj.Taus[tauindex])

        if hei_ref != None:
            newheis = numpy.where(self.dataOut.heightList>hei_ref)

        heiRang = self.dataOut.getHeiRange()
        #Pairs List
        pairslist = []
        nChannel = self.dataOut.nChannels
        for i in range(nChannel):
            if i != centerReceiverIndex:
                pairslist.append((centerReceiverIndex,i))

        #****************REMOVING HARDWARE PHASE DIFFERENCES***************
        # see if the user put in pre defined phase shifts
        voltsPShift = self.dataOut.data_pre.copy()

        if predefinedPhaseShifts != None:
            hardwarePhaseShifts = numpy.array(predefinedPhaseShifts)*numpy.pi/180
        else:
            #get hardware phase shifts using beacon signal
            hardwarePhaseShifts = self.__getHardwarePhaseDiff(self.dataOut.data_pre, pairslist, newheis, 10)
            hardwarePhaseShifts = numpy.insert(hardwarePhaseShifts,centerReceiverIndex,0)

        voltsPShift = numpy.zeros((self.dataOut.data_pre.shape[0],self.dataOut.data_pre.shape[1],self.dataOut.data_pre.shape[2]), dtype = 'complex')
        for i in range(self.dataOut.data_pre.shape[0]):
            voltsPShift[i,:,:] = self.__shiftPhase(self.dataOut.data_pre[i,:,:], hardwarePhaseShifts[i])
        #******************END OF REMOVING HARDWARE PHASE DIFFERENCES*********

        #Remove DC
        voltsDC = numpy.mean(voltsPShift,1)
        voltsDC = numpy.mean(voltsDC,1)
        for i in range(voltsDC.shape[0]):
            voltsPShift[i] = voltsPShift[i] - voltsDC[i]

        #Don't considerate last heights, theyre used to calculate Hardware Phase Shift
        voltsPShift = voltsPShift[:,:,:newheis[0][0]]

        #************ FIND POWER OF DATA W/COH OR NON COH DETECTION (3.4) **********
        #Coherent Detection
        if cohDetection:
            #use coherent detection to get the net power
            cohDet_thresh = cohDet_thresh*numpy.pi/180
            voltsPShift = self.__coherentDetection(voltsPShift, cohDet_timeStep, self.dataOut.timeInterval, pairslist, cohDet_thresh)

        #Non-coherent detection!
        powerNet = numpy.nansum(numpy.abs(voltsPShift[:,:,:])**2,0)
        #********** END OF COH/NON-COH POWER CALCULATION**********************

        #********** FIND THE NOISE LEVEL AND POSSIBLE METEORS ****************
        #Get noise
        noise, noise1 = self.__getNoise(powerNet, noise_timeStep, self.dataOut.timeInterval)
#         noise = self.getNoise1(powerNet, noise_timeStep, self.dataOut.timeInterval)
        #Get signal threshold
        signalThresh = noise_multiple*noise
        #Meteor echoes detection
        listMeteors = self.__findMeteors(powerNet, signalThresh)
        #******* END OF NOISE LEVEL AND POSSIBLE METEORS CACULATION **********

        #************** REMOVE MULTIPLE DETECTIONS (3.5) ***************************
        #Parameters
        heiRange = self.dataOut.getHeiRange()
        rangeInterval = heiRange[1] - heiRange[0]
        rangeLimit = multDet_rangeLimit/rangeInterval
        timeLimit = multDet_timeLimit/self.dataOut.timeInterval
        #Multiple detection removals
        listMeteors1 = self.__removeMultipleDetections(listMeteors, rangeLimit, timeLimit)
        #************ END OF REMOVE MULTIPLE DETECTIONS **********************

        #*********************     METEOR REESTIMATION  (3.7, 3.8, 3.9, 3.10)   ********************
        #Parameters
        phaseThresh = phaseThresh*numpy.pi/180
        thresh = [phaseThresh, noise_multiple, SNRThresh]
        #Meteor reestimation  (Errors N 1, 6, 12, 17)
        listMeteors2, listMeteorsPower, listMeteorsVolts = self.__meteorReestimation(listMeteors1, voltsPShift, pairslist, thresh, noise, self.dataOut.timeInterval, self.dataOut.frequency)
#         listMeteors2, listMeteorsPower, listMeteorsVolts = self.meteorReestimation3(listMeteors2, listMeteorsPower, listMeteorsVolts, voltsPShift, pairslist, thresh, noise)
        #Estimation of decay times (Errors N 7, 8, 11)
        listMeteors3 = self.__estimateDecayTime(listMeteors2, listMeteorsPower, self.dataOut.timeInterval, self.dataOut.frequency)
        #*******************     END OF METEOR REESTIMATION    *******************

        #*********************    METEOR PARAMETERS CALCULATION (3.11, 3.12, 3.13)    **************************
        #Calculating Radial Velocity (Error N 15)
        radialStdThresh = 10
        listMeteors4 = self.__getRadialVelocity(listMeteors3, listMeteorsVolts, radialStdThresh, pairslist, self.dataOut.timeInterval)

        if len(listMeteors4) > 0:
            #Setting New Array
            date = repr(self.dataOut.datatime)
            arrayMeteors4, arrayParameters = self.__setNewArrays(listMeteors4, date, heiRang)

            #Calculate AOA (Error N 3, 4)
            #JONES ET AL. 1998
            AOAthresh = numpy.pi/8
            error = arrayParameters[:,-1]
            phases = -arrayMeteors4[:,9:13]
            pairsList = []
            pairsList.append((0,3))
            pairsList.append((1,2))
            arrayParameters[:,4:7], arrayParameters[:,-1] = self.__getAOA(phases, pairsList, error, AOAthresh, azimuth)

            #Calculate Heights (Error N 13 and 14)
            error = arrayParameters[:,-1]
            Ranges = arrayParameters[:,2]
            zenith = arrayParameters[:,5]
            arrayParameters[:,3], arrayParameters[:,-1] = self.__getHeights(Ranges, zenith, error, hmin, hmax)
        #*********************    END OF PARAMETERS CALCULATION    **************************

        #***************************+     SAVE DATA IN HDF5 FORMAT    **********************
            self.dataOut.data_param = arrayParameters

        return

    def __getHardwarePhaseDiff(self, voltage0, pairslist, newheis, n):

        minIndex = min(newheis[0])
        maxIndex = max(newheis[0])

        voltage = voltage0[:,:,minIndex:maxIndex+1]
        nLength = voltage.shape[1]/n
        nMin = 0
        nMax = 0
        phaseOffset = numpy.zeros((len(pairslist),n))

        for i in range(n):
            nMax += nLength
            phaseCCF = -numpy.angle(self.__calculateCCF(voltage[:,nMin:nMax,:], pairslist, [0]))
            phaseCCF = numpy.mean(phaseCCF, axis = 2)
            phaseOffset[:,i] = phaseCCF.transpose()
            nMin = nMax
#         phaseDiff, phaseArrival = self.estimatePhaseDifference(voltage, pairslist)

        #Remove Outliers
        factor = 2
        wt = phaseOffset - signal.medfilt(phaseOffset,(1,5))
        dw = numpy.std(wt,axis = 1)
        dw = dw.reshape((dw.size,1))
        ind = numpy.where(numpy.logical_or(wt>dw*factor,wt<-dw*factor))
        phaseOffset[ind] = numpy.nan
        phaseOffset = stats.nanmean(phaseOffset, axis=1)

        return phaseOffset

    def __shiftPhase(self, data, phaseShift):
        #this will shift the phase of a complex number
        dataShifted = numpy.abs(data) * numpy.exp((numpy.angle(data)+phaseShift)*1j)
        return dataShifted

    def __estimatePhaseDifference(self, array, pairslist):
        nChannel = array.shape[0]
        nHeights = array.shape[2]
        numPairs = len(pairslist)
#         phaseCCF = numpy.zeros((nChannel, 5, nHeights))
        phaseCCF = numpy.angle(self.__calculateCCF(array, pairslist, [-2,-1,0,1,2]))

        #Correct phases
        derPhaseCCF = phaseCCF[:,1:,:] - phaseCCF[:,0:-1,:]
        indDer = numpy.where(numpy.abs(derPhaseCCF) > numpy.pi)

        if indDer[0].shape[0] > 0:
            for i in range(indDer[0].shape[0]):
                signo = -numpy.sign(derPhaseCCF[indDer[0][i],indDer[1][i],indDer[2][i]])
                phaseCCF[indDer[0][i],indDer[1][i]+1:,:] += signo*2*numpy.pi

#         for j in range(numSides):
#             phaseCCFAux = self.calculateCCF(arrayCenter, arraySides[j,:,:], [-2,1,0,1,2])
#             phaseCCF[j,:,:] = numpy.angle(phaseCCFAux)
#
        #Linear
        phaseInt = numpy.zeros((numPairs,1))
        angAllCCF = phaseCCF[:,[0,1,3,4],0]
        for j in range(numPairs):
            fit = stats.linregress([-2,-1,1,2],angAllCCF[j,:])
            phaseInt[j] = fit[1]
        #Phase Differences
        phaseDiff = phaseInt - phaseCCF[:,2,:]
        phaseArrival = phaseInt.reshape(phaseInt.size)

        #Dealias
        indAlias = numpy.where(phaseArrival > numpy.pi)
        phaseArrival[indAlias] -= 2*numpy.pi
        indAlias = numpy.where(phaseArrival < -numpy.pi)
        phaseArrival[indAlias] += 2*numpy.pi

        return phaseDiff, phaseArrival

    def __coherentDetection(self, volts, timeSegment, timeInterval, pairslist, thresh):
        #this function will run the coherent detection used in Holdworth et al. 2004 and return the net power
        #find the phase shifts of each channel over 1 second intervals
        #only look at ranges below the beacon signal
        numProfPerBlock = numpy.ceil(timeSegment/timeInterval)
        numBlocks = int(volts.shape[1]/numProfPerBlock)
        numHeights = volts.shape[2]
        nChannel = volts.shape[0]
        voltsCohDet = volts.copy()

        pairsarray = numpy.array(pairslist)
        indSides = pairsarray[:,1]
#         indSides = numpy.array(range(nChannel))
#         indSides = numpy.delete(indSides, indCenter)
#
#         listCenter = numpy.array_split(volts[indCenter,:,:], numBlocks, 0)
        listBlocks = numpy.array_split(volts, numBlocks, 1)

        startInd = 0
        endInd = 0

        for i in range(numBlocks):
            startInd = endInd
            endInd = endInd + listBlocks[i].shape[1]

            arrayBlock = listBlocks[i]
#             arrayBlockCenter = listCenter[i]

            #Estimate the Phase Difference
            phaseDiff, aux = self.__estimatePhaseDifference(arrayBlock, pairslist)
            #Phase Difference RMS
            arrayPhaseRMS = numpy.abs(phaseDiff)
            phaseRMSaux = numpy.sum(arrayPhaseRMS < thresh,0)
            indPhase = numpy.where(phaseRMSaux==4)
            #Shifting
            if indPhase[0].shape[0] > 0:
                for j in range(indSides.size):
                    arrayBlock[indSides[j],:,indPhase] = self.__shiftPhase(arrayBlock[indSides[j],:,indPhase], phaseDiff[j,indPhase].transpose())
                voltsCohDet[:,startInd:endInd,:] = arrayBlock

        return voltsCohDet

    def __calculateCCF(self, volts, pairslist ,laglist):

        nHeights = volts.shape[2]
        nPoints = volts.shape[1]
        voltsCCF = numpy.zeros((len(pairslist), len(laglist), nHeights),dtype = 'complex')

        for i in range(len(pairslist)):
            volts1 = volts[pairslist[i][0]]
            volts2 = volts[pairslist[i][1]]

            for t in range(len(laglist)):
                idxT = laglist[t]
                if idxT >= 0:
                    vStacked = numpy.vstack((volts2[idxT:,:],
                                           numpy.zeros((idxT, nHeights),dtype='complex')))
                else:
                    vStacked = numpy.vstack((numpy.zeros((-idxT, nHeights),dtype='complex'),
                                           volts2[:(nPoints + idxT),:]))
                voltsCCF[i,t,:] = numpy.sum((numpy.conjugate(volts1)*vStacked),axis=0)

                vStacked = None
        return voltsCCF

    def __getNoise(self, power, timeSegment, timeInterval):

        numProfPerBlock = numpy.ceil(timeSegment/timeInterval)
        numBlocks = int(power.shape[0]/numProfPerBlock)
        numHeights = power.shape[1]

        listPower = numpy.array_split(power, numBlocks, 0)
        noise = numpy.zeros((power.shape[0], power.shape[1]))
        noise1 = numpy.zeros((power.shape[0], power.shape[1]))

        startInd = 0
        endInd = 0

        for i in range(numBlocks):             #split por canal
            startInd = endInd
            endInd = endInd + listPower[i].shape[0]

            arrayBlock = listPower[i]
            noiseAux = numpy.mean(arrayBlock, 0)
#             noiseAux = numpy.median(noiseAux)
#             noiseAux = numpy.mean(arrayBlock)
            noise[startInd:endInd,:] = noise[startInd:endInd,:] + noiseAux

            noiseAux1 = numpy.mean(arrayBlock)
            noise1[startInd:endInd,:] = noise1[startInd:endInd,:] + noiseAux1

        return noise, noise1

    def __findMeteors(self, power, thresh):
        nProf = power.shape[0]
        nHeights = power.shape[1]
        listMeteors = []

        for i in range(nHeights):
            powerAux = power[:,i]
            threshAux = thresh[:,i]

            indUPthresh = numpy.where(powerAux > threshAux)[0]
            indDNthresh = numpy.where(powerAux <= threshAux)[0]

            j = 0

            while (j < indUPthresh.size - 2):
                if (indUPthresh[j + 2] == indUPthresh[j] + 2):
                    indDNAux = numpy.where(indDNthresh > indUPthresh[j])
                    indDNthresh = indDNthresh[indDNAux]

                    if (indDNthresh.size > 0):
                        indEnd = indDNthresh[0] - 1
                        indInit = indUPthresh[j]

                        meteor = powerAux[indInit:indEnd + 1]
                        indPeak = meteor.argmax() + indInit
                        FLA = sum(numpy.conj(meteor)*numpy.hstack((meteor[1:],0)))

                        listMeteors.append(numpy.array([i,indInit,indPeak,indEnd,FLA])) #CHEQUEAR!!!!!
                        j = numpy.where(indUPthresh == indEnd)[0] + 1
                    else: j+=1
                else: j+=1

        return listMeteors

    def __removeMultipleDetections(self,listMeteors, rangeLimit, timeLimit):

        arrayMeteors = numpy.asarray(listMeteors)
        listMeteors1 = []

        while arrayMeteors.shape[0] > 0:
            FLAs = arrayMeteors[:,4]
            maxFLA = FLAs.argmax()
            listMeteors1.append(arrayMeteors[maxFLA,:])

            MeteorInitTime = arrayMeteors[maxFLA,1]
            MeteorEndTime = arrayMeteors[maxFLA,3]
            MeteorHeight = arrayMeteors[maxFLA,0]

            #Check neighborhood
            maxHeightIndex = MeteorHeight + rangeLimit
            minHeightIndex = MeteorHeight - rangeLimit
            minTimeIndex = MeteorInitTime - timeLimit
            maxTimeIndex = MeteorEndTime + timeLimit

            #Check Heights
            indHeight = numpy.logical_and(arrayMeteors[:,0] >= minHeightIndex, arrayMeteors[:,0] <= maxHeightIndex)
            indTime = numpy.logical_and(arrayMeteors[:,3] >= minTimeIndex, arrayMeteors[:,1] <= maxTimeIndex)
            indBoth = numpy.where(numpy.logical_and(indTime,indHeight))

            arrayMeteors = numpy.delete(arrayMeteors, indBoth, axis = 0)

        return listMeteors1

    def __meteorReestimation(self, listMeteors, volts, pairslist, thresh, noise, timeInterval,frequency):
        numHeights = volts.shape[2]
        nChannel = volts.shape[0]

        thresholdPhase = thresh[0]
        thresholdNoise = thresh[1]
        thresholdDB = float(thresh[2])

        thresholdDB1 = 10**(thresholdDB/10)
        pairsarray = numpy.array(pairslist)
        indSides = pairsarray[:,1]

        pairslist1 = list(pairslist)
        pairslist1.append((0,1))
        pairslist1.append((3,4))

        listMeteors1 = []
        listPowerSeries = []
        listVoltageSeries = []
        #volts has the war data

        if frequency == 30e6:
            timeLag = 45*10**-3
        else:
            timeLag = 15*10**-3
        lag = numpy.ceil(timeLag/timeInterval)

        for i in range(len(listMeteors)):

            ######################   3.6 - 3.7 PARAMETERS REESTIMATION    #########################
            meteorAux = numpy.zeros(16)

            #Loading meteor Data (mHeight, mStart, mPeak, mEnd)
            mHeight = listMeteors[i][0]
            mStart = listMeteors[i][1]
            mPeak = listMeteors[i][2]
            mEnd = listMeteors[i][3]

            #get the volt data between the start and end times of the meteor
            meteorVolts = volts[:,mStart:mEnd+1,mHeight]
            meteorVolts = meteorVolts.reshape(meteorVolts.shape[0], meteorVolts.shape[1], 1)

            #3.6. Phase Difference estimation
            phaseDiff, aux = self.__estimatePhaseDifference(meteorVolts, pairslist)

            #3.7. Phase difference removal & meteor start, peak and end times reestimated
            #meteorVolts0.- all Channels, all Profiles
            meteorVolts0 = volts[:,:,mHeight]
            meteorThresh = noise[:,mHeight]*thresholdNoise
            meteorNoise = noise[:,mHeight]
            meteorVolts0[indSides,:] = self.__shiftPhase(meteorVolts0[indSides,:], phaseDiff) #Phase Shifting
            powerNet0 = numpy.nansum(numpy.abs(meteorVolts0)**2, axis = 0)  #Power

            #Times reestimation
            mStart1 = numpy.where(powerNet0[:mPeak] < meteorThresh[:mPeak])[0]
            if mStart1.size > 0:
                mStart1 = mStart1[-1] + 1

            else:
                mStart1 = mPeak

            mEnd1 = numpy.where(powerNet0[mPeak:] < meteorThresh[mPeak:])[0][0] + mPeak - 1
            mEndDecayTime1 = numpy.where(powerNet0[mPeak:] < meteorNoise[mPeak:])[0]
            if mEndDecayTime1.size == 0:
                mEndDecayTime1 = powerNet0.size
            else:
                mEndDecayTime1 = mEndDecayTime1[0] + mPeak - 1
#             mPeak1 = meteorVolts0[mStart1:mEnd1 + 1].argmax()

            #meteorVolts1.- all Channels, from start to end
            meteorVolts1 = meteorVolts0[:,mStart1:mEnd1 + 1]
            meteorVolts2 = meteorVolts0[:,mPeak + lag:mEnd1 + 1]
            if meteorVolts2.shape[1] == 0:
                meteorVolts2 = meteorVolts0[:,mPeak:mEnd1 + 1]
            meteorVolts1 = meteorVolts1.reshape(meteorVolts1.shape[0], meteorVolts1.shape[1], 1)
            meteorVolts2 = meteorVolts2.reshape(meteorVolts2.shape[0], meteorVolts2.shape[1], 1)
            #####################    END PARAMETERS REESTIMATION    #########################

            #####################   3.8 PHASE DIFFERENCE REESTIMATION  ########################
#             if mEnd1 - mStart1 > 4:       #Error Number 6: echo less than 5 samples long; too short for analysis
            if meteorVolts2.shape[1] > 0:
                #Phase Difference re-estimation
                phaseDiff1, phaseDiffint = self.__estimatePhaseDifference(meteorVolts2, pairslist1)   #Phase Difference Estimation
#                 phaseDiff1, phaseDiffint = self.estimatePhaseDifference(meteorVolts2, pairslist)
                meteorVolts2 = meteorVolts2.reshape(meteorVolts2.shape[0], meteorVolts2.shape[1])
                phaseDiff11 = numpy.reshape(phaseDiff1, (phaseDiff1.shape[0],1))
                meteorVolts2[indSides,:] = self.__shiftPhase(meteorVolts2[indSides,:], phaseDiff11[0:4])     #Phase Shifting

                #Phase Difference RMS
                phaseRMS1 = numpy.sqrt(numpy.mean(numpy.square(phaseDiff1)))
                powerNet1 = numpy.nansum(numpy.abs(meteorVolts1[:,:])**2,0)
                #Data from Meteor
                mPeak1 = powerNet1.argmax() + mStart1
                mPeakPower1 = powerNet1.max()
                noiseAux = sum(noise[mStart1:mEnd1 + 1,mHeight])
                mSNR1 = (sum(powerNet1)-noiseAux)/noiseAux
                Meteor1 = numpy.array([mHeight, mStart1, mPeak1, mEnd1, mPeakPower1, mSNR1, phaseRMS1])
                Meteor1 = numpy.hstack((Meteor1,phaseDiffint))
                PowerSeries  = powerNet0[mStart1:mEndDecayTime1 + 1]
                #Vectorize
                meteorAux[0:7] = [mHeight, mStart1, mPeak1, mEnd1, mPeakPower1, mSNR1, phaseRMS1]
                meteorAux[7:11] = phaseDiffint[0:4]

                #Rejection Criterions
                if phaseRMS1 > thresholdPhase:  #Error Number 17: Phase variation
                    meteorAux[-1] = 17
                elif mSNR1 < thresholdDB1:      #Error Number 1: SNR < threshold dB
                    meteorAux[-1] = 1


            else:
                meteorAux[0:4] = [mHeight, mStart, mPeak, mEnd]
                meteorAux[-1] = 6 #Error Number 6: echo less than 5 samples long; too short for analysis
                PowerSeries = 0

            listMeteors1.append(meteorAux)
            listPowerSeries.append(PowerSeries)
            listVoltageSeries.append(meteorVolts1)

        return listMeteors1, listPowerSeries, listVoltageSeries

    def __estimateDecayTime(self, listMeteors, listPower, timeInterval, frequency):

        threshError = 10
        #Depending if it is 30 or 50 MHz
        if frequency == 30e6:
            timeLag = 45*10**-3
        else:
            timeLag = 15*10**-3
        lag = numpy.ceil(timeLag/timeInterval)

        listMeteors1 = []

        for i in range(len(listMeteors)):
            meteorPower = listPower[i]
            meteorAux = listMeteors[i]

            if meteorAux[-1] == 0:

                try:
                    indmax = meteorPower.argmax()
                    indlag = indmax + lag

                    y = meteorPower[indlag:]
                    x = numpy.arange(0, y.size)*timeLag

                    #first guess
                    a = y[0]
                    tau = timeLag
                    #exponential fit
                    popt, pcov = optimize.curve_fit(self.__exponential_function, x, y, p0 = [a, tau])
                    y1 = self.__exponential_function(x, *popt)
                    #error estimation
                    error = sum((y - y1)**2)/(numpy.var(y)*(y.size - popt.size))

                    decayTime = popt[1]
                    riseTime = indmax*timeInterval
                    meteorAux[11:13] = [decayTime, error]

                    #Table items 7, 8 and 11
                    if (riseTime > 0.3):            #Number 7: Echo rise exceeds 0.3s
                        meteorAux[-1] = 7
                    elif (decayTime < 2*riseTime) : #Number 8: Echo decay time less than than twice rise time
                        meteorAux[-1] = 8
                    if (error > threshError):       #Number 11: Poor fit to amplitude for estimation of decay time
                        meteorAux[-1] = 11


                except:
                    meteorAux[-1] = 11


            listMeteors1.append(meteorAux)

        return listMeteors1

    #Exponential Function

    def __exponential_function(self, x, a, tau):
        y = a*numpy.exp(-x/tau)
        return y

    def __getRadialVelocity(self, listMeteors, listVolts, radialStdThresh, pairslist,  timeInterval):

        pairslist1 = list(pairslist)
        pairslist1.append((0,1))
        pairslist1.append((3,4))
        numPairs = len(pairslist1)
        #Time Lag
        timeLag = 45*10**-3
        c = 3e8
        lag = numpy.ceil(timeLag/timeInterval)
        freq = 30e6

        listMeteors1 = []

        for i in range(len(listMeteors)):
            meteor = listMeteors[i]
            meteorAux = numpy.hstack((meteor[:-1], 0, 0, meteor[-1]))
            if meteor[-1] == 0:
                mStart = listMeteors[i][1]
                mPeak = listMeteors[i][2]
                mLag = mPeak - mStart + lag

                #get the volt data between the start and end times of the meteor
                meteorVolts = listVolts[i]
                meteorVolts = meteorVolts.reshape(meteorVolts.shape[0], meteorVolts.shape[1], 1)

                #Get CCF
                allCCFs = self.__calculateCCF(meteorVolts, pairslist1, [-2,-1,0,1,2])

                #Method 2
                slopes = numpy.zeros(numPairs)
                time = numpy.array([-2,-1,1,2])*timeInterval
                angAllCCF = numpy.angle(allCCFs[:,[0,1,3,4],0])

                #Correct phases
                derPhaseCCF = angAllCCF[:,1:] - angAllCCF[:,0:-1]
                indDer = numpy.where(numpy.abs(derPhaseCCF) > numpy.pi)

                if indDer[0].shape[0] > 0:
                    for i in range(indDer[0].shape[0]):
                        signo = -numpy.sign(derPhaseCCF[indDer[0][i],indDer[1][i]])
                        angAllCCF[indDer[0][i],indDer[1][i]+1:] += signo*2*numpy.pi

#                     fit = scipy.stats.linregress(numpy.array([-2,-1,1,2])*timeInterval, numpy.array([phaseLagN2s[i],phaseLagN1s[i],phaseLag1s[i],phaseLag2s[i]]))
                for j in range(numPairs):
                    fit = stats.linregress(time, angAllCCF[j,:])
                    slopes[j] = fit[0]

                #Remove Outlier
#                 indOut = numpy.argmax(numpy.abs(slopes - numpy.mean(slopes)))
#                 slopes = numpy.delete(slopes,indOut)
#                 indOut = numpy.argmax(numpy.abs(slopes - numpy.mean(slopes)))
#                 slopes = numpy.delete(slopes,indOut)

                radialVelocity = -numpy.mean(slopes)*(0.25/numpy.pi)*(c/freq)
                radialError = numpy.std(slopes)*(0.25/numpy.pi)*(c/freq)
                meteorAux[-2] = radialError
                meteorAux[-3] = radialVelocity

                #Setting Error
                #Number 15: Radial Drift velocity or projected horizontal velocity exceeds 200 m/s
                if numpy.abs(radialVelocity) > 200:
                    meteorAux[-1] = 15
                #Number 12: Poor fit to CCF variation for estimation of radial drift velocity
                elif radialError > radialStdThresh:
                    meteorAux[-1] = 12

            listMeteors1.append(meteorAux)
        return listMeteors1

    def __setNewArrays(self, listMeteors, date, heiRang):

        #New arrays
        arrayMeteors = numpy.array(listMeteors)
        arrayParameters = numpy.zeros((len(listMeteors),10))

        #Date inclusion
        date = re.findall(r'\((.*?)\)', date)
        date = date[0].split(',')
        date = map(int, date)
        date = [date[0]*10000 + date[1]*100 + date[2], date[3]*10000 + date[4]*100 + date[5]]
        arrayDate = numpy.tile(date, (len(listMeteors), 1))

        #Meteor array
        arrayMeteors[:,0] = heiRang[arrayMeteors[:,0].astype(int)]
        arrayMeteors = numpy.hstack((arrayDate, arrayMeteors))

        #Parameters Array
        arrayParameters[:,0:3] = arrayMeteors[:,0:3]
        arrayParameters[:,-3:] = arrayMeteors[:,-3:]

        return arrayMeteors, arrayParameters

    def __getAOA(self, phases, pairsList, error, AOAthresh, azimuth):

        arrayAOA = numpy.zeros((phases.shape[0],3))
        cosdir0, cosdir = self.__getDirectionCosines(phases, pairsList)

        arrayAOA[:,:2] = self.__calculateAOA(cosdir, azimuth)
        cosDirError = numpy.sum(numpy.abs(cosdir0 - cosdir), axis = 1)
        arrayAOA[:,2] = cosDirError

        azimuthAngle = arrayAOA[:,0]
        zenithAngle = arrayAOA[:,1]

        #Setting Error
        #Number 3: AOA not fesible
        indInvalid = numpy.where(numpy.logical_and((numpy.logical_or(numpy.isnan(zenithAngle), numpy.isnan(azimuthAngle))),error == 0))[0]
        error[indInvalid] = 3
        #Number 4: Large difference in AOAs obtained from different antenna baselines
        indInvalid = numpy.where(numpy.logical_and(cosDirError > AOAthresh,error == 0))[0]
        error[indInvalid] = 4
        return arrayAOA, error

    def __getDirectionCosines(self, arrayPhase, pairsList):

        #Initializing some variables
        ang_aux = numpy.array([-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8])*2*numpy.pi
        ang_aux = ang_aux.reshape(1,ang_aux.size)

        cosdir = numpy.zeros((arrayPhase.shape[0],2))
        cosdir0 = numpy.zeros((arrayPhase.shape[0],2))


        for i in range(2):
            #First Estimation
            phi0_aux = arrayPhase[:,pairsList[i][0]] + arrayPhase[:,pairsList[i][1]]
            #Dealias
            indcsi = numpy.where(phi0_aux > numpy.pi)
            phi0_aux[indcsi] -= 2*numpy.pi
            indcsi = numpy.where(phi0_aux < -numpy.pi)
            phi0_aux[indcsi] += 2*numpy.pi
            #Direction Cosine 0
            cosdir0[:,i] = -(phi0_aux)/(2*numpy.pi*0.5)

            #Most-Accurate Second Estimation
            phi1_aux =  arrayPhase[:,pairsList[i][0]] - arrayPhase[:,pairsList[i][1]]
            phi1_aux = phi1_aux.reshape(phi1_aux.size,1)
            #Direction Cosine 1
            cosdir1 = -(phi1_aux + ang_aux)/(2*numpy.pi*4.5)

            #Searching the correct Direction Cosine
            cosdir0_aux = cosdir0[:,i]
            cosdir0_aux = cosdir0_aux.reshape(cosdir0_aux.size,1)
            #Minimum Distance
            cosDiff = (cosdir1 - cosdir0_aux)**2
            indcos = cosDiff.argmin(axis = 1)
            #Saving Value obtained
            cosdir[:,i] = cosdir1[numpy.arange(len(indcos)),indcos]

        return cosdir0, cosdir

    def __calculateAOA(self, cosdir, azimuth):
        cosdirX = cosdir[:,0]
        cosdirY = cosdir[:,1]

        zenithAngle = numpy.arccos(numpy.sqrt(1 - cosdirX**2 - cosdirY**2))*180/numpy.pi
        azimuthAngle = numpy.arctan2(cosdirX,cosdirY)*180/numpy.pi + azimuth #0 deg north, 90 deg east
        angles = numpy.vstack((azimuthAngle, zenithAngle)).transpose()

        return angles

    def __getHeights(self, Ranges, zenith, error, minHeight, maxHeight):

        Ramb = 375  #Ramb = c/(2*PRF)
        Re = 6371   #Earth Radius
        heights = numpy.zeros(Ranges.shape)

        R_aux = numpy.array([0,1,2])*Ramb
        R_aux = R_aux.reshape(1,R_aux.size)

        Ranges = Ranges.reshape(Ranges.size,1)

        Ri = Ranges + R_aux
        hi = numpy.sqrt(Re**2 + Ri**2 + (2*Re*numpy.cos(zenith*numpy.pi/180)*Ri.transpose()).transpose()) - Re

        #Check if there is a height between 70 and 110 km
        h_bool = numpy.sum(numpy.logical_and(hi > minHeight, hi < maxHeight), axis = 1)
        ind_h = numpy.where(h_bool == 1)[0]

        hCorr = hi[ind_h, :]
        ind_hCorr = numpy.where(numpy.logical_and(hi > minHeight, hi < maxHeight))

        hCorr = hi[ind_hCorr]
        heights[ind_h] = hCorr

        #Setting Error
        #Number 13: Height unresolvable echo: not valid height within 70 to 110 km
        #Number 14: Height ambiguous echo: more than one possible height within 70 to 110 km

        indInvalid2 = numpy.where(numpy.logical_and(h_bool > 1, error == 0))[0]
        error[indInvalid2] = 14
        indInvalid1 = numpy.where(numpy.logical_and(h_bool == 0, error == 0))[0]
        error[indInvalid1] = 13

        return heights, error

    def SpectralFitting(self, getSNR = True, path=None, file=None, groupList=None):

        '''
        Function GetMoments()

        Input:
        Output:
        Variables modified:
        '''
        #que carajo es esto? que importan?
        if path != None:
            sys.path.append(path)
        self.dataOut.library = importlib.import_module(file)

        #To be inserted as a parameter
        groupArray = numpy.array(groupList)
#         groupArray = numpy.array([[0,1],[2,3]])
        self.dataOut.groupList = groupArray

        nGroups = groupArray.shape[0]
        nChannels = self.dataIn.nChannels
        nHeights=self.dataIn.heightList.size

        #Parameters Array
        self.dataOut.data_param = None

        #Set constants
        constants = self.dataOut.library.setConstants(self.dataIn)
        self.dataOut.constants = constants
        M = self.dataIn.normFactor
        N = self.dataIn.nFFTPoints
        ippSeconds = self.dataIn.ippSeconds
        K = self.dataIn.nIncohInt
        pairsArray = numpy.array(self.dataIn.pairsList)

        #List of possible combinations
        listComb = itertools.combinations(numpy.arange(groupArray.shape[1]),2)
        indCross = numpy.zeros(len(list(listComb)), dtype = 'int')

        if getSNR:
            listChannels = groupArray.reshape((groupArray.size))
            listChannels.sort()
            noise = self.dataIn.getNoise()
            self.dataOut.data_SNR = self.__getSNR(self.dataIn.data_spc[listChannels,:,:], noise[listChannels])

        for i in range(nGroups):
            coord = groupArray[i,:]

            #Input data array
            data = self.dataIn.data_spc[coord,:,:]/(M*N)
            data = data.reshape((data.shape[0]*data.shape[1],data.shape[2]))

            #Cross Spectra data array for Covariance Matrixes
            ind = 0
            for pairs in listComb:
                pairsSel = numpy.array([coord[x],coord[y]])
                indCross[ind] = int(numpy.where(numpy.all(pairsArray == pairsSel, axis = 1))[0][0])
                ind += 1
            dataCross = self.dataIn.data_cspc[indCross,:,:]/(M*N)
            dataCross = dataCross**2/K

            for h in range(nHeights):
#                 print self.dataOut.heightList[h]

                #Input
                d = data[:,h]

                #Covariance Matrix
                D = numpy.diag(d**2/K)
                ind = 0
                for pairs in listComb:
                    #Coordinates in Covariance Matrix
                    x = pairs[0]
                    y = pairs[1]
                    #Channel Index
                    S12 = dataCross[ind,:,h]
                    D12 = numpy.diag(S12)
                    #Completing Covariance Matrix with Cross Spectras
                    D[x*N:(x+1)*N,y*N:(y+1)*N] = D12
                    D[y*N:(y+1)*N,x*N:(x+1)*N] = D12
                    ind += 1
                Dinv=numpy.linalg.inv(D)
                L=numpy.linalg.cholesky(Dinv)
                LT=L.T

                dp = numpy.dot(LT,d)

                #Initial values
                data_spc = self.dataIn.data_spc[coord,:,h]

                if (h>0)and(error1[3]<5):
                    p0 = self.dataOut.data_param[i,:,h-1]
                else:
                    p0 = numpy.array(self.dataOut.library.initialValuesFunction(data_spc, constants, i))

                try:
                    #Least Squares
                    minp,covp,infodict,mesg,ier = optimize.leastsq(self.__residFunction,p0,args=(dp,LT,constants),full_output=True)
#                   minp,covp = optimize.leastsq(self.__residFunction,p0,args=(dp,LT,constants))
                    #Chi square error
                    error0 = numpy.sum(infodict['fvec']**2)/(2*N)
                    #Error with Jacobian
                    error1 = self.dataOut.library.errorFunction(minp,constants,LT)
                except:
                    minp = p0*numpy.nan
                    error0 = numpy.nan
                    error1 = p0*numpy.nan

                #Save
                if self.dataOut.data_param == None:
                    self.dataOut.data_param = numpy.zeros((nGroups, p0.size, nHeights))*numpy.nan
                    self.dataOut.data_error = numpy.zeros((nGroups, p0.size + 1, nHeights))*numpy.nan

                self.dataOut.data_error[i,:,h] = numpy.hstack((error0,error1))
                self.dataOut.data_param[i,:,h] = minp
        return


    def __residFunction(self, p, dp, LT, constants):

        fm = self.dataOut.library.modelFunction(p, constants)
        fmp=numpy.dot(LT,fm)

        return  dp-fmp

    def __getSNR(self, z, noise):

        avg = numpy.average(z, axis=1)
        SNR = (avg.T-noise)/noise
        SNR = SNR.T
        return SNR

    def __chisq(p,chindex,hindex):
        #similar to Resid but calculates CHI**2
        [LT,d,fm]=setupLTdfm(p,chindex,hindex)
        dp=numpy.dot(LT,d)
        fmp=numpy.dot(LT,fm)
        chisq=numpy.dot((dp-fmp).T,(dp-fmp))
        return chisq



class WindProfiler(Operation):

    __isConfig = False

    __initime = None
    __lastdatatime = None
    __integrationtime = None

    __buffer = None

    __dataReady = False

    __firstdata = None

    n = None

    def __init__(self):
        Operation.__init__(self)

    def __calculateCosDir(self, elev, azim):
        zen = (90 - elev)*numpy.pi/180
        azim = azim*numpy.pi/180
        cosDirX = numpy.sqrt((1-numpy.cos(zen)**2)/((1+numpy.tan(azim)**2)))
        cosDirY = numpy.sqrt(1-numpy.cos(zen)**2-cosDirX**2)

        signX = numpy.sign(numpy.cos(azim))
        signY = numpy.sign(numpy.sin(azim))

        cosDirX = numpy.copysign(cosDirX, signX)
        cosDirY = numpy.copysign(cosDirY, signY)
        return cosDirX, cosDirY

    def __calculateAngles(self, theta_x, theta_y, azimuth):

        dir_cosw = numpy.sqrt(1-theta_x**2-theta_y**2)
        zenith_arr = numpy.arccos(dir_cosw)
        azimuth_arr = numpy.arctan2(theta_x,theta_y) + azimuth*math.pi/180

        dir_cosu = numpy.sin(azimuth_arr)*numpy.sin(zenith_arr)
        dir_cosv = numpy.cos(azimuth_arr)*numpy.sin(zenith_arr)

        return azimuth_arr, zenith_arr, dir_cosu, dir_cosv, dir_cosw

    def __calculateMatA(self, dir_cosu, dir_cosv, dir_cosw, horOnly):

#
        if horOnly:
            A = numpy.c_[dir_cosu,dir_cosv]
        else:
            A = numpy.c_[dir_cosu,dir_cosv,dir_cosw]
        A = numpy.asmatrix(A)
        A1 = numpy.linalg.inv(A.transpose()*A)*A.transpose()

        return A1

    def __correctValues(self, heiRang, phi, velRadial, SNR):
        listPhi = phi.tolist()
        maxid = listPhi.index(max(listPhi))
        minid = listPhi.index(min(listPhi))

        rango = range(len(phi))
   #     rango = numpy.delete(rango,maxid)

        heiRang1 = heiRang*math.cos(phi[maxid])
        heiRangAux = heiRang*math.cos(phi[minid])
        indOut = (heiRang1 < heiRangAux[0]).nonzero()
        heiRang1 = numpy.delete(heiRang1,indOut)

        velRadial1 = numpy.zeros([len(phi),len(heiRang1)])
        SNR1 = numpy.zeros([len(phi),len(heiRang1)])

        for i in rango:
            x = heiRang*math.cos(phi[i])
            y1 = velRadial[i,:]
            f1 = interpolate.interp1d(x,y1,kind = 'cubic')

            x1 = heiRang1
            y11 = f1(x1)

            y2 = SNR[i,:]
            f2 = interpolate.interp1d(x,y2,kind = 'cubic')
            y21 = f2(x1)

            velRadial1[i,:] = y11
            SNR1[i,:] = y21

        return heiRang1, velRadial1, SNR1

    def __calculateVelUVW(self, A, velRadial):

        #Operacion Matricial
#         velUVW = numpy.zeros((velRadial.shape[1],3))
#         for ind in range(velRadial.shape[1]):
#             velUVW[ind,:] = numpy.dot(A,velRadial[:,ind])
#         velUVW = velUVW.transpose()
        velUVW = numpy.zeros((A.shape[0],velRadial.shape[1]))
        velUVW[:,:] = numpy.dot(A,velRadial)


        return velUVW

    def techniqueDBS(self, velRadial0, dirCosx, disrCosy, azimuth, correct, horizontalOnly, heiRang, SNR0):
        """
        Function that implements Doppler Beam Swinging (DBS) technique.

        Input:    Radial velocities, Direction cosines (x and y) of the Beam, Antenna azimuth,
                    Direction correction (if necessary), Ranges and SNR

        Output:    Winds estimation (Zonal, Meridional and Vertical)

        Parameters affected:    Winds, height range, SNR
        """
        azimuth_arr, zenith_arr, dir_cosu, dir_cosv, dir_cosw = self.__calculateAngles(dirCosx, disrCosy, azimuth)
        heiRang1, velRadial1, SNR1 = self.__correctValues(heiRang, zenith_arr, correct*velRadial0, SNR0)
        A = self.__calculateMatA(dir_cosu, dir_cosv, dir_cosw, horizontalOnly)

        #Calculo de Componentes de la velocidad con DBS
        winds = self.__calculateVelUVW(A,velRadial1)

        return winds, heiRang1, SNR1

    def __calculateDistance(self, posx, posy, pairsCrossCorr, pairsList, pairs, azimuth = None):

        posx = numpy.asarray(posx)
        posy = numpy.asarray(posy)

        #Rotacion Inversa para alinear con el azimuth
        if azimuth!= None:
            azimuth = azimuth*math.pi/180
            posx1 = posx*math.cos(azimuth) + posy*math.sin(azimuth)
            posy1 = -posx*math.sin(azimuth) + posy*math.cos(azimuth)
        else:
            posx1 = posx
            posy1 = posy

        #Calculo de Distancias
        distx = numpy.zeros(pairsCrossCorr.size)
        disty = numpy.zeros(pairsCrossCorr.size)
        dist = numpy.zeros(pairsCrossCorr.size)
        ang = numpy.zeros(pairsCrossCorr.size)

        for i in range(pairsCrossCorr.size):
            distx[i] = posx1[pairsList[pairsCrossCorr[i]][1]] - posx1[pairsList[pairsCrossCorr[i]][0]]
            disty[i] = posy1[pairsList[pairsCrossCorr[i]][1]] - posy1[pairsList[pairsCrossCorr[i]][0]]
            dist[i] = numpy.sqrt(distx[i]**2 + disty[i]**2)
            ang[i] = numpy.arctan2(disty[i],distx[i])
        #Calculo de Matrices
        nPairs = len(pairs)
        ang1 = numpy.zeros((nPairs, 2, 1))
        dist1 = numpy.zeros((nPairs, 2, 1))

        for j in range(nPairs):
            dist1[j,0,0] = dist[pairs[j][0]]
            dist1[j,1,0] = dist[pairs[j][1]]
            ang1[j,0,0] = ang[pairs[j][0]]
            ang1[j,1,0] = ang[pairs[j][1]]

        return distx,disty, dist1,ang1

    def __calculateVelVer(self, phase, lagTRange, _lambda):

        Ts = lagTRange[1] - lagTRange[0]
        velW = -_lambda*phase/(4*math.pi*Ts)

        return velW

    def __calculateVelHorDir(self, dist, tau1, tau2, ang):
        nPairs = tau1.shape[0]
        vel = numpy.zeros((nPairs,3,tau1.shape[2]))

        angCos = numpy.cos(ang)
        angSin = numpy.sin(ang)

        vel0 = dist*tau1/(2*tau2**2)
        vel[:,0,:] = (vel0*angCos).sum(axis = 1)
        vel[:,1,:] = (vel0*angSin).sum(axis = 1)

        ind = numpy.where(numpy.isinf(vel))
        vel[ind] = numpy.nan

        return vel

    def __getPairsAutoCorr(self, pairsList, nChannels):

        pairsAutoCorr = numpy.zeros(nChannels, dtype = 'int')*numpy.nan

        for l in range(len(pairsList)):
            firstChannel = pairsList[l][0]
            secondChannel = pairsList[l][1]

            #Obteniendo pares de Autocorrelacion
            if firstChannel == secondChannel:
                pairsAutoCorr[firstChannel] = int(l)

        pairsAutoCorr = pairsAutoCorr.astype(int)

        pairsCrossCorr = range(len(pairsList))
        pairsCrossCorr = numpy.delete(pairsCrossCorr,pairsAutoCorr)

        return pairsAutoCorr, pairsCrossCorr

    def techniqueSA(self, pairsSelected, pairsList, nChannels, tau, azimuth, _lambda, position_x, position_y, lagTRange, correctFactor):
        """
        Function that implements Spaced Antenna (SA) technique.

        Input:    Radial velocities, Direction cosines (x and y) of the Beam, Antenna azimuth,
                    Direction correction (if necessary), Ranges and SNR

        Output:    Winds estimation (Zonal, Meridional and Vertical)

        Parameters affected:    Winds
        """
        #Cross Correlation pairs obtained
        pairsAutoCorr, pairsCrossCorr = self.__getPairsAutoCorr(pairsList, nChannels)
        pairsArray = numpy.array(pairsList)[pairsCrossCorr]
        pairsSelArray = numpy.array(pairsSelected)
        pairs = []

        #Wind estimation pairs obtained
        for i in range(pairsSelArray.shape[0]/2):
            ind1 = numpy.where(numpy.all(pairsArray == pairsSelArray[2*i], axis = 1))[0][0]
            ind2 = numpy.where(numpy.all(pairsArray == pairsSelArray[2*i + 1], axis = 1))[0][0]
            pairs.append((ind1,ind2))

        indtau = tau.shape[0]/2
        tau1 = tau[:indtau,:]
        tau2 = tau[indtau:-1,:]
        tau1 = tau1[pairs,:]
        tau2 = tau2[pairs,:]
        phase1 = tau[-1,:]

        #---------------------------------------------------------------------
        #Metodo Directo
        distx, disty, dist, ang = self.__calculateDistance(position_x, position_y, pairsCrossCorr, pairsList, pairs,azimuth)
        winds = self.__calculateVelHorDir(dist, tau1, tau2, ang)
        winds = stats.nanmean(winds, axis=0)
        #---------------------------------------------------------------------
        #Metodo General
#         distx, disty, dist = self.calculateDistance(position_x,position_y,pairsCrossCorr, pairsList, azimuth)
#         #Calculo Coeficientes de Funcion de Correlacion
#         F,G,A,B,H = self.calculateCoef(tau1,tau2,distx,disty,n)
#         #Calculo de Velocidades
#         winds = self.calculateVelUV(F,G,A,B,H)

        #---------------------------------------------------------------------
        winds[2,:] = self.__calculateVelVer(phase1, lagTRange, _lambda)
        winds = correctFactor*winds
        return winds

    def __checkTime(self, currentTime, paramInterval, outputInterval):

        dataTime = currentTime + paramInterval
        deltaTime = dataTime - self.__initime

        if deltaTime >= outputInterval or deltaTime < 0:
            self.__dataReady = True
        return

    def techniqueMeteors(self, arrayMeteor, meteorThresh, heightMin, heightMax):
        '''
        Function that implements winds estimation technique with detected meteors.

        Input:    Detected meteors, Minimum meteor quantity to wind estimation

        Output:    Winds estimation (Zonal and Meridional)

        Parameters affected:    Winds
        '''
        #Settings
        nInt = (heightMax - heightMin)/2
        winds = numpy.zeros((2,nInt))*numpy.nan

        #Filter errors
        error = numpy.where(arrayMeteor[:,-1] == 0)[0]
        finalMeteor = arrayMeteor[error,:]

        #Meteor Histogram
        finalHeights = finalMeteor[:,3]
        hist = numpy.histogram(finalHeights, bins = nInt, range = (heightMin,heightMax))
        nMeteorsPerI = hist[0]
        heightPerI = hist[1]

        #Sort of meteors
        indSort = finalHeights.argsort()
        finalMeteor2 = finalMeteor[indSort,:]

        #    Calculating winds
        ind1 = 0
        ind2 = 0

        for i in range(nInt):
            nMet = nMeteorsPerI[i]
            ind1 = ind2
            ind2 = ind1 + nMet

            meteorAux = finalMeteor2[ind1:ind2,:]

            if meteorAux.shape[0] >= meteorThresh:
                vel = meteorAux[:, 7]
                zen = meteorAux[:, 5]*numpy.pi/180
                azim = meteorAux[:, 4]*numpy.pi/180

                n = numpy.cos(zen)
        #         m = (1 - n**2)/(1 - numpy.tan(azim)**2)
        #         l = m*numpy.tan(azim)
                l = numpy.sin(zen)*numpy.sin(azim)
                m = numpy.sin(zen)*numpy.cos(azim)

                A = numpy.vstack((l, m)).transpose()
                A1 = numpy.dot(numpy.linalg.inv( numpy.dot(A.transpose(),A) ),A.transpose())
                windsAux = numpy.dot(A1, vel)

                winds[0,i] = windsAux[0]
                winds[1,i] = windsAux[1]

        return winds, heightPerI[:-1]

    def run(self, dataOut, technique, **kwargs):

        param = dataOut.data_param
        if dataOut.abscissaList != None:
            absc = dataOut.abscissaList[:-1]
        noise = dataOut.noise
        heightList = dataOut.getHeiRange()
        SNR = dataOut.data_SNR

        if technique == 'DBS':

            if kwargs.has_key('dirCosx') and kwargs.has_key('dirCosy'):
                theta_x = numpy.array(kwargs['dirCosx'])
                theta_y = numpy.array(kwargs['dirCosy'])
            else:
                elev = numpy.array(kwargs['elevation'])
                azim = numpy.array(kwargs['azimuth'])
                theta_x, theta_y = self.__calculateCosDir(elev, azim)
            azimuth = kwargs['correctAzimuth']
            if kwargs.has_key('horizontalOnly'):
                horizontalOnly = kwargs['horizontalOnly']
            else:   horizontalOnly = False
            if kwargs.has_key('correctFactor'):
                correctFactor = kwargs['correctFactor']
            else:   correctFactor = 1
            if kwargs.has_key('channelList'):
                channelList = kwargs['channelList']
                if len(channelList) == 2:
                    horizontalOnly = True
                arrayChannel = numpy.array(channelList)
                param = param[arrayChannel,:,:]
                theta_x = theta_x[arrayChannel]
                theta_y = theta_y[arrayChannel]

            velRadial0 = param[:,1,:] #Radial velocity
            dataOut.data_output, dataOut.heightList, dataOut.data_SNR = self.techniqueDBS(velRadial0, theta_x, theta_y, azimuth, correctFactor, horizontalOnly, heightList, SNR) #DBS Function
            dataOut.utctimeInit = dataOut.utctime
            dataOut.outputInterval = dataOut.timeInterval

        elif technique == 'SA':

            #Parameters
            position_x = kwargs['positionX']
            position_y = kwargs['positionY']
            azimuth = kwargs['azimuth']

            if kwargs.has_key('crosspairsList'):
                pairs = kwargs['crosspairsList']
            else:
                pairs = None

            if kwargs.has_key('correctFactor'):
                correctFactor = kwargs['correctFactor']
            else:
                correctFactor = 1

            tau = dataOut.data_param
            _lambda = dataOut.C/dataOut.frequency
            pairsList = dataOut.groupList
            nChannels = dataOut.nChannels

            dataOut.data_output = self.techniqueSA(pairs, pairsList, nChannels, tau, azimuth, _lambda, position_x, position_y, absc, correctFactor)
            dataOut.utctimeInit = dataOut.utctime
            dataOut.outputInterval = dataOut.timeInterval

        elif technique == 'Meteors':
            dataOut.flagNoData = True
            self.__dataReady = False

            if kwargs.has_key('nHours'):
                nHours = kwargs['nHours']
            else:
                nHours = 1

            if kwargs.has_key('meteorsPerBin'):
                meteorThresh = kwargs['meteorsPerBin']
            else:
                meteorThresh = 6

            if kwargs.has_key('hmin'):
                hmin = kwargs['hmin']
            else:   hmin = 70
            if kwargs.has_key('hmax'):
                hmax = kwargs['hmax']
            else:   hmax = 110

            dataOut.outputInterval = nHours*3600

            if self.__isConfig == False:
#                 self.__initime = dataOut.datatime.replace(minute = 0, second = 0, microsecond = 03)
                #Get Initial LTC time
                self.__initime = datetime.datetime.utcfromtimestamp(self.dataOut.utctime)
                self.__initime = (self.__initime.replace(minute = 0, second = 0, microsecond = 0) - datetime.datetime(1970, 1, 1)).total_seconds()

                self.__isConfig = True

            if self.__buffer == None:
                self.__buffer = dataOut.data_param
                self.__firstdata = copy.copy(dataOut)

            else:
                self.__buffer = numpy.vstack((self.__buffer, dataOut.data_param))

            self.__checkTime(dataOut.utctime, dataOut.paramInterval, dataOut.outputInterval) #Check if the buffer is ready

            if self.__dataReady:
                dataOut.utctimeInit = self.__initime

                self.__initime += dataOut.outputInterval #to erase time offset

                dataOut.data_output, dataOut.heightList = self.techniqueMeteors(self.__buffer, meteorThresh, hmin, hmax)
                dataOut.flagNoData = False
                self.__buffer = None

        return

class EWDriftsEstimation(Operation):


    def __init__(self):
        Operation.__init__(self)

    def __correctValues(self, heiRang, phi, velRadial, SNR):
        listPhi = phi.tolist()
        maxid = listPhi.index(max(listPhi))
        minid = listPhi.index(min(listPhi))

        rango = range(len(phi))
   #     rango = numpy.delete(rango,maxid)

        heiRang1 = heiRang*math.cos(phi[maxid])
        heiRangAux = heiRang*math.cos(phi[minid])
        indOut = (heiRang1 < heiRangAux[0]).nonzero()
        heiRang1 = numpy.delete(heiRang1,indOut)

        velRadial1 = numpy.zeros([len(phi),len(heiRang1)])
        SNR1 = numpy.zeros([len(phi),len(heiRang1)])

        for i in rango:
            x = heiRang*math.cos(phi[i])
            y1 = velRadial[i,:]
            f1 = interpolate.interp1d(x,y1,kind = 'cubic')

            x1 = heiRang1
            y11 = f1(x1)

            y2 = SNR[i,:]
            f2 = interpolate.interp1d(x,y2,kind = 'cubic')
            y21 = f2(x1)

            velRadial1[i,:] = y11
            SNR1[i,:] = y21

        return heiRang1, velRadial1, SNR1

    def run(self, dataOut, zenith, zenithCorrection):
        heiRang = dataOut.heightList
        velRadial = dataOut.data_param[:,3,:]
        SNR = dataOut.data_SNR

        zenith = numpy.array(zenith)
        zenith -= zenithCorrection
        zenith *= numpy.pi/180

        heiRang1, velRadial1, SNR1 = self.__correctValues(heiRang, numpy.abs(zenith), velRadial, SNR)

        alp = zenith[0]
        bet = zenith[1]

        w_w = velRadial1[0,:]
        w_e = velRadial1[1,:]

        w = (w_w*numpy.sin(bet) - w_e*numpy.sin(alp))/(numpy.cos(alp)*numpy.sin(bet) - numpy.cos(bet)*numpy.sin(alp))
        u = (w_w*numpy.cos(bet) - w_e*numpy.cos(alp))/(numpy.sin(alp)*numpy.cos(bet) - numpy.sin(bet)*numpy.cos(alp))

        winds = numpy.vstack((u,w))

        dataOut.heightList = heiRang1
        dataOut.data_output = winds
        dataOut.data_SNR = SNR1

        dataOut.utctimeInit = dataOut.utctime
        dataOut.outputInterval = dataOut.timeInterval
        return
