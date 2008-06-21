from datetime import datetime, date
import itertools

from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list as generic_object_list
from django.views.generic.list_detail import object_detail as generic_object_detail
from cityblog.models import blog, post, flag, subject
from frontpage.models import FrontPage
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from citytree.utils.hebCalView import *

NUM_POSTS_PER_PAGE = 5
NUM_SUBJECTS_PER_PAGE = 10

def show_blog_or_workshop( request, blog_slug ):
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

    if b.is_workshop():
        for p in posts:
            p.make_sure_workshop_exists()
    #------------- Takes care of workshops --------
        no_events = posts.filter(workshop__workshopevent=None)
        now = datetime.now()
        start_of_today = datetime(now.year, now.month, now.day)
        _have_events = posts.filter(
                workshop__workshopevent__workshopeventpart__start_time__gte=start_of_today
                ).order_by('workshop__workshopevent__workshopeventpart__start_time')
        temp_set = set()
        have_events = []
        for p in _have_events:
            if p not in temp_set:
                have_events.append(p)
                temp_set.add(p)
        #posts = itertools.chain(have_events, no_events)
        posts = have_events
        # don't show no_events for now
        return render_to_response('cityblog/blog_workshops.html', {
            'post_list': posts,
            'blog': b, 'flags': flags
            }, context_instance = RequestContext(request, {}, [calender, bgColorProcessor])
            )
    else:
    #------------ Standard blog with normal, non workshop, posts --------
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
  
  #return render_to_response('cityblog/%s'%template_name, {'post': p, 'blog' : b})
  
  
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

################# Comments #####################
# mostly comments are just using django.contrib.comments
# but since I want some extra features, these are implemented here
#, and the urls are redirected here by the right urlpatters
# the extra features are:
#  * email blog owner on comment (caution: will generate spam)


def cityblog_post_free_comment(request):
    """
    implementation rant:
    using an implementation detail of post_free_comment - that it returns a redirect object
    when the comment has actually been posted.
    """
    if not request.POST:
        raise Http404, _("Only POSTs are allowed")
    try:
        options, target, security_hash = request.POST['options'], request.POST['target'], request.POST['gonzo']
    except KeyError:
        raise Http404, _("One or more of the required fields wasn't submitted")
    if Comment.objects.get_security_hash(options, '', '', target) != security_hash:
        raise Http404, _("Somebody tampered with the comment form (security violation)")
    content_type_id, object_id = target.split(':') # target is something like '52:5157'
    content_type = ContentType.objects.get(pk=content_type_id)
    try:
        obj = content_type.get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
        raise Http404, _("The comment form had an invalid 'target' parameter -- the object ID was invalid")
    option_list = options.split(',')
    new_data = request.POST.copy()
    new_data['content_type_id'] = content_type_id
    new_data['object_id'] = object_id
    new_data['ip_address'] = request.META['REMOTE_ADDR']
    new_data['is_public'] = IS_PUBLIC in option_list
    manipulator = PublicFreeCommentManipulator()
    errors = manipulator.get_validation_errors(new_data)
    if errors or request.POST.has_key('preview'):
        comment = errors and '' or manipulator.get_comment(new_data)
        return render_to_response('comments/free_preview.html', {
            'comment': comment,
            'comment_form': forms.FormWrapper(manipulator, new_data, errors),
            'options': options,
            'target': target,
            'hash': security_hash,
        }, context_instance=RequestContext(request))
    elif request.POST.has_key('post'):
        # If the IP is banned, mail the admins, do NOT save the comment, and
        # serve up the "Thanks for posting" page as if the comment WAS posted.
        if request.META['REMOTE_ADDR'] in settings.BANNED_IPS:
            from django.core.mail import mail_admins
            mail_admins("Practical joker", str(request.POST) + "\n\n" + str(request.META))
        else:
            manipulator.do_html2python(new_data)
            comment = manipulator.save(new_data)
        return HttpResponseRedirect("../posted/?c=%s:%s" % (content_type_id, object_id))
    else:
        raise Http404, _("The comment form didn't provide either 'preview' or 'post'")


