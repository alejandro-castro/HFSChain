import os, sys
#import timeit
import datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import Project
######################CONFIGURACION DE OUT##########################333
####default 1424 y por test de operacion continua 10 segundos 1440*6 =8640
blocksPerFile='1440'
#-------------------------------DOY -1 -------------------------------------#
doitnow = datetime.datetime.now() - datetime.timedelta(days=2)
y = doitnow.year
m = doitnow.month
d = int(doitnow.day)

date = str(y)+"/"+str(m)+"/"+str(d)
#---------------------------------------------------------------------------#
#date='2018/01/12'
# comentar en caso operacion diario
#---------------------------------------
freq1="_2.72MHz_"
freq2="_3.64MHz_"
ext_img=".jpeg"
#---------------------------------------
desc = "HF_PROCESS_EXAMPLE"
filename = "hf_15process.xml"
controllerObj = Project()
controllerObj.setup(id = '191', name='test01', description=desc)

number='2720'
############################## SELECCIONAR DIA####################
# # # # import argparse
# # # # parser = argparse.ArgumentParser()
# # # # parser.add_argument('-d',action='store',dest='dia_seleccionado',help='Dia para generar RTDI off-line')
# # # # results= parser.parse_args()
# # # # print "DAY SELECCIONADO",str(results.dia_seleccionado)
# # # # 
# # # # YEAR=int(2017)
# # # # DAYOFYEAR= int(results.dia_seleccionado)
# # # # d= datetime.date(YEAR,1,1) + datetime.timedelta(DAYOFYEAR-1)
# # # # #print d,"veamos"
# # # # #print YEAR,"YEAR"
# # # # MONTH = d.month
# # # # if MONTH < 10:
# # # #         MONTH='0'+str(MONTH)
# # # # #print MONTH,"MONTH"
# # # # DAY= d.day
# # # # if DAY < 10:
# # # #         DAY = '0'+ str(DAY)
# # # # #print DAY,"DAY"
# # # # date = str(YEAR)+"/"+str(MONTH)+"/"+str(DAY)
# # # # print date,"DIA SELECCIONADO"
#####################################################################################
#-------------------------PATH-PDATA--------------------------------------#
#path='/media/igp-114/PROCDATA/'
#path='/home/alex/DATA_SPEC/'
path='/home/hfuser1204/HFA'
#-----------------------------PATH-graficos-----------------------------------#
code=0# DEPENDE DEL CODIGO DE TX
#figpath='/media/igp-114/graphics_schain/sp'+str(code)+'1_f0/'
#figpath='/home/alex/DATA_SPEC/graphics_schain/sp'+str(code)+'1_f0/'
figpath='/home/hfuser1204/RTDI/graphics_schain/sp'+str(code)+'1_f0/'
#---------------------------------------------------------------------------#
readUnitConfObj = controllerObj.addReadUnit(datatype='HFReader',
                                            path=path,
                                            startDate=date,#2017/11/14
                                            endDate=date,#2017/11/14
                                            campaign = 1,
                                            inc_int  = 0,
                                            code=code,
                                            frequency=2.72,
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            set=0,
                                            delay=0,
                                            walk=1,
                                            timezone=-5*3600
                                            )

#opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

#opObj11 = readUnitConfObj.addOperation(name='printTotalBlocks')
procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj12 = procUnitConfObj0.addOperation(name='setRadarFrequency')
opObj12.addParameter(name='frequency', value='2.72e6', format='float')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='600', format='int')
procUnitConfObj1.addParameter(name='nProfiles', value='600', format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1)', format='pairsList')

procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj1.getId())
opObj20 = procUnitConfObj2.addOperation(name='GetMoments')
channel='0'
cod_tx=str(code)
procUnitConfObj3= controllerObj.addProcUnit(datatype='ImageProc',inputId=procUnitConfObj2.getId())
procUnitConfObj3.addParameter(name='channel', value=channel, format='int')
procUnitConfObj3.addParameter(name='threshv', value='0.1', format='float')

opObj11= procUnitConfObj3.addOperation(name='ImageWriter',optype='other')
opObj11.addParameter(name='blocksPerFile', value=blocksPerFile, format='int') ####default 1424 y por test de operacion continua 10 segundos 1440*6 =8640
opObj11.addParameter(name='standard', value='1', format='bool')
opObj11.addParameter(name='c_station_o', value='11', format='str')
opObj11.addParameter(name='c_freq', value='272', format='str')
opObj11.addParameter(name='c_cod_Tx', value=cod_tx, format='str')
opObj11.addParameter(name='c_ch', value=channel, format='str')
opObj11.addParameter(name='path',value=figpath) 

# # # 
# opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='401', format='int')
# opObj11.addParameter(name='wintitle', value='HF', format='str')
# opObj11.addParameter(name='zmin', value='-145', format='int')
# opObj11.addParameter(name='zmax', value='-105', format='int')
# # # opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='wr_period', value='5', format='int')

number='2720'
opObj11 = procUnitConfObj3.addOperation(name='RTDIPlot', optype='other')
opObj11.addParameter(name='id', value='402', format='int')
opObj11.addParameter(name='wintitle', value='HF_RTDI', format='str')
opObj11.addParameter(name='showprofile', value='1', format='int')
opObj11.addParameter(name='xmin', value='0', format='int')
opObj11.addParameter(name='xmax', value='24', format='int')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value=figpath, format='str')
#opObj11.addParameter(name='figfile', value="holi.jpeg", format='str')
opObj11.addParameter(name='data_time_save',value='1',format='bool')
# opObj11.addParameter(name='ftp_wei', value='11', format='int')
# opObj11.addParameter(name='exp_code', value='888', format='int')
# opObj11.addParameter(name='sub_exp_code', value=number, format='int')
# opObj11.addParameter(name='plot_pos', value='1', format='int')
opObj11.addParameter(name='ext', value='.jpeg', format='str')
opObj11.addParameter(name='standard', value='1', format='bool')
opObj11.addParameter(name='c_station_o', value='11', format='str')
opObj11.addParameter(name='c_web', value='5', format='str')
opObj11.addParameter(name='c_freq', value='272', format='str')
opObj11.addParameter(name='c_cod_Tx', value=cod_tx, format='str')
opObj11.addParameter(name='c_ch', value=channel, format='str')
 
# opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
# opObj11.addParameter(name='id', value='3000', format='int')
# opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')
# opObj11.addParameter(name='showprofile', value='1', format='int')
# opObj11.addParameter(name='xmin', value='0', format='float')
# opObj11.addParameter(name='xmax', value='24', format='float')
# #opObj11.addParameter(name='channelList', value='0', format='intlist') 
# opObj11.addParameter(name='save', value='1', format='bool')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='wr_period', value='2', format='int')



print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
