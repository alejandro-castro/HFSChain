




import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "Sousy_test"
filename = "sousy_processing.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='Test_sousy', description=desc)

#path = '/media/data/data/vientos/57.2063km/echoes/NCO_Woodman'
#path2= '/media/'
#path2='/media/New Volume/LowTroposphere'
#path1='/media/New Volume/LT_shortpulse'
#path = path1 + ',' + path2
path='G:\\LowTroposphere'

path = '/media/signalchain/FVillanuevaR/LowTroposphere'
wr_path = '/media/signalchain/datos/sousy'
figures_path = '/home/signalchain/Pictures/sousy'

readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2014/07/08',
                                            endDate='2014/07/08',
                                            startTime='10:00:00',
                                            endTime='17:59:59',
                                            delay=0,
                                            set=0,
                                            online=0,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')
#########################################################
################ SOUSY###################################
#########################################################
#
procUnitConfObjSousy = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
#
# codigo64='1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,1,0,1,1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,0,0,0,1,0,0,1,0,1,1,1,0,0,0,1,0,'+\
#              '1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,1,0,1,0,0,0,1,0,0,1,0,0,0,0,1,1,1,0,1,1,1,1,0,1,1,0,1,0,0,0,1,1,1,0,1'
opObj11 = procUnitConfObjSousy.addOperation(name='setRadarFrequency')
opObj11.addParameter(name='frequency', value='53.5e6', format='float')



opObj11 =  procUnitConfObjSousy.addOperation(name='filterByHeights')
opObj11.addParameter(name='window', value='2', format='int')

codigo='1,-1'
opObj11 = procUnitConfObjSousy.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value=codigo, format='floatlist')
opObj11.addParameter(name='nCode', value='2', format='int')
opObj11.addParameter(name='nBaud', value='1', format='int')

opObj11 = procUnitConfObjSousy.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='2048', format='int')

procUnitConfObjSousySpectra = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjSousy.getId())
procUnitConfObjSousySpectra.addParameter(name='nFFTPoints', value='64', format='int')
procUnitConfObjSousySpectra.addParameter(name='nProfiles', value='64', format='int')

opObj13 = procUnitConfObjSousySpectra.addOperation(name='removeDC')
opObj13.addParameter(name='mode', value='2', format='int')

opObj11 = procUnitConfObjSousySpectra.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='1', format='float')
# 
# opObj11 = procUnitConfObjSousySpectra.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='101', format='int')
# opObj11.addParameter(name='wintitle', value='Sousy_RTIPlot', format='str')
# opObj11.addParameter(name='zmin', value='30', format='int')
# opObj11.addParameter(name='zmax', value='100', format='int')
# opObj11.addParameter(name='ymin', value='0', format='int')
# opObj11.addParameter(name='ymax', value='10', format='int')
# opObj11.addParameter(name='xmin', value='10', format='float')
# opObj11.addParameter(name='xmax', value='18', format='float')
# opObj11.addParameter(name='showprofile', value='0', format='int')
# opObj11.addParameter(name='save', value='1', format='int')
# #opObj11.addParameter(name='figfile', value='rti0_sousy.png', format='str')
# opObj11.addParameter(name='figpath', value=figures_path, format='str')

opObj11 = procUnitConfObjSousySpectra.addOperation(name='SpectraWriter', optype='other')
opObj11.addParameter(name='path', value=wr_path)
opObj11.addParameter(name='blocksPerFile', value='100', format='int')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()