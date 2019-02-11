import os,glob,datetime
import argparse
import pexpect #pip install --user  pexpect
import time
#SOY NUEVO HOLA
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
        console = pexpect.spawn('/bin/bash', ['-c',command])
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
parser.add_argument('-code',action='store',dest='code_seleccionado',default = 0,help='Code para generar Spectro off-line 0,1,2')
parser.add_argument('-lo',action='store',dest='localstation',default =11 ,help='Codigo de estacion 11 JRO A, 12 JRO B, 21 HYO A, 22 HYO B, etc..')
results= parser.parse_args()
code= int(results.code_seleccionado)
rxcode= int(results.localstation)

###########################################################################################################################
#filelog = glob.glob("/media/igp-114/PROCDATA/*.txt")
#file_1=os.path.basename(filelog[0])
#remote_folder="/home/wmaster/web2/web_rtdi/data/JRO/%s/%s/%s/%s/figures/"%(station_name, YEAR, MONTH,DAY)
remote_folder="/home/wmaster/web2/web_signalchain/data/BARRANCA/"
temp_command = "scp -r -P 6633 /media/igp-114/PROCDATA/*.txt wmaster@jro-app.igp.gob.pe:%s"%(remote_folder)
if sendBySCP(temp_command):
    print ' - Envio de data log Terminado '
