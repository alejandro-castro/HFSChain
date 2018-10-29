import os
import datetime
import numpy
import copy

from figure import Figure, isRealtime

class CorrelationPlot(Figure):
    
    isConfig = None
    __nsubplots = None
    
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'corr'
    
    def __init__(self):
        
        self.isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 280
        self.HEIGHT = 250
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0
        
        self.PLOT_CODE = 1
        self.FTP_WEI = None
        self.EXP_CODE = None
        self.SUB_EXP_CODE = None
        self.PLOT_POS = None
        
    def getSubplots(self):
        
        ncol = int(numpy.sqrt(self.nplots)+0.9)
        nrow = int(self.nplots*1./ncol + 0.9)
        
        return nrow, ncol
    
    def setup(self, id, nplots, wintitle, showprofile=False, show=True):
               
        showprofile = False       
        self.__showprofile = showprofile
        self.nplots = nplots
        
        ncolspan = 1
        colspan = 1
        if showprofile:
            ncolspan = 3
            colspan = 2
            self.__nsubplots = 2
        
        self.createFigure(id = id,
                          wintitle = wintitle,
                          widthplot = self.WIDTH + self.WIDTHPROF,
                          heightplot = self.HEIGHT + self.HEIGHTPROF,
                          show=show)
        
        nrow, ncol = self.getSubplots()
        
        counter = 0
        for y in range(nrow):
            for x in range(ncol):
                
                if counter >= self.nplots:
                    break
                
                self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)
                
                if showprofile:
                    self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan+colspan, 1, 1)
                    
                counter += 1
    
    def run(self, dataOut, id, wintitle="", channelList=None, showprofile=False,
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            save=False, figpath='', figfile=None, show=True, ftp=False, wr_period=1,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0, realtime=False):
        
        """
        
        Input:
            dataOut         :
            id        :
            wintitle        :
            channelList     :
            showProfile     :
            xmin            :    None,
            xmax            :    None,
            ymin            :    None,
            ymax            :    None,
            zmin            :    None,
            zmax            :    None
        """
        
        if dataOut.flagNoData:
            return None
        
        if realtime:
            if not(isRealtime(utcdatatime = dataOut.utctime)):
                print 'Skipping this plot function'
                return
        
        if channelList == None:
            channelIndexList = dataOut.channelIndexList
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError, "Channel %d is not in dataOut.channelList"
                channelIndexList.append(dataOut.channelList.index(channel))
                
        factor = dataOut.normFactor
        lenfactor = factor.shape[1]
        x = dataOut.getLagTRange(1)
        y = dataOut.getHeiRange()
        
        z = copy.copy(dataOut.data_corr[:,:,0,:])
        for i in range(dataOut.data_corr.shape[0]):
            z[i,:,:] = z[i,:,:]/factor[i,:]    
        zdB = numpy.abs(z)
        
        avg = numpy.average(z, axis=1)
#         avg = numpy.nanmean(z, axis=1)
#         noise = dataOut.noise/factor
  
        #thisDatetime = dataOut.datatime
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
        title = wintitle + " Correlation" 
        xlabel = "Lag T (s)"
        ylabel = "Range (Km)"
        
        if not self.isConfig:
            
            nplots = dataOut.data_corr.shape[0]  
            
            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = 0
            if zmax == None: zmax = 1
            
            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos
            
            self.isConfig = True
        
        self.setWinTitle(title)
            
        for i in range(self.nplots):
            str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))
            title = "Channel %d and %d: : %s" %(dataOut.pairsList[i][0]+1,dataOut.pairsList[i][1]+1 , str_datetime)
            axes = self.axesList[i*self.__nsubplots]
            axes.pcolor(x, y, zdB[i,:,:],
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, cblabel='')
            
#             if self.__showprofile:
#                 axes = self.axesList[i*self.__nsubplots +1]
#                 axes.pline(avgdB[i], y,
#                         xmin=zmin, xmax=zmax, ymin=ymin, ymax=ymax,
#                         xlabel='dB', ylabel='', title='',
#                         ytick_visible=False,
#                         grid='x')
#                 
#                 noiseline = numpy.repeat(noisedB[i], len(y))
#                 axes.addpline(noiseline, y, idline=1, color="black", linestyle="dashed", lw=2)
            
        self.draw()
        
        if figfile == None:
            str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
            figfile = self.getFilename(name = str_datetime)
        
        if figpath != '':
            self.counter_imagwr += 1
            if (self.counter_imagwr>=wr_period):
                # store png plot to local folder
                self.saveFigure(figpath, figfile)
                # store png plot to FTP server according to RT-Web format 
                name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
                ftp_filename = os.path.join(figpath, name)
                self.saveFigure(figpath, ftp_filename)                
                self.counter_imagwr = 0         
