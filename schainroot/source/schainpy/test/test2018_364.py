import os, sys
#import timeit
import datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "HF_EXAMPLE"
filename = "hf_test.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

number='3640'
#----------------------------------------------NEW----------------------------------------------------#
'''
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-code',action='store',dest='code_seleccionado',help='Code para generar Spectro off-line 0,1,2')
results= parser.parse_args()
print "CODE SELECCIONADO",str(results.code_seleccionado)

code= int(results.code_seleccionado)
'''
#-----------------------------------------------------------------------------------------------------#
#-------------------------PATH-PDATA--------------------------------------#
path='/media/igp-114/PROCDATA/'

#-----------------------------PATH-graficos-----------------------------------#
code=0# DEPENDE DEL CODIGO DE TX
figpath='/media/igp-114/graphics_schain/sp'+str(code)+'1_f1/'
#-------------------------------DOY -1 -------------------------------------#
doitnow = datetime.datetime.now() - datetime.timedelta(days=0)
y = doitnow.year
m = doitnow.month
d = int(doitnow.day)

date = str(y)+"/"+str(m)+"/"+str(d)

#date='2017/12/16'
#---------------------------------------------------------------------------#


readUnitConfObj = controllerObj.addReadUnit(datatype='HFReader',
                                            path=path,
                                            startDate=date,#2017/11/14
                                            endDate=date,#2017/11/14
                                            code=code,
     		                            frequency=3.64,
                                            startTime='18:05:00',
                                            endTime='23:59:59',
                                            online=0,
                                            set=0,
                                            delay=0,
                                            walk=1,
                                            timezone=-5*3600
                                            )

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj12 = procUnitConfObj0.addOperation(name='setRadarFrequency')
opObj12.addParameter(name='frequency', value='3.64e6', format='float')
# # 
procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='600', format='int')
procUnitConfObj1.addParameter(name='nProfiles', value='600', format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1)', format='pairsList')

opObj12 = procUnitConfObj1.addOperation(name='removeInterference')

#opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#opObj11.addParameter(name='n', value='10', format='float')


opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='1000', format='int')
opObj11.addParameter(name='wintitle', value='HF_Jicamarca_Spc', format='str')
#opObj11.addParameter(name='channelList', value='1', format='intlist')
opObj11.addParameter(name='xmin', value='-50', format='float')
opObj11.addParameter(name='xmax', value='50', format='float') 
#opObj11.addParameter(name='ymin', value='1485', format='float')
##opObj11.addParameter(name='ymax', value='1500', format='float')
opObj11.addParameter(name='zmin', value='-145', format='float')
opObj11.addParameter(name='zmax', value='-105', format='float')#-105
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')


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
opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')
opObj11.addParameter(name='COH', value='0', format='bool')
opObj11.addParameter(name='PHASE', value='1', format='bool')
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
opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')
###opObj11.addParameter(name='show', value='0', format='bool')
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
opObj21.addParameter(name='wintitle', value='Doppler-Radial Velocity Plot0', format='str')
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
opObj21.addParameter(name='wintitle', value='SNR_0', format='str')
opObj21.addParameter(name='channelList', value='0', format='intlist') 
#opObj21.addParameter(name='show', value='0', format='bool')
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
opObj21.addParameter(name='ftp_wei', value='11', format='int')
opObj21.addParameter(name='exp_code', value='555', format='int')
opObj21.addParameter(name='sub_exp_code', value=number, format='int')
opObj21.addParameter(name='plot_pos', value='1', format='int')   
opObj21.addParameter(name='ext', value='.jpeg', format='str')
#  # # # # # 

opObj21 = procUnitConfObj2.addOperation(name='ParametersPlot', optype='other')
opObj21.addParameter(name='id', value='8000', format='int')
opObj21.addParameter(name='wintitle', value='SNR_1', format='str')
opObj21.addParameter(name='channelList', value='1', format='intlist') 
#opObj11.addParameter(name='show', value='0', format='bool')
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
opObj21.addParameter(name='ftp_wei', value='11', format='int')
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
