'''
@author: Daniel Suarez
'''
import os
import glob
import ftplib
import multiprocessing
from model.proc.jroproc_base import ProcessingUnit, Operation

class FTP(object):
    """
    Ftp is a public class used to define custom File Transfer Protocol from "ftplib" python module
    
    Non-standard Python modules used: None
    
    Written by "Daniel Suarez":mailto:daniel.suarez@jro.igp.gob.pe  Oct. 26, 2010
    """
    
    def __init__(self,server = None, username=None, password=None, remotefolder=None):        
        """
        This method is used to setting parameters for FTP and establishing connection to remote server
        
        Inputs:
            server    - remote server IP Address 
            
            username    - remote server Username 
            
            password    - remote server password
            
            remotefolder    - remote server current working directory
        
        Return: void
        
        Affects: 
            self.status    - in Error Case or Connection Failed this parameter is set to 1 else 0
            
            self.folderList    - sub-folder list of remote folder
            
            self.fileList    - file list of remote folder
            
            
        """
        
        if ((server == None) and (username==None) and (password==None) and (remotefolder==None)):
            server, username, password, remotefolder = self.parmsByDefault()
        
        self.server = server
        self.username = username
        self.password = password
        self.remotefolder = remotefolder
        self.file = None
        self.ftp = None
        self.status = 0
        
        try:
            self.ftp = ftplib.FTP(self.server)
            self.ftp.login(self.username,self.password)
            self.ftp.cwd(self.remotefolder)            
#            print 'Connect to FTP Server: Successfully'
        
        except ftplib.all_errors:
            print 'Error FTP Service'
            self.status = 1
            return
        
        
        
        self.dirList = []

        try:
            self.dirList = self.ftp.nlst()
        
        except ftplib.error_perm, resp:
            if str(resp) == "550 No files found":
                    print "no files in this directory"
                    self.status = 1
                    return
        
        except ftplib.all_errors:
            print 'Error Displaying Dir-Files'
            self.status = 1
            return
        
        self.fileList = []
        self.folderList = []
        #only for test
        for f in self.dirList:
            name, ext = os.path.splitext(f)
            if ext != '':
                self.fileList.append(f)
#                print 'filename: %s - size: %d'%(f,self.ftp.size(f))

    def parmsByDefault(self):
        server = 'jro-app.igp.gob.pe'
        username = 'wmaster'
        password = 'mst2010vhf'
        remotefolder = '/home/wmaster/graficos'
        
        return server, username, password, remotefolder
        
    
    def mkd(self,dirname):
        """
        mkd is used to make directory in remote server
        
        Input:
            dirname    - directory name
        
        Return:
            1 in error case else 0
        """
        try: 
            self.ftp.mkd(dirname)
        except:
            print 'Error creating remote folder:%s'%dirname
            return 1
        
        return 0
    
    
    def delete(self,filename):
        """
        delete is used to delete file in current working directory of remote server
        
        Input:
            filename    - filename to delete in remote folder
            
        Return:
            1 in error case else 0
        """
        
        try:
            self.ftp.delete(filename)
        except:
            print 'Error deleting remote file:%s'%filename
            return 1
        
        return 0
    
    def download(self,filename,localfolder):
        """
        download is used to downloading file from remote folder into local folder
        
        Inputs:
            filename    - filename to donwload
            
            localfolder    - directory local to store filename
        
        Returns:
            self.status    - 1 in error case else 0
        """
        
        self.status = 0
        
        
        if not(filename in self.fileList):
            print 'filename:%s not exists'%filename
            self.status = 1
            return self.status
                
        newfilename = os.path.join(localfolder,filename)
                        
        self.file = open(newfilename, 'wb') 
        
        try:
            print 'Download: ' + filename                       
            self.ftp.retrbinary('RETR ' + filename, self.__handleDownload)
            print 'Download Complete'
        except ftplib.all_errors:
            print 'Error Downloading ' + filename
            self.status = 1
            return self.status
        
        self.file.close()
        
        return self.status 


    def __handleDownload(self,block):
        """
        __handleDownload is used to handle writing file
        """
        self.file.write(block)
    
    
    def upload(self,filename,remotefolder=None):
        """
        upload is used to uploading local file to remote directory
        
        Inputs:
            filename    - full path name of local file to store in remote directory
            
            remotefolder    - remote directory 
            
        Returns:
            self.status    - 1 in error case else 0
        """
        
        if remotefolder == None:
            remotefolder = self.remotefolder
        
        self.status = 0
        
        try:
            print "Remote_folder: %s"%(remotefolder)
            command_1="mkdir -p %s"%(remotefolder)
            os.system("ssh wmaster@181.177.232.125 %s"%(command_1))
            files_to_send=filename
            (head, tail) = os.path.split(filename)
            print files_to_send,1 
            print head+"/*.jpeg"
            files_to_send=head+"/*.jpeg"
            temp_command = "scp -P 6633 %s wmaster@181.177.232.125:%s"%(files_to_send,remotefolder)
            print "#==> Temp_Command:"
            print temp_command
            try:
                    os.system(temp_command)
            except:
                print "desgracia"
        except:
            self.status=1
            return self.status



        
    def dir(self,remotefolder):
        """
        dir is used to change working directory of remote server and get folder and file list
        
        Input:
            remotefolder    - current working directory
            
        Affects:
            self.fileList    - file list of working directory
        
        Return: 
            infoList    - list with filenames and size of file in bytes
            
            self.folderList    -    folder list
        """
        
        self.remotefolder = remotefolder
        print 'Change to ' + self.remotefolder
        try:        
            self.ftp.cwd(remotefolder)        
        except ftplib.all_errors:
            print 'Error Change to ' + self.remotefolder            
            infoList = None
            self.folderList = None
            return infoList,self.folderList
        
        self.dirList = []

        try:
            self.dirList = self.ftp.nlst()
        
        except ftplib.error_perm, resp:
            if str(resp) == "550 No files found":                    
                    print "no files in this directory"
                    infoList = None
                    self.folderList = None
                    return infoList,self.folderList
        except ftplib.all_errors:
            print 'Error Displaying Dir-Files'
            infoList = None
            self.folderList = None
            return infoList,self.folderList          
                
        infoList = [] 
        self.fileList = []
        self.folderList = []
        for f in self.dirList:
            name,ext = os.path.splitext(f)
            if ext != '':                                 
                self.fileList.append(f)
                value = (f,self.ftp.size(f))
                infoList.append(value)                    
            
            if ext == '':                
                self.folderList.append(f)
                 
        return infoList,self.folderList
                       
                        
    def close(self):
        """
        close is used to close and end FTP connection
        
        Inputs: None
        
        Return: void
        
        """
        self.ftp.close()

class SendByFTP(Operation):
    def __init__(self):
        self.status = 1
        self.counter = 0
    
    def error_print(self, ValueError):
        print ValueError, 'Error FTP'
        print "don't worry the program is running..."
    
    def worker_ftp(self, server, username, password, remotefolder, filenameList):
        
        self.ftpObj = FTP(server, username, password, remotefolder)
        for filename in filenameList:
            self.ftpObj.upload(filename)
        self.ftpObj.close()
    
    def ftp_thread(self, server, username, password, remotefolder):
        if not(self.status):
            return
        
        p = multiprocessing.Process(target=self.worker_ftp, args=(server, username, password, remotefolder, self.filenameList,))
        p.start()
        
        p.join(3)
        
        if p.is_alive():
            p.terminate()
            p.join()
            print 'killing ftp process...1'
            self.status = 0
            return
        
        self.status = 1
        return
    
    def filterByExt(self, ext, localfolder):
        fnameList = glob.glob1(localfolder,ext)
        self.filenameList = [os.path.join(localfolder,x) for x in fnameList]

        if len(self.filenameList) == 0:
            self.status = 0
    
    def run(self, dataOut, ext, localfolder, remotefolder, server, username, password, period=1):
        
        self.counter += 1 
        if self.counter >= period:
            self.filterByExt(ext, localfolder)
            
            self.ftp_thread(server, username, password, remotefolder)

            self.counter = 0
        
        self.status = 1
        
