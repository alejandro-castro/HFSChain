import os,glob,datetime
import argparse
import pexpect #pip install --user  pexpect
import time
# En caso no se pueda enviar hacer escribir etas lineas >

#ssh -X -C wmaster@jro-app.igp.gob.pe -p 6633

#Resultado >
#The authenticity of host '[jro-app.igp.gob.pe]:6633 ([181.177.244.71]:6633)' can't be established.
#RSA key fingerprint is 24:ea:fe:d5:4e:91:8d:82:d5:7d:1f:bf:e2:0c:36:70.
#Are you sure you want to continue connecting (yes/no)? yes

debug = True

def sendBySCP(Incommand): #"%04d/%02d/%02d 00:00:00"%(tnow.year,tnow.month,tnow.day)
	username = "wmaster"
	password = "mst2010vhf"#"123456"
	#port = "-p6633"
	host = "jro-app.igp.gob.pe"#"25.59.69.206"
	#hostdirectory = "/home/wmaster/web2/web_signalchain/data/%s/%s/%s/figures"%(place,rxname,day)
	#command = "sshfs %s %s@%s:%s %s -o nonempty "%(port,username,host,hostdirectory,mountpoint)
	command = Incommand
	if debug:
		print command
	try:
		#pexpect.spawn doesn't interpret shell meta characters,
		#console = pexpect.spawn(command)
		#Para reconocerlos se debe usar la siguiente linea >
		console = pexpect.spawn('/bin/bash', ['-c',command])
		console.expect(username + "@" + host + "'s password:")
		time.sleep(3)
		#usual response > wmaster@jro-app.igp.gob.pe's password:
		console.sendline(password)
		time.sleep(7)
		console.expect(pexpect.EOF)
		return True
	except Exception, e:
		if debug:
			print str(e)
		return False

###################################INGRESANDO CODIGO 0 o 2##############################################################
parser = argparse.ArgumentParser()
parser.add_argument('-code',action='store',dest='code_seleccionado',help='Code para generar Spectro off-line 0,1,2')
parser.add_argument('-lo',action='store',dest='localstation',default =11 ,help='Codigo de estacion 11 JRO A, 12 JRO B, 21 HYO A, 22 HYO B, etc..')
results= parser.parse_args()
code= int(results.code_seleccionado)
rxcode= int(results.localstation)

###########################################################################################################################
tdstr = datetime.date.today()
str1 = tdstr + datetime.timedelta(days=-1)
yesterday = str1.strftime("%Y%j")

dlist = []

dlist.append(yesterday)


# EL PATH CORRESPONDE A LA ESTACION HFA

PATH='/home/hfuser1204/RTDI/graphics_schain/'
graph_freq0=PATH+'sp'+str(code)+'1_f0'
graph_freq1=PATH+'sp'+str(code)+'1_f1'



for file in dlist:

	doy = 'd'+file
	jpg_files = glob.glob("%s/%s/*.jpeg"%(graph_freq1, doy))
	jpg_files.sort()
	print "%s/%s/*.jpeg"%(graph_freq1, doy)
	if len(jpg_files) is 0:
		print 'No hay RESULTADOS en la carpeta!!!'
		continue
	file_1=os.path.basename(jpg_files[0])

	YEAR=int (file_1[0:4])
	DAYOFYEAR= int(file_1[4:7])
	DAYOFYEAR_str = file_1[4:7]
	d = datetime.date(YEAR, 1, 1) + datetime.timedelta(DAYOFYEAR - 1)
	print "(1) Determinando dia a enviar."
	print 'd.strftime("%Y/%m/%d")>', d.strftime("%Y/%m/%d")

	MONTH = d.strftime("%m")
	DAY = d.strftime("%d")
	AorB = rxcode%2 # Si es par(B) AorB sera 0, si es impar(A) AorB sera 1.

	if rxcode == 11 or rxcode == 12 :
		rxname = 'JRO'
	if rxcode == 21 or rxcode == 22 :
		rxname = 'HUANCAYO'
	if rxcode == 31 or rxcode == 32 :
		rxname = 'MALA'
	if rxcode == 41 or rxcode == 42 :
		rxname = 'MERCED'
	if rxcode == 51 or rxcode == 52 :
		rxname = 'BARRANCA'
	if rxcode == 61 or rxcode == 62 :
		rxname = 'OROYA'


	if code ==0 and AorB == 1:
		station_name="HFTXANCON"
	if code ==0 and AorB == 0:
		station_name="HFBTXANCON"
	if code ==1 and AorB == 1:
		station_name="HFTXSICAYA"
	if code ==1 and AorB == 0:
		station_name="HFBTXSICAYA"
	if code ==2 and AorB == 1:
		station_name="HFTXICA"
	if code ==2 and AorB == 0:
		station_name="HFBTXICA"

	#remote_folder="/home/wmaster/web2/web_rtdi/data/JRO/%s/%s/%s/%s/figures/"%(station_name, YEAR, MONTH,DAY)
	remote_folder="/home/wmaster/web2/web_rtdi/data/%s/%s/%s/%s/%s/figures/"%(rxname,station_name, YEAR, MONTH,DAY)
	print "(2) Direccion de llegada de datos."
	print "Remote_folder: %s"%(remote_folder)
	#Primer Comando, generar carpeta de destino.

	command_1="ssh wmaster@jro-app.igp.gob.pe -p 6633 mkdir -p %s"%(remote_folder)
	if sendBySCP(command_1):
		print 'Carpeta Creada'

	#os.system("ssh wmaster@jro-app.igp.gob.pe -p 6633 %s "%(command_1))

	#Segundo comando, pasar las imagenes necesarias para la freq 0
	print "(3) Enviando resultados frecuencia 0"
	temp_command = "scp -r -P 6633 %s/%s/%s%s%s*.jpeg wmaster@jro-app.igp.gob.pe:%s"%(graph_freq0,doy,YEAR,DAYOFYEAR_str,rxcode,remote_folder)
	if sendBySCP(temp_command):
		print ' -- Datos Enviados F0'
	#Segundo comando, pasar las imagenes necesarias para la freq 1					AQUI
	#temp_command = "scp -r -P 6633 %s/%s/*.jpeg wmaster@jro-app.igp.gob.pe:%s"%(graph_freq1,doy,remote_folder)
	print "(4) Enviando resultados frencuencia 1"
	temp_command = "scp -r -P 6633 %s/%s/%s%s%s*.jpeg wmaster@jro-app.igp.gob.pe:%s"%(graph_freq1,doy,YEAR,DAYOFYEAR_str,rxcode,remote_folder)
	if sendBySCP(temp_command):
		print ' -- Datos enviados F1 '
