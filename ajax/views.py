from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse
from citytree.utils.hebCalView import *
from datetime import date
from django.template import Context, loader
from citytree.utils.hebDate import HebDate

def calendar( request ):
    
    #---------- Get parameters from post --------------
    try:
        month       = int(request.GET['month'])
        year        = int(request.GET['year'])
        day         = 1
        calLinkType = int(request.GET['urlType'])
        
        #----------- Check if we're displaying this month ------------
        h = HebDate()
        
        if( month == h.getHebMonth() and year == h.getHebYear() ):
            thisMonth = True
            day       = h.getHebDayOfMonth()
        else :
            thisMonth = False
        
        calLinkTemplate = CALENDAR_URL_TYPE_REGISTRY[calLinkType] 
        links           = makeHebCalLinks( calLinkTemplate, hebMonth=month, hebYear=year )
        response        = hebCal( request, links, urlType=calLinkType,
                                  hebDay=day, hebMonth=month, hebYear=year, highlightToday=thisMonth );
    except Exception, e:
      raise Http404
    
    #import time
    #time.sleep(2.0) #artificially display ajax progress inidicator
      
    #---------------- Handle Calendar Functionality ------
    return HttpResponse( response['calendar'], mimetype='text/html; charset=utf-8')
