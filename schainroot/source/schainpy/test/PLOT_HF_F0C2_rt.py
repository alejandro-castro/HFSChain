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
#----------------------------------------------NEW----------------------------------------------------#
'''
example:
python PLOT_HF.py  -path '/media/igp-114/PROCDATA' -f 2.72 -C 0 -ii 6 -online 0 -code 0 -date "2018/01/25" -startTime "00:00:00" -endTime "23:59:59"
'''
print "REVISAR LA LINEA DE EJEMPLO EN EL ARCHIVO EN CASO PROBLEMAS DE EJECUCION"
import argparse
parser = argparse.ArgumentParser()
########################## PATH- DATA  ###################################################################################################
parser.add_argument('-path',action='store',dest='path_lectura',help='Directorio de Datos \
					.Por defecto, se esta ingresando entre comillas /media/igp-114/PROCDATA/',default='/media/igp-114/PROCDATA/')
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
                                                                                Example: XA   ----- X: Es el primer valor determina la ubicacion de la estacion. A: Es \
                                                                                                  el segundo valor determina la orientacion N45O o N45E.  \
                                                                                                        11: JRO-N450, 12: JRO-N45E \
                                                                                                        21: HYO-N45O, 22: HYO-N45E',default=11)
###########################################################################################################################################



###########################################################################################################################################
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
##################CONFIGURACION DE TIEMPO REAL##########################################################
freq=2.72
code=2
online=1
lo=lo  ###### OJO AQUI DEBEMOS MODIFICAR DEPENDIENDO DE LA UBICACION DE LA ESTADION DEFAULT 11
lo=31
########################################################################################################

nProfiles = 100
nFFT      = 100
set       = 0

if campaign == 1:
	nProfiles=600
   	nFFT     =600
	inc_int= 0
if online == 1:
        date      = today
	time_start= "00:00:00"
	time_end  = "23:59:59"
	set = None

ngraph= 1
if freq <3:
	ngraph= 0

setupF   = freq
setradarF= freq*10**6
numberF  = int(freq*10**3)
number   = str(numberF)
lo_n=lo/10
lo_0=lo_n*10+1
lo_1=lo_0+1
print "Path",path
print "Frecuencia en Mhz",freq
print "Freq_setup",freq
print "Freq_setradar",setradarF
print "Freq_number", numberF
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
print "REVISAR LA LINEA DE EJEMPLO EN EL ARCHIVO EN CASO PROBLEMAS DE EJECUCION"

time.sleep(4)
#-----------------------------------------------------------------------------------------------------#
#-------------------------PATH-PDATA-------------------------------------
#path='/media/igp-114/PROCDATA/'
#-----------------------------PATH-graficos-----------------------------------#
figpath='/media/igp-114/graphics_schain/realtime/sp'+str(code)+'1_f'+str(ngraph)+'/'####TIEMPO REAL GRAFICOS
print "figpath",figpath    
#---------------------------------------------------------------------------#
readUnitConfObj = controllerObj.addReadUnit(datatype = 'HFReader',
                                            path     = path,
                                            startDate= date,   #'2017/12/31',# 2017/11/14 date
                                            endDate  = date,   #'2017/12/31',#date 2017/11/14
                                            code     = code,
     		                            frequency= setupF,
				            campaign = campaign,
					    inc_int  = inc_int,
                                            startTime= time_start,
                                            endTime  = time_end,
                                            online   = online,
#                                            set      = set,
                                            delay    = 0,
                                            walk     = 1,
                                            timezone = -5*3600
                                            )

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj12 = procUnitConfObj0.addOperation(name='setRadarFrequency')
opObj12.addParameter(name='frequency', value=setradarF, format='float')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value=nFFT, format='int')
procUnitConfObj1.addParameter(name='nProfiles', value=nProfiles, format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1)', format='pairsList')

#opObj12 = procUnitConfObj1.addOperation(name='removeInterference')

# opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
# opObj11.addParameter(name='n', value='6', format='float')


opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='1000', format='int')
opObj11.addParameter(name='wintitle', value='HF_Jicamarca_Spc_F0C2', format='str')
#opObj11.addParameter(name='channelList', value='1', format='intlist')
opObj11.addParameter(name='xmin', value='-50', format='float')
opObj11.addParameter(name='xmax', value='50', format='float') 
##opObj11.addParameter(name='ymin', value='1485', format='float')
##opObj11.addParameter(name='ymax', value='1500', format='float')
opObj11.addParameter(name='zmin', value='-145', format='float')
opObj11.addParameter(name='zmax', value='-105', format='float')#-105
opObj11.addParameter(name='save_ftp', value='1', format='bool')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='data_time_save',value='1',format='bool')
opObj11.addParameter(name='wr_period', value='10', format='int')
opObj11.addParameter(name='ftp_wei', value='11', format='int')
opObj11.addParameter(name='exp_code', value='444', format='int')
opObj11.addParameter(name='sub_exp_code', value=number, format='int')
opObj11.addParameter(name='plot_pos', value='1', format='int')
opObj11.addParameter(name='ext', value='.jpeg', format='str')


# # opObj11.addParameter(name='figfile', value=figfile_spectra_name, format='str')
# # opObj11.addParameter(name='wr_period', value='5', format='int')
# #opObj11.addParameter(name='ftp_wei', value='0', format='int')
# #opObj11.addParameter(name='exp_code', value='20', format='int')
# #opObj11.addParameter(name='sub_exp_code', value='0', format='int')
# #opObj11.addParameter(name='plot_pos', value='0', format='int')
 
##opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
##opObj11.addParameter(name='id', value='2000', format='int')
##opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')
##opObj11.addParameter(name='showprofile', value='0', format='int')
###opObj11.addParameter(name='channelList', value='0', format='intlist') 
##opObj11.addParameter(name='xmin', value='0', format='float')
##opObj11.addParameter(name='xmax', value='24', format='float')
##opObj11.addParameter(name='zmin', value='-145', format='float')
##opObj11.addParameter(name='zmax', value='-105', format='float')
##opObj11.addParameter(name='save', value='1', format='bool')
##opObj11.addParameter(name='figpath', value=figpath, format='str')
### # # # opObj11.addParameter(name='figfile', value=figfile_power_name, format='str')
##opObj11.addParameter(name='data_time_save',value='1',format='bool')
##opObj11.addParameter(name='wr_period', value='10', format='int')
##opObj11.addParameter(name='ftp_wei', value='1', format='int')
##opObj11.addParameter(name='exp_code', value='444', format='int')
##opObj11.addParameter(name='sub_exp_code', value='2720', format='int')
##opObj11.addParameter(name='plot_pos', value='1', format='int')
##opObj11.addParameter(name='ext', value='.jpeg', format='str')
'''
opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
opObj11.addParameter(name='id', value='3000', format='int')
opObj11.addParameter(name='wintitle', value='HF_Jicamarca_Phase_F0C2', format='str')
opObj11.addParameter(name='COH', value='0', format='bool')
opObj11.addParameter(name='PHASE', value='1', format='bool')
opObj11.addParameter(name='show', value='0', format='bool')
opObj11.addParameter(name='xmin', value='0', format='float')
opObj11.addParameter(name='xmax', value='24', format='float')
# # opObj11.addParameter(name='channelList', value='0', format='intlist') 
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='pairsList', value='(0,1)', format='pairsList')
# # opObj11.addParameter(name='figfile', value="Phase_2.72Mhz.jpg", format='str')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='data_time_save',value='1',format='bool')
opObj11.addParameter(name='wr_period', value='10', format='int')
opObj11.addParameter(name='ftp_wei', value='11', format='int')
opObj11.addParameter(name='exp_code', value='888', format='int')
opObj11.addParameter(name='sub_exp_code', value=number, format='int')
opObj11.addParameter(name='plot_pos', value='1', format='int')
opObj11.addParameter(name='ext', value='.jpeg', format='str')

opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
opObj11.addParameter(name='id', value='3002', format='int')
opObj11.addParameter(name='wintitle', value='HF_Jicamarca_Coh_F0C2', format='str')
opObj11.addParameter(name='show', value='0', format='bool')
opObj11.addParameter(name='COH', value='1', format='bool')
opObj11.addParameter(name='PHASE', value='0', format='bool')
opObj11.addParameter(name='xmin', value='0', format='float')
opObj11.addParameter(name='xmax', value='24', format='float')
####opObj11.addParameter(name='channelList', value='0', format='intlist') 
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='pairsList', value='(0,1)', format='pairsList')
####opObj11.addParameter(name='figfile', value="Coherencia_2.72Mhz.jpg", format='str')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='data_time_save',value='1',format='bool')
opObj11.addParameter(name='wr_period', value='10', format='int')
opObj11.addParameter(name='ftp_wei', value='11', format='int')
opObj11.addParameter(name='exp_code', value='999', format='int')
opObj11.addParameter(name='sub_exp_code', value=number, format='int')
opObj11.addParameter(name='plot_pos', value='1', format='int')
opObj11.addParameter(name='ext', value='.jpeg', format='str')
'''
procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj1.getId())
opObj20 = procUnitConfObj2.addOperation(name='GetMoments')
'''  
opObj21 = procUnitConfObj2.addOperation(name='ParametersPlot', optype='other')
opObj21.addParameter(name='id', value='4000', format='int')
opObj21.addParameter(name='wintitle', value='Doppler-Radial Velocity Plot0 F0C2', format='str')
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
opObj21.addParameter(name='wr_period', value='10', format='int')
opObj21.addParameter(name='ftp_wei', value='11', format='int')
opObj21.addParameter(name='exp_code', value='777', format='int')
opObj21.addParameter(name='sub_exp_code', value=number, format='int')
opObj21.addParameter(name='plot_pos', value='1', format='int')
opObj21.addParameter(name='ext', value='.jpeg', format='str')
#  # # # # #    
'''
opObj21 = procUnitConfObj2.addOperation(name='ParametersPlot', optype='other')
opObj21.addParameter(name='id', value='7000', format='int')
opObj21.addParameter(name='wintitle', value='SNR_0 F0C2', format='str')
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
opObj21.addParameter(name='wr_period', value='10', format='int')
opObj21.addParameter(name='ftp_wei', value=str(lo_0), format='int')
opObj21.addParameter(name='exp_code', value='555', format='int')
opObj21.addParameter(name='sub_exp_code', value=number, format='int')
opObj21.addParameter(name='plot_pos', value='1', format='int')   
opObj21.addParameter(name='ext', value='.jpeg', format='str')
#  # # # # # 

opObj21 = procUnitConfObj2.addOperation(name='ParametersPlot', optype='other')
opObj21.addParameter(name='id', value='8000', format='int')
opObj21.addParameter(name='wintitle', value='SNR_1 F0C2', format='str')
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
opObj21.addParameter(name='wr_period', value='10', format='int')
opObj21.addParameter(name='ftp_wei', value=str(lo_1), format='int')
opObj21.addParameter(name='exp_code', value='666', format='int')
opObj21.addParameter(name='sub_exp_code', value=number, format='int')
opObj21.addParameter(name='plot_pos', value='1', format='int')
opObj21.addParameter(name='ext', value='.jpeg', format='str') 

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()

#timeit.timeit('controllerObj.run()', number=2)

controllerObj.run()

