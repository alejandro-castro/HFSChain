""" 
The TIME_CONVERSIONS.py module gathers classes and functions for time system transformations
(e.g. between seconds from 1970 to datetime format).   

MODULES CALLED:
NUMPY, TIME, DATETIME, CALENDAR
        
MODIFICATION HISTORY:
Created by Ing. Freddy Galindo (frederickgalindo@gmail.com). ROJ Aug 13, 2009.
"""

import numpy as np
import time as tm
import datetime as dt
import calendar as cr

class Time:
    """
    time(year,month,dom,hour,min,secs)

    An object represents a date and time of certain event..

    Parameters
    ----------
    YEAR =  Number of the desired year. Year  must be valid values  from the civil calendar.
    Years B.C.E must be represented as negative integers. Years in the common era are repre-
    sented as  positive integers. In particular,  note that there is no year 0  in the civil
    calendar. 1 B.C.E. (-1) is followed by 1 C.E. (1).

    MONTH = Number of desired month (1=Jan, ..., 12=December).

    DOM = Number of day of the month.

    HOUR = Number of the hour of the day. By default hour=0

    MINS = Number of the minute of the hour. By default min=0

    SECS = Number of the second of the minute. By default secs=0.
        
    Examples
    --------
    time_info = time(2008,9,30,12,30,00)

    time_info = time(2008,9,30)
    """
    
    def __init__(self,year=None,month=None,dom=None,hour=0,mins=0,secs=0):
        # If one the first three inputs are not defined, it takes the current date.
        date = tm.localtime()
        if year==None:year=date[0]
        if month==None:month=date[1]
        if dom==None:dom=date[2]
        
        # Converting to arrays
        year = np.array([year]); month = np.array([month]); dom = np.array([dom])
        hour = np.array([hour]); mins = np.array([mins]); secs = np.array([secs])
        
        # Defining time information object.
        self.year = np.atleast_1d(year)
        self.month = np.atleast_1d(month)
        self.dom = np.atleast_1d(dom)
        self.hour = np.atleast_1d(hour)
        self.mins = np.atleast_1d(mins)
        self.secs = np.atleast_1d(secs)
        
    def change2julday(self):
        """
        Converts a datetime to Julian days.
        """
        
        # Defining constants
        greg = 2299171 # incorrect Julian day for Oct, 25, 1582.
        min_calendar = -4716
        max_calendar = 5000000
        
        min_year = np.nanmin(self.year)
        max_year = np.nanmax(self.year)
        if (min_year<min_calendar) or (max_year>max_calendar):
            print "Value of Julian date is out of allowed range"
            return -1

        noyear = np.sum(self.year==0)
        if noyear>0:
            print "There is no year zero in the civil calendar"
            return -1

        # Knowing if the year is less than 0.
        bc = self.year<0        
        
        # Knowing if the month is less than March.      
        inJanFeb = self.month<=2
        
        jy = self.year + bc - inJanFeb
        jm = self.month + (1 + 12*inJanFeb)
        
        # Computing Julian days.
        jul= np.floor(365.25*jy) + np.floor(30.6001*jm) + (self.dom+1720995.0)
        
        # Test whether to change to Gregorian Calendar
        if np.min(jul) >= greg:
            ja = np.int32(0.01*jy)
            jul = jul + 2 - ja + np.int32(0.25*ja)
        else:
            gregchange = np.where(jul >= greg)
            if gregchange[0].size>0:        
                ja = np.int32(0.01 + jy[gregchange])
                jy[grechange] = jy[gregchange] + 2 - ja + np.int32(0.25*ja)

        # Determining machine-specific parameters affecting floating-point.
        eps = 0.0 # Replace this line for a function to get precision.
        eps = abs(jul)*0.0 > eps
        
        jul = jul + (self.hour/24. -0.5) + (self.mins/1440.) + (self.secs/86400.) + eps 
        
        return jul[0]
    
    def change2secs(self):         
        """
        Converts datetime to number of seconds respect to 1970.
        """
        
        year = self.year
        if year.size>1: year = year[0]
            
        month = self.month
        if month.size>1: month = month[0]
        
        dom = self.dom
        if dom.size>1: dom = dom[0]
        
        # Resizing hour, mins and secs if it was necessary.
        hour = self.hour
        if hour.size>1:hour = hour[0]
        if hour.size==1:hour = np.resize(hour,year.size)
        
        mins = self.mins
        if mins.size>1:mins = mins[0]
        if mins.size==1:mins = np.resize(mins,year.size)
    
        secs = self.secs
        if secs.size>1:secs = secs[0]
        if secs.size==1:secs = np.resize(secs,year.size)

        # Using time.mktime to compute seconds respect to 1970.
        secs1970 = np.zeros(year.size)
        for ii in np.arange(year.size):
            secs1970[ii] = tm.mktime((int(year[ii]),int(month[ii]),int(dom[ii]),\
                int(hour[ii]),int(mins[ii]),int(secs[ii]),0,0,0))

        secs1970 = np.int32(secs1970 - tm.timezone)
        
        return secs1970
        
    def change2strdate(self,mode=1):
        """
        change2strdate  method converts a date and time of certain event to date string. The
        string format is like localtime (e.g. Fri Oct  9 15:00:19 2009).
        
        Parameters
        ----------
        None.
        
        Return
        ------
            
        Modification History
        --------------------
        Created by Freddy R. Galindo, ROJ, 09 October 2009.
        
        """
        
        secs = np.atleast_1d(self.change2secs())
        strdate = []
        for ii in np.arange(np.size(secs)):         
            secs_tmp = tm.localtime(secs[ii] + tm.timezone)
            if mode==1:
                strdate.append(tm.strftime("%d-%b-%Y (%j) %H:%M:%S",secs_tmp))
            elif mode==2:            
                strdate.append(tm.strftime("%d-%b-%Y (%j)",secs_tmp))
                
        strdate = np.array(strdate)

        return strdate


class Secs:
    """
    secs(secs):
    
    An object represents the number of seconds respect to 1970.
    
    Parameters
    ----------
    
    SECS = A scalar or array giving the number of seconds respect to 1970.
    
    Example:
    --------
    secs_info = secs(1251241373)
    
    secs_info = secs([1251241373,1251241383,1251241393])    
    """
    def __init__(self,secs):    
        self.secs = secs
        
    def change2julday(self):
        """
        Convert seconds from 1970 to Julian days.
        """
            
        secs_1970 = time(1970,1,1,0,0,0).change2julday()
        
        julian = self.secs/86400.0 + secs_1970
        
        return julian
    
    def change2time(self):        
        """
        Converts seconds from 1970 to datetime.
        """
        
        secs1970 = np.atleast_1d(self.secs)
        
        datetime = np.zeros((9,secs1970.size))
        for ii in np.arange(secs1970.size):
            tuple = tm.gmtime(secs1970[ii])
            datetime[0,ii] = tuple[0]
            datetime[1,ii] = tuple[1]
            datetime[2,ii] = tuple[2]
            datetime[3,ii] = tuple[3]
            datetime[4,ii] = tuple[4]
            datetime[5,ii] = tuple[5]
            datetime[6,ii] = tuple[6]
            datetime[7,ii] = tuple[7]
            datetime[8,ii] = tuple[8]

        datetime = np.int32(datetime)

        return datetime
            

class Julian:    
    """
    julian(julian):
    
    An object represents julian days.
    
    Parameters
    ----------
    
    JULIAN = A scalar or array giving the julina days.
    
    Example:
    --------
    julian_info = julian(2454740)
    
    julian_info = julian([2454740,2454760,2454780])
    """
    def __init__(self,julian):
        self.julian = np.atleast_1d(julian)
        
    def change2time(self):    
        """
        change2time method converts from julian day to calendar date and time.
        
        Return
        ------
        year = An array giving the year of the desired julian day.
        month = An array giving the month of the desired julian day. 
        dom = An array giving the day of the desired julian day.
        hour = An array giving the hour of the desired julian day.
        mins = An array giving the minute of the desired julian day.
        secs = An array giving the second of the desired julian day.
        
        Examples
        --------
        >> jd = 2455119.0 
        >> [yy,mo,dd,hh,mi,ss] = TimeTools.julian(jd).change2time()
        >> print [yy,mo,dd,hh,mi,ss]
        [2009] [10] [ 14.] [ 12.] [ 0.] [ 0.]
        
        Modification history
        --------------------             
        Translated from "Numerical Recipies in C", by William H. Press, Brian P. Flannery,
        Saul A. Teukolsky, and William T. Vetterling. Cambridge University Press, 1988.
        Converted to Python by Freddy R. Galindo, ROJ, 06 October 2009.
        """

        min_julian = -1095      
        max_julian = 1827933925
        if (np.min(self.julian) < min_julian) or (np.max(self.julian) > max_julian):
            print 'Value of Julian date is out of allowed range.'
            return None

        # Beginning of Gregorian calendar
        igreg = 2299161
        julLong = np.floor(self.julian + 0.5) 
        minJul = np.min(julLong)
        
        if (minJul >= igreg):
            # All are Gregorian
            jalpha = np.int32(((julLong - 1867216) - 0.25)/36524.25)
            ja = julLong + 1 + jalpha - np.int32(0.25*jalpha)
        else:            
            ja = julLong
            gregChange = np.where(julLong >= igreg)
            if gregChange[0].size>0:
                jalpha = np.int32(((julLong[gregChange]-1867216) - 0.25)/36524.25)
                ja[gregChange] = julLong[gregChange]+1+jalpha-np.int32(0.25*jalpha)

        # clear memory.
        jalpha = -1
        
        jb = ja + 1524
        jc = np.int32(6680. + ((jb-2439870)-122.1)/365.25)
        jd = np.int32(365.*jc + (0.25*jc))
        je = np.int32((jb - jd)/30.6001)
        
        dom = jb - jd - np.int32(30.6001*je)
        month = je - 1
        month = ((month - 1) % 12) + 1
        month = np.atleast_1d(month)
        year = jc - 4715
        year = year - (month > 2)*1
        year = year - (year <= 0)*1
        year = np.atleast_1d(year)
        
        # Getting hours, minutes, seconds
        fraction = self.julian + 0.5 - julLong
        eps_0 = dom*0.0 + 1.0e-12
        eps_1 = 1.0e-12*np.abs(julLong)
        eps = (eps_0>eps_1)*eps_0 + (eps_0<=eps_1)*eps_1
        
        hour_0 = dom*0 + 23
        hour_2 = dom*0 + 0
        hour_1 = np.floor(fraction*24.0 + eps)
        hour = ((hour_1>hour_0)*23) + ((hour_1<=hour_0)*hour_1)
        hour = ((hour_1<hour_2)*0)  + ((hour_1>=hour_2)*hour_1)
        
        fraction = fraction - (hour/24.0)
        mins_0 = dom*0 + 59
        mins_2 = dom*0 + 0
        mins_1 = np.floor(fraction*1440.0 + eps)
        mins = ((mins_1>mins_0)*59) + ((mins_1<=mins_0)*mins_1)
        mins = ((mins_1<mins_2)*0)  + ((mins_1>=mins_2)*mins_1)
        
        secs_2 = dom*0 + 0
        secs_1 = (fraction - mins/1440.0)*86400.0
        secs = ((secs_1<secs_2)*0)  + ((secs_1>=secs_2)*secs_1)
    
        return year, month,dom, hour, mins, secs
        
    def change2secs(self):
        """
        Converts from Julian days to seconds from 1970. 
        """
        
        jul_1970 = Time(1970,1,1,0,0,0).change2julday()
        
        secs = np.int32((self.julian - jul_1970)*86400)
        
        return secs
    
    def change2lst(self,longitude=-76.8667):
        """
        CT2LST converts  from local civil time to local mean sideral time       
        
        longitude = The longitude in degrees (east of Greenwich) of the  place for which
        the local sideral time is desired, scalar. The Greenwich mean sideral time (GMST)
        can be found by setting longitude=0.
        """

        # Useful constants, see Meus, p. 84
        c = np.array([280.46061837, 360.98564736629, 0.000387933, 38710000.0])
        jd2000 = 2451545.0
        t0 = self.julian - jd2000
        t = t0/36525.
        
        # Computing GST in seconds
        theta = c[0] + (c[1]*t0) + (t**2)*(c[2]-t/c[3])
        
        # Computing LST in hours
        lst = (theta + longitude)/15.0
        neg = np.where(lst < 0.0)
        if neg[0].size>0:lst[neg] = 24.0 + (lst[neg] % 24)
        lst = lst % 24.0
    
        return lst


class date2doy:
    def __init__(self,year,month,day):
        self.year = year
        self.month = month
        self.day = day
    
    def change2doy(self):
        if cr.isleap(self.year) == True:
            tfactor = 1
        else:
            tfactor = 2

        day = self.day
        month = self.month               
        
        doy = np.floor((275*month)/9.0) - (tfactor*np.floor((month+9)/12.0)) + day - 30
        
        return np.int32(doy)


class Doy2Date:
    def __init__(self,year,doy):
        self.year = year
        self.doy = doy
        
    def change2date(self):
        months = np.arange(12) + 1
    
        first_dem = date2doy(self.year,months,1)
        first_dem = first_dem.change2doy()      
        
        imm = np.where((self.doy - first_dem) > 0)
        
        month = imm[0].size
        dom = self.doy -first_dem[month - 1] + 1

        return month, dom
