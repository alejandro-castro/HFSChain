#----------------------------------------------NEW----------------------------------------------------#
#example:
#python GenerateMomentsHDF5.py  -path '/media/igp-114/PROCDATA' -f 2.72 -C 0 -ii 6 -online 0 -code 0 -date "2018/01/25" -startTime "00:00:00" -endTime "23:59:59" -lo 31

import os, sys
import time
import datetime
import argparse

path = os.path.split(os.getcwd())[0]
sys.path.append(path)
from controller import *

print "REVISAR LA LINEA DE EJEMPLO COMENTADA DENTRO DE ESTE SCRIPT EN CASO TENGA PROBLEMAS DE EJECUCION"


yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
daybefore= yesterday.strftime("%Y/%m/%d")
today = datetime.datetime.now().strftime("%Y/%m/%d")


parser = argparse.ArgumentParser()
########################## PATH- DATA  ###################################################################################################
parser.add_argument('-path',action='store',dest='path_lectura',help='Directorio de Datos \
					.Por defecto, se esta ingresando entre comillas /media/igp-114/PROCDATA/',default='/media/igp-114/PROCDATA/')
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
parser.add_argument('-startTime',action='store',dest='time_start',help='Ingresar tiempo de inicio, formato 00:00:00 entre comillas',default="00:00:00")
parser.add_argument('-endTime',action='store',dest='time_end',help='Ingresar tiempo de fin, formato 23:59:59 entre comillas',default="23:59:59")
########################## LOCATION AND ORIENTATION ####################################################################################################
parser.add_argument('-lo',action='store',dest='lo_seleccionado',type=int,help='Parametro para establecer la ubicacion de la estacion de Rx y su orientacion.\
										Example: XA   ----- X: Es el primer valor determina la ubicacion de la estacion. A: Es \
										  el segundo valor determina la orientacion N45O o N45E.  \
										11: JRO-N450, 12: JRO-N45E \
												21: HYO-N45O, 22: HYO-N45E', default=11)
########################## GRAPHICS - RESULTS  ###################################################################################################
parser.add_argument('-graphics_folder',action='store',dest='graphics_folder',help='Directorio de Resultados \
					.Por defecto, se esta ingresando entre comillas /home/igp-114/Pictures/', default='/home/ci-81/Pictures/')


#Parsing the options of the script
results	   = parser.parse_args()
path	   = str(results.path_lectura)
freq	   = results.f_freq
campaign   = results.c_campaign
inc_int	   = results.i_integration
online	   = (results.online)
code	   = int(results.code_seleccionado)
date	   = results.date_seleccionado
time_start = results.time_start
time_end   = results.time_end
lo		   = results.lo_seleccionado
graphics_folder = results.graphics_folder

# Setting the number of profiles, FFTs and incoherent integrations
if campaign == 1:
	nProfiles=600
	nFFT	 =600
	inc_int= 0
else:
	nProfiles = 100
	nFFT	  = 100
	#if code == 1:
	#	time_start = "00:01:50" # This is done to synchronize the pulsed Sicaya Transmitter with its processing

# Setting the online time
if online == 1:
	date	  = today
	time_start= "00:00:00"
	time_end  = "23:59:59"

#Setting flag for frequency used to store the results of experiment in the respective folder
if freq <3:
	ngraph = 0
else:
	ngraph =1

#Setting the frequency radar for both voltage proc and HF reader
setupF   = freq
setradarF= freq*10**6


print "Path",path
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

time.sleep(0.1)

location_dict = {11:"JRO_A", 12: "JRO_B", 21:"HYO_A", 22:"HYO_B", 31:"MALA_A", 32:"MALA_B",
				41:"MERCED_A", 42:"MERCED_B", 51:"BARRANCA_A", 52:"BARRANCA_B"}
#-----------------------------PATH-graficos-----------------------------------#
#Typical folder /home/hfuser/Pictures/
identifier = 'sp%s1_f%s'%(code, ngraph)
figpath = graphics_folder+'/GRAPHICS_SCHAIN_%s/'%(location_dict[lo]) + identifier +'/'


print "Directorio de graficos y resultados", figpath
#---------------------------------------------------------------------------#

controllerObj = Project()
controllerObj.setup(id = '191', name='test01', description="Generate HDF5s with Moments Data")

readUnitConfObj = controllerObj.addReadUnit(datatype = 'HFReader',
											path	 = path,
											startDate= date,   #Format 'YEAR/MONTH/DAY'
											endDate  = date,   #Format 'YEAR/MONTH/DAY'
											code	 = code,
											frequency= setupF,
											campaign = campaign,
											inc_int  = inc_int,
											startTime= time_start,
											endTime  = time_end,
											online   = online,
											set	  = 0,
											delay	= 0,
											walk	 = 1,
											timezone = -5*3600
											)

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj12 = procUnitConfObj0.addOperation(name='setRadarFrequency')
opObj12.addParameter(name='frequency', value=setradarF, format='float')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value=nFFT, format='int')
procUnitConfObj1.addParameter(name='nProfiles', value=nProfiles, format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1)', format='pairsList')
procUnitConfObj1.addParameter(name='noiseMode', value=2, format='int')

opObj12 = procUnitConfObj1.addOperation(name='removeInterference') #It should be analyzed its use because it can remove part of the signal
#opObj12 = procUnitConfObj1.addOperation(name='removeDC')


procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj1.getId())
opObj20 = procUnitConfObj2.addOperation(name='GetMoments')
opObj20 = procUnitConfObj2.addOperation(name='GetCrossData')
#opObj20 = procUnitConfObj2.addOperation(name='GetRGBData') # Not used because the RGB data is obtained directly from the HF Reader.

opObj25 = procUnitConfObj2.addOperation(name='HDF5Writer', optype='other')
opObj25.addParameter(name='path', value=figpath+'/MomentData')
opObj25.addParameter(name='location',value=lo,format='int')
opObj25.addParameter(name='identifier',value=identifier,format='str')
opObj25.addParameter(name='blocksPerFile', value='10', format='int')
opObj25.addParameter(name='metadataList',value='type,inputUnit,heightList,frequency',format='list')#,RxInfo,TxInfo /*RxInfo = lat,long,alt,type double or simple, etc...
opObj25.addParameter(name='dataList',value='data_param,data_SNR,data_RGB,CrossData,utctime,location,identifier',format='list')#AvgCohModuledata_DC,data_Coherence
#The identifier of data is in the form sp01_f0 and it is save so the user can know where does each HDF5 file came from

controllerObj.createObjects()
controllerObj.connectObjects()

controllerObj.run()
