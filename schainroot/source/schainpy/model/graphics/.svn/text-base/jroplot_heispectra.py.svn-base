'''

@author: Daniel Suarez
'''

import os
import datetime
import numpy

from figure import Figure, isRealtime

class SpectraHeisScope(Figure):
    
    
    isConfig = None
    __nsubplots = None
    
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'spc'
    
    def __init__(self):
        
        self.isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 230
        self.HEIGHT = 250
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0
        
    def getSubplots(self):
        
        ncol = int(numpy.sqrt(self.nplots)+0.9)
        nrow = int(self.nplots*1./ncol + 0.9)
        
        return nrow, ncol
    
    def setup(self, id, nplots, wintitle, show):
        
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
                          show = show)
        
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

    
    def run(self, dataOut, id, wintitle="", channelList=None,
            xmin=None, xmax=None, ymin=None, ymax=None, save=False,
            figpath='', figfile=None, ftp=False, wr_period=1, show=True,
            server=None, folder=None, username=None, password=None):
        
        """
        
        Input:
            dataOut         :
            id        :
            wintitle        :
            channelList     :
            xmin            :    None,
            xmax            :    None,
            ymin            :    None,
            ymax            :    None,
        """
        
        if dataOut.realtime:
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
        
#        x = dataOut.heightList
        c   =  3E8 
        deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]
        #deberia cambiar para el caso de 1Mhz y 100KHz
        x = numpy.arange(-1*dataOut.nHeights/2.,dataOut.nHeights/2.)*(c/(2*deltaHeight*dataOut.nHeights*1000))
        #para 1Mhz descomentar la siguiente linea
        #x= x/(10000.0)
#        y = dataOut.data[channelIndexList,:] * numpy.conjugate(dataOut.data[channelIndexList,:])
#        y = y.real
        factor = dataOut.normFactor
        data = dataOut.data_spc / factor
        datadB = 10.*numpy.log10(data)
        y = datadB
        
        #thisDatetime = dataOut.datatime
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
        title = wintitle + " Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = ""
        #para 1Mhz descomentar la siguiente linea
        #xlabel = "Frequency x 10000"
        ylabel = "Intensity (dB)"
        
        if not self.isConfig:
            nplots = len(channelIndexList)
            
            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       show=show)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
                
            self.isConfig = True
        
        self.setWinTitle(title)
        
        for i in range(len(self.axesList)):
            ychannel = y[i,:]
            str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))
            title = "Channel %d: %4.2fdB: %s" %(i, numpy.max(ychannel), str_datetime)
            axes = self.axesList[i]
            axes.pline(x, ychannel,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title, grid='both')
        
        
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
                #name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
                #ftp_filename = os.path.join(figpath, name)
                #self.saveFigure(figpath, ftp_filename)                
                self.counter_imagwr = 0

class RTIfromSpectraHeis(Figure):
    
    isConfig = None
    __nsubplots = None

    PREFIX = 'rtinoise'
    
    def __init__(self):
        
        self.timerange = 24*60*60
        self.isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 820
        self.HEIGHT = 200
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0
        self.xdata = None
        self.ydata = None
        self.figfile = None
        
    def getSubplots(self):
        
        ncol = 1
        nrow = 1
        
        return nrow, ncol
    
    def setup(self, id, nplots, wintitle, showprofile=True, show=True):
               
        self.__showprofile = showprofile
        self.nplots = nplots
        
        ncolspan = 7
        colspan = 6
        self.__nsubplots = 2
        
        self.createFigure(id = id,
                          wintitle = wintitle,
                          widthplot = self.WIDTH+self.WIDTHPROF,
                          heightplot = self.HEIGHT+self.HEIGHTPROF,
                          show = show)
        
        nrow, ncol = self.getSubplots()
        
        self.addAxes(nrow, ncol*ncolspan, 0, 0, colspan, 1)
        
                        
    def run(self, dataOut, id, wintitle="", channelList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None,
            timerange=None,
            save=False, figpath='', figfile=None, ftp=False, wr_period=1, show=True,
            server=None, folder=None, username=None, password=None):
        
        if channelList == None:
            channelIndexList = dataOut.channelIndexList
            channelList = dataOut.channelList
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError, "Channel %d is not in dataOut.channelList"
                channelIndexList.append(dataOut.channelList.index(channel))
        
        if timerange != None:
            self.timerange = timerange
        
        tmin = None
        tmax = None
        x = dataOut.getTimeRange()
        y = dataOut.getHeiRange()
        
        factor = dataOut.normFactor
        data = dataOut.data_spc / factor
        data = numpy.average(data,axis=1)
        datadB = 10*numpy.log10(data)
        
#        factor = dataOut.normFactor
#        noise = dataOut.getNoise()/factor
#        noisedB = 10*numpy.log10(noise)
        
        #thisDatetime = dataOut.datatime
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
        title = wintitle + " RTI: %s" %(thisDatetime.strftime("%d-%b-%Y"))
        xlabel = "Local Time"
        ylabel = "Intensity (dB)"
        
        if not self.isConfig:
            
            nplots = 1
            
            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)
            
            tmin, tmax = self.getTimeLim(x, xmin, xmax)
            if ymin == None: ymin = numpy.nanmin(datadB)
            if ymax == None: ymax = numpy.nanmax(datadB)
            
            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.isConfig = True
            self.figfile = figfile
            self.xdata = numpy.array([])
            self.ydata = numpy.array([])
        
        self.setWinTitle(title)
            
        
#        title = "RTI %s" %(thisDatetime.strftime("%d-%b-%Y"))
        title = "RTI - %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        
        legendlabels = ["channel %d"%idchannel for idchannel in channelList]
        axes = self.axesList[0]
        
        self.xdata = numpy.hstack((self.xdata, x[0:1]))
        
        if len(self.ydata)==0:
            self.ydata = datadB[channelIndexList].reshape(-1,1)
        else:
            self.ydata = numpy.hstack((self.ydata, datadB[channelIndexList].reshape(-1,1)))
        
        
        axes.pmultilineyaxis(x=self.xdata, y=self.ydata,
                    xmin=tmin, xmax=tmax, ymin=ymin, ymax=ymax,
                    xlabel=xlabel, ylabel=ylabel, title=title, legendlabels=legendlabels, marker='.', markersize=8, linestyle="solid", grid='both',
                    XAxisAsTime=True
                    )
            
        self.draw()
        
        if x[1] >= self.axesList[0].xmax:
            self.counter_imagwr = wr_period
            del self.xdata
            del self.ydata
            self.__isConfig = False
        
        if self.figfile == None:
            str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.figfile = self.getFilename(name = str_datetime)
        
        if figpath != '':
            self.counter_imagwr += 1
            if (self.counter_imagwr>=wr_period):
                # store png plot to local folder
                self.saveFigure(figpath, self.figfile)
                # store png plot to FTP server according to RT-Web format 
                #name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
                #ftp_filename = os.path.join(figpath, name)
                #self.saveFigure(figpath, ftp_filename)                
                self.counter_imagwr = 0
