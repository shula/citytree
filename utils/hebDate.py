from hdate import *

class HebDate( object ):
  
    def __init__( self ):
        self.hebDate = Hdate()
        
        self.hebDayOfMonth         = None
        self.hebMonth              = None
        self.hebYear               = None
        self.julianDay             = None
        self.monthStartDayOfWeek   = None
        self.totalNumDaysInYear    = None
        self.startOfMonthDayOfYear = None
        self.daysInHebMonth        = None
        
        self.init()

    def setEngDate( self, day, month, year ):
        self.hebDate.set_gdate( day, month, year )
        self.init()
        
    def setHebDate( self, day, month, year ):
        self.hebDate.set_hdate( day, month, year )
        self.init()
        
    def setJulian( self, julianDay ) :
        self.hebDate.set_jd( julianDay )
        self.init()
        
    def init( self ):
        #get day of month
        self.hebDayOfMonth   = int(self.hebDate.get_hday())
        self.hebMonth        = int(self.hebDate.get_hmonth())
        self.hebYear         = int(self.hebDate.get_hyear())
        self.julianDay       = int(self.hebDate.get_julian())

        #get day of week month starts on
        tmp = Hdate()
        tmp.set_hdate( 1, self.hebMonth, self.hebYear)
        
        firstDayOfMonthJulian      = tmp.get_julian()
        
        self.monthStartDayOfWeek   =  tmp.get_day_of_the_week()

        self.totalNumDaysInYear    = tmp.get_size_of_year()

        #the day that the month started at
        self.startOfMonthDayOfYear = tmp.get_days()
        
        #Get the number of days in this hebrew month
        nextMonth = self.hebMonth+1
        year      = self.hebYear
        if( self.hebMonth == 12 ):
            nextMonth = 1
            year      += 1
            
        tmp.set_hdate( 1, nextMonth, year )
        firstDayOfNextMonthJulian  = tmp.get_julian()
        
        self.daysInHebMonth = firstDayOfNextMonthJulian-firstDayOfMonthJulian
        
        
    def getEngDate( self ):
        from datetime import date
        engYear  = self.hebDate.get_gyear()
        engMonth = self.hebDate.get_gmonth()
        engDay   = self.hebDate.get_gday()
        
        return date( engYear, engMonth, engDay )
        
    def getHebDayOfMonth( self ):
         return self.hebDayOfMonth
     
    def getHebMonth( self ):
         return self.hebMonth
     
    def getHebYear( self ):
         return self.hebYear
     
    def getNumDaysInHebYear( self ):
         return self.totalNumDaysInYear
     
    def getMonthStartDayOfHebYear( self ):
         return self.startOfMonthDayOfYear
     
    def getMonthStartDayOfWeek( self ):
         return self.monthStartDayOfWeek
         
    def getJulianDay( self ):
        return self.julianDay
        
    def getDaysInHebMonth( self ):
        return self.daysInHebMonth
        
    def getNextMonth( self ):
        ret = HebDate()
        ret.setHebDate( self.daysInHebMonth, self.hebMonth, self.hebYear )
        julian = ret.getJulianDay() + 1
        ret.setJulian( julian)
        return ret
        
    def getPrevMonth( self ):
        ret = HebDate()
        ret.setHebDate( 1, self.hebMonth, self.hebYear )
        julian = ret.getJulianDay() - 1
        ret.setJulian( julian)
        return ret
         
#-------------------------- Utility Functions -----------------------

def date2hebdate(date):
    hebdate = HebDate()
    hebdate.setEngDate(date.day, date.month, date.year)
    return hebdate

def makeHebCalLinks( urlPattern, engDate=None, hebMonth=None, hebYear=None ):
    h        = HebDate()
    
    if( engDate ):
        h.setEngDate( engDate.day, engDate.month, engDate.year )
        truncate_at_day = h.hebDayOfMonth
    else:
        h.setHebDate( 1, hebMonth, hebYear )
        truncate_at_day = False
    
    retLinks = {}
    
    curYear     = h.getHebYear()
    curMonth    = h.getHebMonth()
    daysInMonth = h.getDaysInHebMonth()
    if truncate_at_day:
        daysInMonth = min(daysInMonth, truncate_at_day)
    
    for i in range(1,daysInMonth+1) :
        hebDateObj = HebDate()
        hebDateObj.setHebDate( i, curMonth, curYear )
        
        theEngDate = hebDateObj.getEngDate()
        retLinks[i - 1] = urlPattern % theEngDate.strftime("%d-%m-%Y")

    return retLinks
    
def getHebFractionalDayOfYear( theDate ):
    h        = HebDate()
    h.setEngDate( theDate.day, theDate.month, theDate.year )
    
    today = h.getMonthStartDayOfHebYear()+h.getHebDayOfMonth()-1
    total = h.getNumDaysInHebYear()
    
    ret =  today/(1.0*total)
    
    return ret
        
