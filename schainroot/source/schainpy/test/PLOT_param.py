import os, sys
import time
import datetime
import argparse

path = os.path.split(os.getcwd())[0]
sys.path.append(path)
from controller import *

#----------------------------------------------NEW----------------------------------------------------#
#example:
#
print "REVISAR LA LINEA DE EJEMPLO COMENTADA DENTRO DE ESTE SCRIPT EN CASO TENGA PROBLEMAS DE EJECUCION"


yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
daybefore= yesterday.strftime("%Y/%m/%d")
today = datetime.datetime.now().strftime("%Y/%m/%d")


parser = argparse.ArgumentParser()
########################## PATH - MOMENTS DATA  ###################################################################################################
parser.add_argument('-path',action='store',dest='path_lectura',help='Directorio de Datos de Momentos \
	.Por defecto, se esta ingresando entre comillas /home/igp-114/Pictures/',default='/home/igp-114/Pictures/')
########################## FRECUENCIA ####################################################################################################
parser.add_argument('-f',action='store',dest='f_freq',type=float,help='Frecuencia en Mhz 2.72 y 3.64. Por defecto, se esta ingresando 2.72 ',default=2.72216796875)
########################## CAMPAIGN ### 600 o 100 perfiles ###############################################################################
parser.add_argument('-C',action='store',dest='c_campaign',type=int,help='Campaign 1 (600 perfiles) y 0(100 perfiles). Por defecto, se esta ingresando 1',default=1)
########################## INCOHERENT INTEGRATION ### Entre 0 y 6  #######################################################################
parser.add_argument('-ii',action='store',dest='i_integration',type=int,help='Data spectra tiene integraciones incoherentes entre \
	0 y 6. Por defecto, se esta ingresando 0',default=0)
########################## ONLINE OR OFFLINE   ###########################################################################################
parser.add_argument('-online',action='store',dest='online',type=int,help='Operacion 0 Off-line 1 On-Line\
		.Por defecto, se esta ingresando 0(off Line) ',default=0)
########################## CODIGO - INPUT ################################################################################################
parser.add_argument('-code',action='store',dest='code_seleccionado',type=int,help='Code de Tx para generar en estacion \
	de Rx Spectro 0,1,2. Por defecto, se esta ingresando 0(Ancon)',default=0)
########################## DAY- SELECCION ################################################################################################
parser.add_argument('-date',action='store',dest='date_seleccionado',help='Seleccionar fecha si es OFFLINE se ingresa \
	la fecha con el dia deseado. Por defecto, considera el dia anterior',default=daybefore)
######################### TIME- SELECCION ################################################################################################
parser.add_argument('-startTime',action='store',dest='time_start',help='Ingresar tiempo de inicio, formato 15:00:00 entre comillas',default="00:00:00")
parser.add_argument('-endTime',action='store',dest='time_end',help='Ingresar tiempo de fin, formato 23:59:59 entre comillas',default="23:59:59")
########################## LOCATION AND ORIENTATION ####################################################################################################
parser.add_argument('-lo',action='store',dest='lo_seleccionado',type=int,help='Parametro para establecer la ubicacion de la estacion de Rx y su orientacion.\
	Example: XA   ----- X: Es el primer valor determina la ubicacion de la estacion. A: Es \
	el segundo valor determina la orientacion N45O o N45E.  \
	11: JRO-N450, 12: JRO-N45E \
	21: HYO-N45O, 22: HYO-N45E',default=11)
###########################################################################################################################################


#Parsing the options of the script
results    = parser.parse_args()
path       = str(results.path_lectura)
freq       = results.f_freq
campaign   = results.c_campaign
inc_int    = results.i_integration
online       = (results.online)
code       = int(results.code_seleccionado)
date       = results.date_seleccionado
time_start = results.time_start
time_end   = results.time_end
lo         = results.lo_seleccionado


# Setting the number of profiles, FFTs and incoherent integrations
if campaign == 1:
	nProfiles=600
	nFFT     =600
	inc_int= 0
else:
	nProfiles = 100
	nFFT      = 100
	if code == 1:
		time_start = "00:01:50" # This is done to synchronize the pulsed Sicaya Transmitter with its processing

# Setting the online time
if online == 1:
	date      = today
	time_start= "00:00:00"
	time_end  = "23:59:59"


#Setting flag for frequency used to store the results of experiment in the respective folder
if freq <3:
	ngraph= 0
else:
	ngraph= 1


#Setting the frequency radar for both voltage proc and HF reader
setupF   = freq
setradarF= freq*10**6

#Setting the exact folder from where the moment data will be read
location_dict = {11:"JRO_A", 12: "JRO_B", 21:"HYO_A", 22:"HYO_B", 31:"MALA_A", 32:"MALA_B",
				41:"MERCED_A", 42:"MERCED_B", 51:"BARRANCA_A", 52:"BARRANCA_B"}
identifier = 'sp%s1_f%s'%(code, ngraph)
parampath  = path + '/GRAPHICS_SCHAIN_%s/'%(location_dict[lo]) + identifier +'/MomentData/' #MomentData should be the subfolder that was set in GenerateMomentsHDF5.py

#Setting the exact folder where the graphics will be located
figpath	   = path + '/GRAPHICS_SCHAIN_%s/'%(location_dict[lo]) + identifier+'/'


print "Param path",parampath
print "Fig path", figpath
print "Frecuencia en Mhz",freq
print "Freq_setup",freq
print "Freq_setradar",setradarF
print "Mode Campaign" ,campaign
print "nProfiles",nProfiles
print "nFFT",nFFT
print "Incoherent integration",inc_int
print "Online",online
print "Code",code
print "Date",date
print "Time_start", time_start
print "Time_end"  , time_end
print "ngraph",ngraph
print "Location&orientation",lo

time.sleep(1)

#---------------------------------------------------------------------------#

controllerObj = Project()
controllerObj.setup(id = '191', name='paramplot', description="Este programa graficara los parametros adquiridos a traves de los momentos espectrales.")

readUnitConfObj = controllerObj.addReadUnit(datatype='HFParamReader',
                                            path     = parampath,
                                            startDate= date,   #'2017/12/31',# 2017/11/14 date
                                            endDate  = date,   #'2017/12/31',#date 2017/11/14
                                            code     = code,
                                            frequency= setupF,
                                            campaign = campaign,
                                            inc_int  = inc_int,
                                            startTime= time_start,
                                            endTime  = time_end,
                                            online   = online,
                                            set      = 0,
                                            delay    = 0,
                                            walk     = 1,
                                            timezone = -5*3600
                                            )

readUnitConfObj.addParameter(name='blocksPerFile', value='10', format='int')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=readUnitConfObj.getId())
procUnitConfObj1.addParameter(name='nProfiles', value=nFFT, format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1)', format='pairsList')


opObj21 = procUnitConfObj1.addOperation(name='ParametersPlot', optype='other')
opObj21.addParameter(name='id', value='4000', format='int')
opObj21.addParameter(name='wintitle', value='Doppler-Radial Velocity Plot0', format='str')
opObj21.addParameter(name='show', value='0', format='bool')
opObj21.addParameter(name='channelList', value='0', format='intlist')
opObj21.addParameter(name='SNR', value='0', format='bool')
#opObj21.addParameter(name='SNRmin', value='-50', format='int')
#opObj21.addParameter(name='SNRmax', value='50', format='int')
#opObj21.addParameter(name='SNRthresh', value='1', format='float')
opObj21.addParameter(name='xmin', value=0, format='float')
opObj21.addParameter(name='xmax', value=24, format='float')
opObj21.addParameter(name='zmin', value=-50, format='float')
opObj21.addParameter(name='zmax', value=50, format='float')
#opObj21.addParameter(name='parameterIndex', value=, format='int')
opObj21.addParameter(name='save', value='1', format='bool')
opObj21.addParameter(name='figpath', value=figpath, format='str')
opObj21.addParameter(name='data_time_save',value='1',format='bool')
opObj21.addParameter(name='ext', value='.jpeg', format='str')


############
opObj21 = procUnitConfObj1.addOperation(name='ParametersPlot', optype='other')
opObj21.addParameter(name='id', value='7000', format='int')
opObj21.addParameter(name='wintitle', value='SNR_0', format='str')
opObj21.addParameter(name='channelList', value='0', format='intlist')
opObj21.addParameter(name='show', value='0', format='bool')
opObj21.addParameter(name='SNR', value='1', format='bool')
opObj21.addParameter(name='DOP', value='0', format='bool')
opObj21.addParameter(name='SNRdBmin', value='-9', format='int')
opObj21.addParameter(name='SNRdBmax', value='9', format='int')
#opObj21.addParameter(name='SNRthresh', value='1', format='float')
opObj21.addParameter(name='xmin', value=0, format='float')
opObj21.addParameter(name='xmax', value=24, format='float')
#opObj21.addParameter(name='zmin', value=-6, format='float')
#opObj21.addParameter(name='zmax', value=6, format='float')
#opObj21.addParameter(name='parameterIndex', value=, format='int')
opObj21.addParameter(name='save', value='1', format='bool')
opObj21.addParameter(name='figpath', value=figpath, format='str')
opObj21.addParameter(name='data_time_save',value='1',format='bool')
opObj21.addParameter(name='ext', value='.jpeg', format='str')


############
opObj21 = procUnitConfObj1.addOperation(name='ParametersPlot', optype='other')
opObj21.addParameter(name='id', value='4005', format='int')
opObj21.addParameter(name='wintitle', value='Doppler-Radial Velocity Plot1', format='str')
opObj21.addParameter(name='show', value='0', format='bool')
opObj21.addParameter(name='channelList', value='1', format='intlist')
opObj21.addParameter(name='SNR', value='0', format='bool')
#opObj21.addParameter(name='SNRmin', value='-50', format='int')
#opObj21.addParameter(name='SNRmax', value='50', format='int')
#opObj21.addParameter(name='SNRthresh', value='1', format='float')
opObj21.addParameter(name='xmin', value=0, format='float')
opObj21.addParameter(name='xmax', value=24, format='float')
opObj21.addParameter(name='zmin', value=-50, format='float')
opObj21.addParameter(name='zmax', value=50, format='float')
#opObj21.addParameter(name='parameterIndex', value=, format='int')
opObj21.addParameter(name='save', value='1', format='bool')
opObj21.addParameter(name='figpath', value=figpath, format='str')
opObj21.addParameter(name='data_time_save',value='1',format='bool')
opObj21.addParameter(name='ext', value='.jpeg', format='str')

############
opObj21 = procUnitConfObj1.addOperation(name='ParametersPlot', optype='other')
opObj21.addParameter(name='id', value='8000', format='int')
opObj21.addParameter(name='wintitle', value='SNR_1', format='str')
opObj21.addParameter(name='channelList', value='1', format='intlist')
opObj21.addParameter(name='show', value='0', format='bool')
opObj21.addParameter(name='SNR', value='1', format='bool')
opObj21.addParameter(name='DOP', value='0', format='bool')
opObj21.addParameter(name='SNRdBmin', value='-9', format='int')
opObj21.addParameter(name='SNRdBmax', value='9', format='int')
#opObj21.addParameter(name='SNRthresh', value='0', format='float')
opObj21.addParameter(name='xmin', value=0, format='float')
opObj21.addParameter(name='xmax', value=24, format='float')
#opObj21.addParameter(name='parameterIndex', value=, format='int')
opObj21.addParameter(name='save', value='1', format='bool')
opObj21.addParameter(name='figpath', value=figpath, format='str')
opObj21.addParameter(name='data_time_save',value='1',format='bool')
opObj21.addParameter(name='ext', value='.jpeg', format='str')
#
############
opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
opObj11.addParameter(name='id', value='3002', format='int')
opObj11.addParameter(name='wintitle', value='AmpMapCoherence', format='str')
opObj11.addParameter(name='show', value='0', format='bool')
opObj11.addParameter(name='COH', value='1', format='bool')
opObj11.addParameter(name='PHASE', value='0', format='bool')
opObj11.addParameter(name='xmin', value='0', format='float')
opObj11.addParameter(name='xmax', value='24', format='float')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='pairsList', value='(0,1)', format='pairsList')
####opObj11.addParameter(name='figfile', value="Coherencia_2.72Mhz.jpg", format='str')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='data_time_save',value='1',format='bool')
opObj11.addParameter(name='ext', value='.jpeg', format='str')
#
opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
opObj11.addParameter(name='id', value='3000', format='int')
opObj11.addParameter(name='wintitle', value='PhaseMapCoherence', format='str')
opObj11.addParameter(name='COH', value='1', format='bool')
opObj11.addParameter(name='PHASE', value='1', format='bool')
opObj11.addParameter(name='show', value='1', format='bool')
opObj11.addParameter(name='xmin', value='0', format='float')
opObj11.addParameter(name='xmax', value='24', format='float')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='pairsList', value='(0,1)', format='pairsList')
# # opObj11.addParameter(name='figfile', value="Phase_2.72Mhz.jpg", format='str')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='data_time_save',value='1',format='bool')
opObj11.addParameter(name='ext', value='.jpeg', format='str')


controllerObj.createObjects()
controllerObj.connectObjects()


controllerObj.run()
