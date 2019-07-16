'''
example:
python PlotSpectrograms.py  -path '/media/igp-114/PROCDATA' -f 2.72 -C 0 -ii 6 -online 0 -code 0 -date "2018/01/25" -startTime "00:00:00" -endTime "23:59:59" -lo 31
'''

import os, sys
import time
import datetime
import argparse

path = os.path.split(os.getcwd())[0]
sys.path.append(path)
from controller import *



print "REVISAR LA LINEA DE EJEMPLO EN EL ARCHIVO EN CASO PROBLEMAS DE EJECUCION"

yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
daybefore= yesterday.strftime("%Y/%m/%d")
today = datetime.datetime.now().strftime("%Y/%m/%d")

parser = argparse.ArgumentParser()
########################## PATH- DATA  ###################################################################################################
parser.add_argument('-path',action='store',dest='path_lectura',help='Directorio de Datos \
					.Por defecto, se esta ingresando entre comillas /media/igp-114/PROCDATA/',default='/home/igp-114/PROCDATA/')
########################## FRECUENCIA ####################################################################################################
parser.add_argument('-f',action='store',dest='f_freq',type=float,help='Frecuencia en Mhz 2.72 y 3.64. Por defecto, se esta ingresando 2.72 ',default=2.72)
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
												21: HYO-N45O, 22: HYO-N45E',default=11)
########################## GRAPHICS - RESULTS  ###################################################################################################
parser.add_argument('-graphics_folder',action='store',dest='graphics_folder',help='Directorio de Resultados \
					.Por defecto, se esta ingresando entre comillas /home/igp-114/Pictures/', default='/home/igp-114/Pictures/')
###########################################################################################################################################
results	= parser.parse_args()
path	   = str(results.path_lectura)
freq	   = results.f_freq
campaign   = results.c_campaign
inc_int	= results.i_integration
online	   = (results.online)
code	   = int(results.code_seleccionado)
date	   = results.date_seleccionado
time_start = results.time_start
time_end   = results.time_end
lo		 = results.lo_seleccionado
graphics_folder = results.graphics_folder

if campaign == 1:
	path += "/CAMPAIGN/"
	nProfiles=600
	nFFT	 =600
	inc_int= 0
else:
	nProfiles = 100
	nFFT	  = 100


if online == 1:
	date	  = today
	time_start= "00:00:00"
	time_end  = "23:59:59"

if freq <3:
	ngraph= 0
else:
	ngraph= 1


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


#-----------------------------------------------------------------------------------------------------#
#It's not considered the B station in the single stations, because it uses a single PC.
location_dict = {11:"JRO_A", 12: "JRO_B", 21:"HYO_A", 22:"HYO_B", 31:"MALA",
	41:"MERCED", 51:"BARRANCA", 61:"OROYA"}
#-----------------------------PATH-graficos-----------------------------------#
identifier = 'sp%s1_f%s'%(code, ngraph)
figpath = graphics_folder+'/GRAPHICS_SCHAIN_%s/'%(location_dict[lo]) + identifier +'/'


print "figpath",figpath
#---------------------------------------------------------------------------#

controllerObj = Project()
controllerObj.setup(id = '400', name='momentsplot', description="Ploteo de los distintos espectrogramas\
 con la ubicacion de la frecuencia Doppler promedio y su ancho espectral")

readUnitConfObj = controllerObj.addReadUnit(datatype = 'HFReader',
											path	 = path,
											startDate= date,
											endDate  = date,
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

opObj01 = procUnitConfObj0.addOperation(name='setRadarFrequency')
opObj01.addParameter(name='frequency', value=setradarF, format='float')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value=nFFT, format='int')
procUnitConfObj1.addParameter(name='nProfiles', value=nProfiles, format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1)', format='pairsList')
procUnitConfObj1.addParameter(name='noiseMode', value=2, format='int')

#procUnitConfObj1.addOperation(name='removeInterference')
#procUnitConfObj1.addOperation(name='removeDC')


procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj1.getId())
procUnitConfObj2.addOperation(name='GetMoments')


opObj21 = procUnitConfObj2.addOperation(name='MomentsPlot', optype='other')
opObj21.addParameter(name='id', value='3', format='int')
opObj21.addParameter(name='showprofile', value='1', format='int')
opObj21.addParameter(name='wintitle', value='Moments Plot', format='str')
opObj21.addParameter(name='save', value='1', format='bool')
opObj21.addParameter(name='figpath', value=figpath, format='str')
opObj21.addParameter(name='zmin', value='-140', format='float')
opObj21.addParameter(name='zmax', value='-100', format='float')
opObj21.addParameter(name='xmin', value='-280', format='float')
opObj21.addParameter(name='xmax', value='280', format='float')
opObj21.addParameter(name='ymin', value='0', format='float')
opObj21.addParameter(name='ymax', value='1500', format='float')
opObj21.addParameter(name='showMeanDoppler', value='1', format='bool')
opObj21.addParameter(name='showSpectralWidth', value='0', format='bool')
opObj21.addParameter(name='show', value='0', format='bool')

controllerObj.createObjects()
controllerObj.connectObjects()

controllerObj.run()
