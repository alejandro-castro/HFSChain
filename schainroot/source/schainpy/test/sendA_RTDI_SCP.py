import os,glob,datetime
import argparse
import pexpect #pip install --user  pexpect
import time

debugg = True

def sendBySCP(Incommand): #"%04d/%02d/%02d 00:00:00"%(tnow.year,tnow.month,tnow.day)
    username = "wmaster"
    password = "mst2010vhf"#"123456"
    #port = "-p6633"
    host = "jro-app.igp.gob.pe"#"25.59.69.206"
    #hostdirectory = "/home/wmaster/web2/web_signalchain/data/%s/%s/%s/figures"%(place,rxname,day)
    #command = "sshfs %s %s@%s:%s %s -o nonempty "%(port,username,host,hostdirectory,mountpoint)
    command = Incommand
    if debugg:
        print command
    try:
        #pexpect.spawn doesn't interpret shell meta characters,
        #console = pexpect.spawn(command)
        #Para reconocerlos se debe usar la siguiente linea >
        console = pexpect.spawn('/bin/bash', ['-c', command])
        console.expect(username + "@" + host + "'s password:")
        time.sleep(3)
        #usual response > wmaster@jro-app.igp.gob.pe's password:
        console.sendline(password)
        time.sleep(7)
        console.expect(pexpect.EOF)
        return True
    except Exception, e:
        if debugg:
            print str(e)
        return False

###################################INGRESANDO CODIGO 0 o 2##############################################################
parser = argparse.ArgumentParser()
parser.add_argument('-code',action='store',dest='code_seleccionado',help='Code para generar Spectro off-line 0,1,2')
parser.add_argument('-lo',action='store',dest='localstation',default =11 ,help='Codigo de estacion 11 JRO A, 12 JRO B, 21 HYO A, 22 HYO B, etc..')
results= parser.parse_args()
print "CODE SELECCIONADO",str(results.code_seleccionado)

code= int(results.code_seleccionado)
rxcode= int(results.localstation)
###########################################################################################################################
#currentdate = datetime.datetime.now()
#doitnow=currentdate.strftime("%j")
#doitnow=int(doitnow)-1# DIA DE ENVIO EL DIA ACTUAL -1

#dlist = [350,352,353,354,355]# LISTA DE DOY PARA ENVIAR
#dlist.append(doitnow)

tdstr = datetime.date.today()
str1 = tdstr + datetime.timedelta(days=-1)
yesterday = str1.strftime("%Y%j")
dlist =['2019029'] #AAAADOY ['2017365',]
#dlist = ['2018334','2018335','2018347','2018349','2018351']
dlist.append(yesterday)


# EL PATH CORRESPONDE A LA ESTACION HFA
PATH='/home/hfuser/RTDI/graphics_schain/'
graph_freq0=PATH+'sp'+str(code)+'1_f0'
graph_freq1=PATH+'sp'+str(code)+'1_f1'

#TESTING PART 1
print "We are testing ... uncomment pathlines."
graph_freq0 = '/home/jm/Documents/2018.HF'
graph_freq1 = '/home/jm/Documents/2018.HF'


for file in dlist:
    '''
    if file<10:
       before='d201800'
    if 9<file<100:
       before='d20180'
    if 99<file:
       before='d2018'
    doy=before+str(file)
    '''
    doy = 'd'+file
    print 'doy>',doy
    jpg_files = glob.glob("%s/%s/*.jpeg"%(graph_freq1, doy))
    jpg_files.sort()
    print jpg_files
    if len(jpg_files) is 0:
        print 'No hay figuras en la carpeta!!!'

    file_1=os.path.basename(jpg_files[0])

    YEAR=int (file_1[0:4])
    DAYOFYEAR= int(file_1[4:7])
    DAYOFYEAR_str = file_1[4:7]
    d = datetime.date(YEAR, 1, 1) + datetime.timedelta(DAYOFYEAR - 1)
    print 'd.strftime("%Y/%m/%d")>', d.strftime("%Y/%m/%d")

    MONTH = d.strftime("%m")
    print MONTH
    #DAY=d.day
    #if DAY<10:
    #   DAY='0'+str(DAY)
    DAY = d.strftime("%d")
    print DAY

    AorB = rxcode%2 # Si es par(B) AorB sera 0, si es impar(A) AorB sera 1.
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

    remote_folder="/home/wmaster/web2/web_rtdi/data/JRO/%s/%s/%s/%s/figures/"%(station_name, YEAR, MONTH,DAY)
    remote_folder="/home/wmaster/web2/web_rtdi/data/BARRANCA/%s/%s/%s/%s/figures/"%(station_name, YEAR, MONTH,DAY)
    print "Remote_folder: %s"%(remote_folder)
    #Primer Comando, generar carpeta de destino.

    command_1="ssh wmaster@jro-app.igp.gob.pe -p 6633 mkdir -p %s"%(remote_folder)
    if sendBySCP(command_1):
        print 'Carpeta Creada'

    #os.system("ssh wmaster@jro-app.igp.gob.pe -p 6633 %s "%(command_1))

    #Segundo comando, pasar las imagenes necesarias para la freq 0
    #TODO > Agregar al filtro el year/doy/con el codigo de estacion/* para que no envie todos los datos.

    temp_command = "scp -r -P 6633 %s/%s/%s%s%s*.jpeg wmaster@jro-app.igp.gob.pe:%s"%(graph_freq0,doy,YEAR,DAYOFYEAR_str,rxcode,remote_folder)
    #temp_command = "scp -P 6633 %s/%s/ wmaster@jro-app.igp.gob.pe:%s"%(graph_freq0,doy,remote_folder)
    print "Temp_Command: ==========================================="
    print temp_command

    if sendBySCP(temp_command):
        print 'Datos Enviados'
    #Segundo comando, pasar las imagenes necesarias para la freq 1                    AQUI
    temp_command = "scp -r -P 6633 %s/%s/*.jpeg wmaster@jro-app.igp.gob.pe:%s"%(graph_freq1,doy,remote_folder)
    print "Temp_Command 2: "
    print temp_command
    #os.system(temp_command)

'''
sudoPassword = 'mypass'
command = 'mount -t vboxsf myfolder /home/myuser/myfolder'
p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))
Try this and let me know if it works. :-)

And this one:

os.popen("sudo -S %s"%(command), 'w').write('mypass')


process = os.popen('gcc -E myHeader.h')
preprocessed = process.read()
process.close()

'''
