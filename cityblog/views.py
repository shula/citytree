from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list as generic_object_list
from django.views.generic.list_detail import object_detail as generic_object_detail
from cityblog.models import blog, post, flag, subject
from frontpage.models import FrontPage
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext 
from datetime import datetime, date
from citytree.utils.hebCalView import *

NUM_POSTS_PER_PAGE = 5
NUM_SUBJECTS_PER_PAGE = 10

def show_blog( request, blog_slug ):
  #fd=open('/tmp/alon1','w')
  #fd.write('boo')
  #fd.close()
  #return HttpResponse('working?')
  b = get_object_or_404(blog, slug=blog_slug)
  posts = b.post_set.filter(draft=0)
  
  #------------ Get List of flags in blog ---------
  flags = flag.objects.filter( post__blog = b.id ).filter( blog__post__draft = 0 ).distinct()
  
  #------------ If a specific flag was requested, then show only that flag -------
  if( request.method == 'GET' and request.GET.has_key('flag') ):
      flagId = int(request.GET['flag'])
      posts = posts.filter( flags__id =  flagId )
  
  #------------ Create Objects for Hebrew Calender ----
  calLinkType     = FRONTPAGE_URL_TYPE
  calLinkTemplate = CALENDAR_URL_TYPE_REGISTRY[calLinkType]
  
  dateToShow = date.today()
  bgColorProcessor = makeHebBGColorProcessor( dateToShow )
  dayLinks = makeHebCalLinks( '/?date=%s', date.today() )
  calender = makeHebCalRequestContext(dayLinks, engDate=date.today(), urlType=calLinkType, highlightToday=True)
  
  
  return generic_object_list( request, queryset=posts,
              template_object_name='post',
              template_name='cityblog/blog_posts.html',
              allow_empty=True, 
              extra_context={'blog' : b, 'flags' : flags },
              context_processors =[calender,bgColorProcessor],
              paginate_by=NUM_POSTS_PER_PAGE)
   
   
def subject_view( request, subject_slug ):
    theSubject = get_object_or_404(subject, slug=subject_slug)
    flags = theSubject.flags.all()
    
    cat_ids = [ cat.id for cat in flags ]
    
    thePosts = post.objects.filter( draft=0, flags__in = cat_ids )
    
    frontpage = FrontPage.objects.filter(draft=False).latest()
    
    return generic_object_list( request, queryset=thePosts,
                  template_object_name='post',
                  template_name='cityblog/subject_view.html',
                  allow_empty=True, 
                  extra_context={ 'theSubject' : theSubject,
                                  'frontpage' : frontpage },
                  context_processors =[],
                  paginate_by=NUM_SUBJECTS_PER_PAGE)
   
def display_post( request, post_id, preview = False ):
    
  if( not preview ):
      p    = get_object_or_404(post, id=post_id, draft=0)
  else:
      p    = get_object_or_404(post, id=post_id, author=request.user.id )
      
  blog    = p.blog
  pImages = p.postimage_set.all().order_by( 'index' )            
  
  #-------------- Get Correct Template ----------------
  if( p.post_style == 2 ):
      template_name = "post_long.html"
  elif( p.post_style == 3 ):
      template_name = "post_gallery.html"
  else:
      template_name = "post_short.html"
      
  #------------ Get List of flags in blog ---------
  flags = flag.objects.filter( post__blog = blog.id ).filter( post__draft = 0 ).distinct()
      
  #------------ Create Objects for Hebrew Calender ----
  calLinkType     = FRONTPAGE_URL_TYPE
  calLinkTemplate = CALENDAR_URL_TYPE_REGISTRY[calLinkType]
  
  #dateToShow = date.today()
  #bgColorProcessor = makeHebBGColorProcessor( dateToShow )
  #dayLinks = makeHebCalLinks( calLinkTemplate, date.today() )
  #calendar = makeHebCalRequestContext(dayLinks, engDate=date.today(), urlType=calLinkType, highlightToday=True)

  #-------------- Extra Info ----------------
  
  return generic_object_detail(
    request,
    object_id =  post_id,
    queryset  = post.objects.all(),
    template_name = 'cityblog/%s'%template_name,
    #context_processors =[calendar,bgColorProcessor],
    extra_context = { 'blog' : blog, 'flags' : flags, 'galleryImages': pImages },
    template_object_name = 'post'
  )
  
  return render_to_response('cityblog/%s'%template_name, {'post': p, 'blog' : b})
  
  
def send_feedback( request ):
    from django.core.mail import send_mail, BadHeaderError
    
    if( request.method != 'POST'):
            return HttpResponseRedirect('/')
    
    redirect_url = request.POST.get('redirect_to', '')
    subject      = request.POST.get('subject', '')
    message      = request.POST.get('message', '')
    sender_name  = request.POST.get('sender_name', '')
    from_email   = request.POST.get('from_email', '')
    
    if redirect_url and subject and message and from_email and sender_name:
        try:
            msg = "User Who Sent the email %s \n\n %s" % (sender_name, message  )
            
            send_mail(subject, msg, from_email, ['tree@citytree.net'])
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponseRedirect(redirect_url)
    else:
        return HttpResponse('Make sure all fields are entered and valid.')

