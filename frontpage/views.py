from datetime import datetime, date, timedelta

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext 
from django.contrib.auth.decorators import user_passes_test

from citytree.cityblog.models  import Blog, Subject
from citytree.utils.hebCalView import *
from frontpage.models import FrontPage
from workshop.models import WorkshopEvent
import workshop.util as workshop_util

admin_only = user_passes_test(lambda u: (not u.is_anonymous() and u.is_staff), login_url='/')

def show_front_page( request, front_page = None ):
  
  if front_page is None:
    try:
      pageObj = FrontPage.objects.filter(draft=False).latest()
    except FrontPage.DoesNotExist:
      raise Http404
  else:
    pageObj = front_page
  
  from citytree.utils.hebDate import makeHebCalLinks
  
  dateToShow = date.today()
  
  #------------ Find the page object that corresponds to the date in the get string if one exists ----
  if( request.method == 'GET' and request.GET.has_key('date') ):
    try:
          from time import strptime
          
          dateStr = request.GET['date']
          [year, month, day] = strptime(dateStr, "%d-%m-%Y")[0:3]
          testDate = date( year, month, day )
          
          testDate1 = testDate + timedelta(1) #next day
          
          pageObj = FrontPage.objects.filter( date__lte=testDate1, draft=False ).latest()
          dateToShow = testDate
    except Exception, e: #In case of invalid GET string - don't do anything
        #DEBUG
        print "Exception retrieving object, reverting to today, %r"%e
        pass
  
  #------------ Create Objects for Hebrew Calender ----
  calLinkType     = FRONTPAGE_URL_TYPE
  calLinkTemplate = CALENDAR_URL_TYPE_REGISTRY[calLinkType]
  
  bgColorProcessor = makeHebBGColorProcessor( dateToShow )
  dayLinks = makeHebCalLinks( calLinkTemplate, engDate=dateToShow )
  workshopLinks = workshop_util.makeHebCalLinks(dateToShow)
  dayLinks.update(workshopLinks)
  calender = makeHebCalRequestContext(dayLinks, engDate=dateToShow, 
                            urlType=calLinkType, highlightToday=True)

  displayed_blogs = Blog.objects.filter(display_in_menu=True)

  return render_to_response('frontpage/frontpage.html', 
    {'content':pageObj, 'blogs': Blog.objects.all(),
     'subjects' : Subject.objects.all(),
     'events': WorkshopEvent.future_events(),
     'displayed_blogs': displayed_blogs
    },
    context_instance=RequestContext(request, {}, [calender,bgColorProcessor]))
    

def preview_front_page(request, page_id):
    """
    Preview frontpage - for administator only
    """
    pageObj = get_object_or_404(FrontPage, id=page_id)
    dateToShow = date.today()
    
    #------------ Create Objects for Hebrew Calender ----
    calLinkType     = FRONTPAGE_URL_TYPE
    calLinkTemplate = CALENDAR_URL_TYPE_REGISTRY[calLinkType]
  
    bgColorProcessor = makeHebBGColorProcessor( dateToShow )
    dayLinks = makeHebCalLinks( calLinkTemplate, engDate=date.today() )
    calender = makeHebCalRequestContext(dayLinks, engDate=date.today(),
                                           urlType=calLinkType, highlightToday=True  )
    
    return render_to_response('frontpage/frontpage.html', 
    {'content':pageObj, 'blogs': Blog.objects.all(), 'subjects' : Subject.objects.all()},
    context_instance=RequestContext(request, {}, [calender,bgColorProcessor]))
    
preview_front_page = admin_only(preview_front_page) 
    
