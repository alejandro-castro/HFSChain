import os, sys
import time
import datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)
from controller import *
desc = "HF_EXAMPLE"
filename = "hf_test.xml"
controllerObj = Project()
controllerObj.setup(id = '191', name='test01', description=desc)
######################CONFIGURACION DE OUT##########################333
####default 1424 y por test de operacion continua 10 segundos 1440*6 =8640
blocksPerFile='1440'
#----------------------------------------------NEW----------------------------------------------------#
'''
example:
python RTDI_OUT_HF.py  -path '/home/hfuser1204/HFA' -f 2.72 -C 0 -ii 6 -ch 0 -online 0 -code 0 -lo 11 -date "2018/01/25" -startTime "00:00:00" -endTime "23:59:59"

python RTDI_OUT_HF.py -path '/home/hfuser1204/HFA' -f 2.72 -code 0 -lo 11 -ch 0


python RTDI_OUT_HF.py -path '/home/hfuser1204/HFA' -f 2.72 -code 0 -lo 11 -ch 0 -date "2018/02/15"
'''
print "REVISAR LA LINEA DE EJEMPLO EN EL ARCHIVO EN CASO PROBLEMAS DE EJECUCION"
import argparse
parser = argparse.ArgumentParser()
########################## PATH- DATA  ###################################################################################################
parser.add_argument('-path',action='store',dest='path_lectura',help='Directorio de Datos \
					.Por defecto, se esta ingresando entre comillas /home/hfuser1204/HFA/',default='/home/hfuser/HFA/')
########################## FRECUENCIA ####################################################################################################
parser.add_argument('-f',action='store',dest='f_freq',type=float,help='Frecuencia en Mhz 2.72 y 3.64. Por defecto, se esta ingresando 2.72 ',default=2.72)
########################## CAMPAIGN ### 600 o 100 perfiles ###############################################################################
parser.add_argument('-C',action='store',dest='c_campaign',type=int,help='Campaign 1 (600 perfiles) y 0(100 perfiles). Por defecto, se esta ingresando 1',default=1)
########################## INCOHERENT INTEGRATION ### Entre 0 y 6  #######################################################################
parser.add_argument('-ii',action='store',dest='i_integration',type=int,help='Data spectra tiene integraciones incoherentes entre \
									0 y 6. Por defecto, se esta ingresando 0',default=0)
########################## ONLINE OR OFFLINE	###########################################################################################
parser.add_argument('-online',action='store',dest='online',type=int,help='Operacion 0 Off-line 1 On-Line\
										.Por defecto, se esta ingresando 0(off Line) ',default=0)
########################## CODIGO - INPUT ################################################################################################
parser.add_argument('-code',action='store',dest='code_seleccionado',type=int,help='Code de Tx para generar en estacion \
											de Rx Spectro 0,1,2. Por defecto, se esta ingresando 0(Ancon)',default=0)
########################## DAY- SELECCION ################################################################################################
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
daybefore= yesterday.strftime("%Y/%m/%d")
today = datetime.datetime.now().strftime("%Y/%m/%d")
parser.add_argument('-date',action='store',dest='date_seleccionado',help='Seleccionar fecha si es OFFLINE se ingresa \
							la fecha con el dia deseado. Por defecto, considera el dia anterior',default=daybefore)
######################### TIME- SELECCION ################################################################################################
parser.add_argument('-startTime',action='store',dest='time_start',help='Ingresar tiempo de inicio, formato 00:00:00 entre comillas',default="00:00:00")
parser.add_argument('-endTime',action='store',dest='time_end',help='Ingresar tiempo de fin, formato 23:59:59 entre comillas',default="23:59:59")

########################## LOCATION AND ORIENTATION ####################################################################################################
parser.add_argument('-lo',action='store',dest='lo_seleccionado',type=int,help='Parametro para establecer la ubicacion de la estacion de Rx y su orientacion.\
										Example: XA	----- X: Es el primer valor determina la ubicacion de la estacion. A: Es \
												  el segundo valor determina la orientacion N45O o N45E.  \
													11: JRO-N450, 12: JRO-N45E \
														  21: HYO-N45O, 22: HYO-N45E',default=11)

########################## CHANNEL ########################################################################################################
parser.add_argument('-ch',action='store',dest='ch_seleccionado',type=int,help=' Seleccion de Canal entre 0 y 1',default=0)
###########################################################################################################################################

results	 = parser.parse_args()
path		 = str(results.path_lectura)
freq		 = results.f_freq
campaign	= results.c_campaign
inc_int	 = results.i_integration
online		 = (results.online)
code		 = int(results.code_seleccionado)
date		 = results.date_seleccionado
time_start = results.time_start
time_end	= results.time_end
lo			= results.lo_seleccionado
channel	 = results.ch_seleccionado


nProfiles = 100
nFFT		= 100
set		 = 0

if campaign == 1:
	nProfiles = 600
	nFFT = 600
	inc_int = 0
if online == 1:
	date = today
	time_start= "00:00:00"
	time_end  = "23:59:59"
	set = None

ngraph= 1
if channel==0:
	c_web = 6
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

setupF	= freq
setradarF= freq*10**6
numberF  = int(freq*10**3)
c_freq	= int(freq*10**2)
number	= str(numberF)
lo_n=lo/10
lo_0=lo_n*10+1
lo_1=lo_0+1

print "Path",path
print "Frecuencia en Mhz",freq
print "Freq_setup",freq
print "Freq_setradar",setradarF
print "Freq_number", numberF
print "c_freq", c_freq
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
print "set",set
print "Location&orientation",lo
print "Channel",channel
print "REVISAR LA LINEA DE EJEMPLO EN EL ARCHIVO EN CASO PROBLEMAS DE EJECUCION"

time.sleep(1)

#-----------------------------------------------------------------------------------------------------#
#-------------------------PATH-PDATA-------------------------------------
#path='/media/igp-114/PROCDATA/'
#-----------------------------PATH-graficos-----------------------------------#
if status_figpath== True:
	figpath='/home/hfuser/RTDI/graphics_schain/sp'+str(code)+'1_f'+str(ngraph)+'/'
else:
	figpath='/home/hfuser/RTDI_B/graphics_schain/sp'+str(code)+'1_f'+str(ngraph)+'/'

figpath = path + "/Figures/graphics_schain/sp"+str(code)+'1_f'+str(ngraph)+'/'
print "figpath******************",figpath

parampath = '/home/ci-81/Documents/JRO_CAMPAIGN_ALEJANDRO/Refactor/sp'+str(code)+'1_f'+str(ngraph)+'/param/'

#---------------------------------------------------------------------------#
readUnitConfObj = controllerObj.addReadUnit(datatype = 'HFParamReader',
														path	  = parampath,
														startDate= date,	#'2017/12/31',# 2017/11/14 date
														endDate  = date,	#'2017/12/31',#date 2017/11/14
														code	  = code,
	  													frequency= setupF,
														campaign = campaign,
														inc_int  = inc_int,
														startTime= time_start,
														endTime  = time_end,
														online	= online,
														set		= 0,
														delay	 = 0,
														walk	  = 1,
														timezone = -5*3600
														)
readUnitConfObj.addParameter(name='blocksPerFile', value='10', format='int')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='ParametersProc',inputId=readUnitConfObj.getId())
procUnitConfObj1.addParameter(name='nProfiles', value=nFFT, format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1)', format='pairsList')

procUnitConfObj2= controllerObj.addProcUnit(datatype='ImageProc',inputId=procUnitConfObj1.getId())
procUnitConfObj2.addParameter(name='channel', value=str(channel), format='int')
procUnitConfObj2.addParameter(name='threshv', value='0.1', format='float')
#procUnitConfObj2.addParameter(name='E_Region', value='1', format='bool')

opObj11= procUnitConfObj2.addOperation(name='ImageWriter',optype='other')
opObj11.addParameter(name='blocksPerFile', value=blocksPerFile, format='int') ####default 1424 y por test de operacion continua 10 segundos 1440*6 =8640
opObj11.addParameter(name='standard', value='1', format='bool')
opObj11.addParameter(name='c_station_o', value=str(lo), format='str')
opObj11.addParameter(name='c_freq', value=str(c_freq), format='str')
opObj11.addParameter(name='c_cod_Tx', value=str(code), format='str')
opObj11.addParameter(name='c_ch', value=str(channel), format='str')
opObj11.addParameter(name='path',value=figpath,format='str')

opObj11 = procUnitConfObj2.addOperation(name='RTDIPlot', optype='other')
opObj11.addParameter(name='id', value='402', format='int')
# opObj11.addParameter(name='xmin', value='0', format='int')
# opObj11.addParameter(name='xmax', value='24', format='int')
# opObj11.addParameter(name='ymin', value='500', format='int')
# opObj11.addParameter(name='ymax', value='1000', format='int')
#opObj11.addParameter(name='figfile', value="Test", format='str') # Tiene menos importancia que standard, si standard es True, este argumento se ignora
#opObj11.addParameter(name='show', value='1', format='bool')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='ext', value='.png', format='str')
opObj11.addParameter(name='standard', value='1', format='bool')
opObj11.addParameter(name='c_station_o', value=str(lo), format='str')
opObj11.addParameter(name='c_web', value=str(c_web), format='str')
opObj11.addParameter(name='c_freq', value=str(c_freq), format='str')
opObj11.addParameter(name='c_cod_Tx', value=str(code), format='str')
opObj11.addParameter(name='c_ch', value=str(channel), format='str')

# print "Escribiendo el archivo XML"
# controllerObj.writeXml(filename)
# print "Leyendo el archivo XML"
# controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()

#timeit.timeit('controllerObj.run()', number=2)

controllerObj.run()
