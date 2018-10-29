import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "EWDrifts+Imaging+Faraday Experiments"
filename = "mst_plots.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)


path = '/media/DATA/isr2014'
figpath = '/home/operaciones/Pictures/isr_mayo2014'
readUnitConfObj = controllerObj.addReadUnit(datatype='Spectra',
                                            path=path,
                                            startDate='2014/01/08',
                                            endDate='2014/01/08',
                                            startTime='10:00:00',
                                            endTime='14:59:59',
                                            delay=20,
                                            online=1,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObjMSTSpectra = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())




opObj11 = procUnitConfObjMSTSpectra.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='215', format='int')
opObj11.addParameter(name='wintitle', value='MST', format='str')
opObj11.addParameter(name='ymin', value='120', format='int')
opObj11.addParameter(name='ymax', value='190', format='int')
opObj11.addParameter(name='zmin', value='20', format='int')
opObj11.addParameter(name='zmax', value='50', format='int')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/mst_mayo2014', format='str')
opObj11.addParameter(name='wr_period', value='1', format='int')
opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
opObj11.addParameter(name='folder', value='/home/wmaster/graficos', format='str')
opObj11.addParameter(name='username', value='wmaster', format='str')
opObj11.addParameter(name='password', value='mst2010vhf', format='str')
opObj11.addParameter(name='ftp_wei', value='0', format='int')
opObj11.addParameter(name='exp_code', value='19', format='int')
opObj11.addParameter(name='sub_exp_code', value='0', format='int')
opObj11.addParameter(name='plot_pos', value='0', format='int') 


opObj11 = procUnitConfObjMSTSpectra.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='301', format='int')
opObj11.addParameter(name='wintitle', value='ISR', format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='xmin', value='0', format='int')
opObj11.addParameter(name='xmax', value='24', format='int')
opObj11.addParameter(name='ymin', value='120', format='int')
opObj11.addParameter(name='ymax', value='190', format='int')
opObj11.addParameter(name='zmin', value='20', format='int')
opObj11.addParameter(name='zmax', value='50', format='int')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/mst_mayo2014', format='str')
opObj11.addParameter(name='wr_period', value='5', format='int')
opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
opObj11.addParameter(name='folder', value='/home/wmaster/graficos', format='str')
opObj11.addParameter(name='username', value='wmaster', format='str')
opObj11.addParameter(name='password', value='mst2010vhf', format='str')
opObj11.addParameter(name='ftp_wei', value='0', format='int')
opObj11.addParameter(name='exp_code', value='19', format='int')
opObj11.addParameter(name='sub_exp_code', value='0', format='int')
opObj11.addParameter(name='plot_pos', value='0', format='int') 



print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()