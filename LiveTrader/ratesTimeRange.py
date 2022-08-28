import datetime
import math
import pytz
import numpy as np

def ratesTimeRange(endTime, intervalMinutes, lookbackPeriod):
    #Function to retrieve available start/finish date 
    #That is, handle weekends so bars returned = lookbackPeriod

    mktCloseDays = [5, 6]

    #First handle if requesting over weekend.
    #Set end date to Saturday midnight (12am Sat)
    if endTime.weekday() in mktCloseDays:
        while endTime.weekday() != 4:
            endTime = endTime - datetime.timedelta(days = 1)
        endTime = datetime.datetime(year = endTime.year, month = endTime.month, day = endTime.day+1, tzinfo = endTime.tzinfo)    

    #Set up range
    minsBack = intervalMinutes * lookbackPeriod
    startTime = endTime - datetime.timedelta(minutes = minsBack)

    #Handle weekends between this period
    #Disregarding pull periods longer than 1wk - unlikely.
    if startTime.weekday() in mktCloseDays:        
        dayShift = 7 - startTime.weekday() 
        startTime = startTime - datetime.timedelta(days = dayShift)

    return startTime, endTime