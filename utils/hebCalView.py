from colorConverter  import *
from hebDate         import *
from django.conf     import settings
from django.template import Context, loader
from datetime        import date

calendarSaturation  = 35.0   #these two are for the calendar
calendarBrightness  = 100.0

curDaySaturation    = calendarSaturation + 28.0
curDayBrightness    = calendarBrightness - 10.0

mainSaturation      = 6.0   #these two are for the rest of the page
mainBrightness      = 96.0

#------------------- URL Patterns for calendar ------------------
FRONTPAGE_URL_TYPE = 1

CALENDAR_URL_TYPE_REGISTRY =  {
    FRONTPAGE_URL_TYPE : '?date=%s'
}

#---------- class definition for Days --------------
class Day( object ):
    def __init__( self, dayNum=None, dayColor=None, linkUrl=None ):
        
        self.valid      = False
        self.linkValid  = False
        self.hasBGColor = False
        self.dayNum     = None
        self.color      = None
        
        #---------- Init Values -----------
        if( dayNum != None ):
            self.valid     = True
            self.dayNum    = dayNum
            
            if( dayColor != None ):
                self.color     = dayColor
                self.hasBGColor = True
            
            if( linkUrl != None ):
                self.linkValid = True
                self.linkUrl   = linkUrl
                
    def isValid( self ):
        return self.valid
        
    def getHasBGColor( self ):
        return self.hasBGColor
        
    def hasLink( self ):
        return self.linkValid
        
    def getUrl( self ):
        return self.linkUrl
        
    def getNum( self ):
        return self.dayNum
        
    def bgColor( self ):
        return self.color

#---------- Useful Functions --------------
def makeHebCalRequestContext( urls, engDate, urlType, highlightToday ):
    """
    Wrapper for hebcalview.
    """
    return lambda request: hebCal( request, urls, engDate, urlType, highlightToday=highlightToday )

def makeHebBGColorProcessor( engDate ):
  percent    = getHebFractionalDayOfYear( engDate )
  saturation = globals()['mainSaturation']
  brightness = globals()['mainBrightness']
  
  (h,s,v) = interpolateHSV( saturation, brightness, percent )
  (r,g,b) = hsvToRgb(h,s,v)
  color   = rgbToWebColor(r,g,b)
  
  return lambda request: { 'site_bg_color' : color }
  
def hebCal( request, urls, engDate=None, urlType=None, 
                                hebDay=None, hebMonth=None, hebYear = None,
                                highlightToday = False):
    
    h           = HebDate()
    
    hebDateToday = HebDate()
    today = date.today()
    hebDateToday.setEngDate( today.day, today.month, today.year )
    todayJulian = hebDateToday.getJulianDay()
    
    #--------------- Get Date ----------------
    if( engDate != None ):
        h.setEngDate( engDate.day, engDate.month, engDate.year )
    else:
        assert( hebMonth != None and hebYear != None )
        h.setHebDate( hebDay, hebMonth, hebYear )
    
    media_url = settings.MEDIA_URL

    total = 0
    startOfMonthDayOfYear = h.getMonthStartDayOfHebYear()
    totalDaysInYear       = h.getNumDaysInHebYear()
    hebDayOfMonth         = h.getHebDayOfMonth()
    hebMonth              = h.getHebMonth()
    hebYear               = h.getHebYear()
    hebDaysInMonth        = h.getDaysInHebMonth()
    outDays               = []
    
    #output empty cells at start of week
    for i in range(0, h.getMonthStartDayOfWeek()-1 ):
        outDays.append(Day())
        total += 1
    
    h.setHebDate(1, hebMonth, hebYear) #draw from start of month
    julianDay = h.getJulianDay()
    
    daysToDraw = todayJulian-julianDay+1
    if( daysToDraw > hebDaysInMonth ): 
        daysToDraw = hebDaysInMonth
    
    #Display all days in month up to today
    for i in range(0,daysToDraw) :
        percent = (startOfMonthDayOfYear+i)/(totalDaysInYear*1.0)
        
        theSaturation =  calendarSaturation
        theBrightness = calendarBrightness
        
        if( i+1 == hebDayOfMonth and highlightToday ):
            theSaturation = curDaySaturation
            theBrightness = curDayBrightness
        
        (hC,s,v) = interpolateHSV( theSaturation, theBrightness, percent )
        (r,g,b) = hsvToRgb(hC,s,v)
        
        theDay     = i+1
        theLink    = urls[i]
        theColor   = rgbToWebColor(r,g,b)
        outDays.append(Day( theDay, theColor, theLink ))
        
        total+=1

    #Insert remaining days in month without background
    for i in range(daysToDraw, hebDaysInMonth):
        outDays.append( Day(dayNum=i+1) )
        total += 1
    
    while( total < 7*6 ):
        outDays.append(Day())
        total += 1
   
    moonImageUrl = "%s/calendar/cityMoons/%d.gif"%(media_url, hebDayOfMonth)
    
    #---------------------- Handle Next Month & Previous Year ------------------
    nextMonthDate = h.getNextMonth()
    prevMonthDate = h.getPrevMonth()
    
    hasPrevMonth = True
    prevMonth    = prevMonthDate.getHebMonth()
    prevYear     = prevMonthDate.getHebYear()
    
    hasNextMonth = True
    nextMonth    = nextMonthDate.getHebMonth()
    nextYear     = nextMonthDate.getHebYear()
    
    if( hebDateToday.getHebMonth() == hebMonth and 
        hebDateToday.getHebYear() == hebYear ):
        hasNextMonth = False
    
    # TODO: tail patch to get site working again.
    if (len(outDays) > 31):
        outDays = outDays[:31]
    
    #---------------------- Render ------------------
    t = loader.get_template('calendar.html')
    c = Context({'days': outDays, 
                 'hebMonth'    : int(hebMonth),
                 'moonImageUrl': moonImageUrl,
                 'hasNextMonth': hasNextMonth,
                 'nextMonth'   : nextMonth,
                 'nextYear'    : nextYear,
                 'hasPrevMonth': hasPrevMonth,
                 'prevMonth'   : prevMonth,
                 'prevYear'    : prevYear,
                 'urlType'     : urlType,
                 'media_url'   : media_url
                 })
        
                 
    calendarText = t.render(c)
    return {'calendar' : calendarText }