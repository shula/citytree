# -*- coding: utf-8 -*-

from datetime import datetime
from time import strptime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django import newforms as forms
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list as generic_object_list
from django.views.generic.create_update import create_object  as generic_create_object
from django.views.generic.create_update import update_object  as generic_update_object
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext 
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
 
from desk.forms import PostForm, WorkshopForm, WorkshopEventForm
from cityblog.models import blog, post, flag, postImage
from workshop.models import Workshop, WorkshopEvent, WorkshopEventPart

MAIN_SECTION       = 1
HELP_SECTION       = 2

NO_BLOG_POSTS_MESSAGE = 1 #message to display when there are no posts in the blog
BLOG_POST_DELETED     = 2

NEW_POST_CREATED_SUCCESSFULLY = 3
NEW_POST_CREATED_SUCCESSFULLY_CONTINUE_EDITING = 4


NUM_POSTS_PER_PAGE    = 30
NUM_IMAGES_IN_POST    = 12 #Number of pictures that can be attached to a post

#get login/logout to work with correct urls. require at least one blog (thus removing
# regular users without adding yet another field)
login_needed = user_passes_test(lambda u: not u.is_anonymous() and u.blog_set.count()>0, login_url='/desk/login/')

def tree_trunk( request ):
    """ The main tree trunk page """
  
    user_blogs = blog.objects.filter( authors=request.user.id)
  
    return render_to_response('desk/tree_trunk.html', {
                'section' : MAIN_SECTION , 
                'user_blogs': user_blogs, 
                'username': request.user.first_name,
                'APP_NAME' : 'cityblog' }, context_instance=RequestContext(request) )
tree_trunk = login_needed(tree_trunk)

def help_view( request ):
    """
    Desk help
    """
   
    user_blogs = blog.objects.filter( authors=request.user.id)
   
    return render_to_response('desk/help.html', 
                                {'APP_NAME' : 'cityblog',
                                'user_blogs': user_blogs,
                                'section' : HELP_SECTION }, 
                                context_instance=RequestContext(request) )
help_view = login_needed(help_view)

def blogdetail( request, blog_slug ):
    """
    List the posts in a blog

    If it is a workshop blog, the list is slightly different, and the button allows
    creating of new workshop, not new post.
    """
    user_blogs = blog.objects.filter( authors=request.user.id)
    theBlog   = get_object_or_404( blog, slug=blog_slug )
    blogPosts = theBlog.post_set.filter(author=request.user.id) #make sure user can only see their own posts
    theMessage   = None
  
    if( not blogPosts ):
        theMessage = NO_BLOG_POSTS_MESSAGE
    elif( request.method == 'GET' and request.GET.has_key('del') ):
        theMessage = BLOG_POST_DELETED
  
    return generic_object_list( request, queryset=blogPosts, 
        template_name='desk/display_list_of_blog_posts.html', allow_empty=True, 
        extra_context={'blog':theBlog, 
                     'user_blogs': user_blogs,
                     'message' : theMessage,
                     'section' : MAIN_SECTION ,
                     },
    paginate_by=NUM_POSTS_PER_PAGE)

blogdetail = login_needed(blogdetail)
  

def delete_blog_post( request, post_id ):
    """
    Delete requisit post
    """
    thePost = get_object_or_404( post, id=post_id, author=request.user.id )
    
    thePost.delete()
    
    referer = request.META.get('HTTP_REFERER', '/desk/')
    
    #remove get string if any exists (all characters after and including the trailing '?'
    referer = referer[0:referer.rfind('?')]
    referer += '?del=1'
    
    return HttpResponseRedirect( referer )
    
def handleImageUploads( postObject, new_data ):

    from django.utils.datastructures import MultiValueDict
    #get index of all images currently attached to this post
    imgLookup = {}
    for img in postObject.postimage_set.all():
        imgLookup[img.index] = img.id
    
    imgWasDeleted=False
    
    for idx in xrange( 0, NUM_IMAGES_IN_POST ):
        imgKey    = 'gallery_image%d'%idx
        fileKey   = 'gallery_image_file%d'%idx
        labelKey  = 'gallery_image_label%d'%idx
        tsrTxtKey = 'gallery_teaser_text%d'%idx
        idxKey    = 'gallery_image_indx%d'%idx
        delKey    = 'gallery_image_delete%d'%idx
        
        dataToSave = MultiValueDict()
        
        #--------- Check if we're deleting an image --------------
        if( imgLookup.has_key(idx) and new_data.has_key(delKey)):
            postImg = get_object_or_404( postImage, id=new_data[delKey] )
            postImg.delete()
            imgWasDeleted = True
            continue

            
        #--------- Create Manipulators --------------
        # Due to moving to development django (post 0.96.6) ImageWithThumbnail is broken. The fix
        # is to create the instance (postImage in this case) first, then populate the images fields in it.
        if not imgLookup.has_key(idx) and new_data.has_key(fileKey):
            new_postImage = postImage()
            new_postImage.index = idx
            new_postImage.post = postObject
            new_postImage.save()
            imgLookup[new_postImage.index] = new_postImage.id
        if imgLookup.has_key(idx):
            manipulator = postImage.ChangeManipulator(imgLookup[idx])
            
        if( new_data.has_key(fileKey) ):
            dataToSave.setlist('image_file',new_data.getlist(fileKey) )
            
        #--------- Load Data --------------
        if( new_data.has_key(fileKey) or imgLookup.has_key(idx)):
            dataToSave['image']   = new_data[imgKey]
            dataToSave['index']   = new_data[idxKey]
            dataToSave['label']   = new_data[labelKey]
            dataToSave['caption'] = new_data[tsrTxtKey]
            dataToSave['post']    = postObject.id
            
            errors = manipulator.get_validation_errors(dataToSave)
            manipulator.do_html2python(dataToSave)
            if not errors:
                manipulator.save(dataToSave)
                
    #------ Hack To Maintain Image order ------------
    #if( imgWasDeleted ):
    for new_idx, (idx, img) in enumerate(sorted([(img.index, img) for img in postObject.postimage_set.all()])):
        img.index = new_idx
        img.save()


def fix_boolean_fields(data, fields):
    # in newforms, there are two options for a BooleanField:
    #  as a multiple choice - in that case we fix BooleanField not handling '0' as False
    #  as a checkbox - if it is False it just doesn't appear - we fix that too.
    for field in fields:
        if not data.has_key(field) or data[field] == '0':
            data[field] = False

def create_edit_blog_post( request, post_id=None, blog_slug=None ):
    if post_id is None:
        theBlog = get_object_or_404(blog, slug=blog_slug)
    else:
        theBlog = get_object_or_404(post, id=post_id).blog
    if theBlog.is_workshop():
        clazz = WorkshopCreator
    else:
        clazz = PostCreator
    return clazz(request, post_id, blog_slug).response()
create_edit_blog_post = login_needed(create_edit_blog_post)

class Responder(object):

    _template = '' # override by inheritance

    def __init__(s, request):
        s._request = request
        s._form = None
        s._initial = {}
        s._response = None # if set then it is returned instead of calling _render
        s._render_dict = {}
        s._instance = None
        s._get_instance() # if this is an edit, will override _instance

    def response(s):
        if s._instance is not None: # editing existing object
            if s._request.method != 'POST':
                s._form = s._form_class(instance = s._instance)
            s._edit_existing()
        else:
            s._create_new()
            s._form = s._form_class(initial=s._initial)
      
        #--------------------- Now Render response ------------
        if s._request.method == 'POST':
            s.new_data = s._request.POST.copy()
            s._handle_post()
            s._form = s._form_class(s.new_data, files=s._request.FILES, instance=s._instance)
            s.new_data.update(s._request.FILES)
            if s._form.is_valid():
                if s._instance is None:
                    s._post_new()
                    s._form.instance = s._instance
                s._instance = s._form.save()
                s._on_valid_form()
            else: # form is not valid
                s.errors = s._form.errors
 
        else: # GET, presumably (definitely no POST)
            s._handle_get()
        if s._response is not None:
            return s._response
        return s._render()
    
    def _post_new(s):
        pass

    def _on_valid_form(s):
        pass

    def _edit_existing(s):
        pass

    def _create_new(self):
        pass

    def _handle_get(self):
        pass

    def _handle_post(self):
        pass

    def _makeRenderDictionary(s):
        pass

    def _get_instance(s):
        pass # Must not fail on missing object - just set _instance to None

    def _render(s):
        s._render_dict.update({
            'instance': s._instance,
            'form': s._form,
            })
        s._makeRenderDictionary()
        #-------------- Render Response ------------
        return render_to_response(s._template, s._render_dict,
                    context_instance=RequestContext(s._request))


class PostCreator(Responder):

    _template='desk/create_edit_post.html'
    _form_class = PostForm

    def __init__(s, request, post_id=None, blog_slug=None):
        s.post_id    = post_id
        s.blog_slug  = blog_slug

        s.userId     = request.user.id
        s.user_blogs = blog.objects.filter( authors=s.userId )
        s.thePost    = None
        s.postImages = None
        s.theBlog    = None
        s.message    = None
        s.nullImages = range(0, NUM_IMAGES_IN_POST)

        Responder.__init__(s, request)
 
    def _get_instance(s):
        objs = post.objects.filter(id=s.post_id)
        if objs.count() > 0:
            s._instance = objs[0]

    def _edit_existing(s):
        """ post_id is set. Fill in variables from existing post
        """
        thePost = s.thePost = s._instance
        s.theBlog    = thePost.blog
        s.imageObj   = thePost.image
        s.postImages = thePost.postimage_set.all().order_by( 'index' )
        s.nullImages = range(len(s.postImages), NUM_IMAGES_IN_POST)
    
        #check that user has the right to edit this post
        if( thePost.author.id != s.userId ):
            raise Http404()

    def _create_new(s):
        """ post_id is Null. Create an empty form, default variable values.
        """
        #Check if this user has the rights to post to this blog
        try:
            s.theBlog = blog.objects.all().filter(slug=s.blog_slug)[0]
            s.theUser = s.theBlog.authors.filter(id=s.userId)[0]
        except Exception, e:
            raise Http404

    def _handle_get(s):
        if( s._request.GET.has_key('new') ):
            if( int(s._request.GET['new']) == 1):
                s.message = NEW_POST_CREATED_SUCCESSFULLY
            else:
                s.message = NEW_POST_CREATED_SUCCESSFULLY_CONTINUE_EDITING
        s.errors = {}

    def _handle_post(s):
        fix_boolean_fields(s.new_data, ['draft', 'enable_comments'])
        
        def isSet( theHash, theKey ):
            return (theHash.has_key( theKey ) and len( theHash[theKey] ) > 0 )
        
        if not isSet(s.new_data, 'post_date'):
            s.new_data['post_date'] = datetime.now()

        s.new_data['author'] = str(s.userId)
        s.new_data['blog']   = str(s.theBlog.id)

    def _on_valid_form(s):
        s.newPost = s._instance
        s.post_id = s.newPost.id
        
        # XXX: save images (not really required?)
        #if request.FILES.has_key('image'):
        #    newPost.save_image_file(newPost.image, request.FILES['image']['content'])
        
        #-------------- Append Images ----------------
        handleImageUploads( s.newPost, s.new_data )
          
        # Do a post-after-redirect so that reload works, etc.
        if( s.new_data.has_key('create_new_item_after_edit')):
            s._response = HttpResponseRedirect("/desk/blogs/%s/createPost/?new=2" % (s.newPost.blog.slug))
        else:
            s._response = HttpResponseRedirect("/desk/editPost/%d/?new=1" % (s.newPost.id))

    def _post_new(s):
        """ POST - post_id is None
        """
        # once again, we have a problem with ImageWithThumbnail, so the fix is:
        # make sure the post has an id first, then add image.
        s.thePost = thePost = post()
        thePost.blog = s.theBlog
        thePost.author = s.theUser
        thePost.post_date = datetime.now()
        thePost.save()
        s.post_id = thePost.id
        s._instance = s.thePost
 
    def _makeRenderDictionary(s):
         s._render_dict.update(
                {'post'       : s.thePost,
                 'postImages' : s.postImages,
                 'nullImages' : s.nullImages, #blank places to add extra images to a blog post
                 'blog'       : s.theBlog,
                 'user_blogs' : s.user_blogs,
                 'message'    : s.message,
                 'blogFlags'  : s._makeFilterFlags(),
                 'section'    : MAIN_SECTION ,
                 })

    def _makeFilterFlags(s):
        #------- Filter Flags ------------
        legalFlags = flag.objects.filter( Q(blog__isnull=True) | Q(blog=s.theBlog.id) )
        renderFlags = []
        postFlags = {}  #Flags that this post currently contains
      
        def stam( id ): postFlags[id] = True
      
        if( s.thePost != None ):
           [ stam(f.id) for f in s.thePost.flags.all() ]
      
        class FlagProxy( object ):
            def __init__(self, id, name, sel ): 
                self.id = id
                self.name = name
                self.selected = sel
            
        for f in legalFlags:
            a = FlagProxy( f.id, f.name, postFlags.has_key(f.id) )
            renderFlags.append(a)

        return renderFlags

# TODO: nice way to merge the post and its workshop to one form, *automagically*.
# i.e. like edit_inline

class WorkshopCreator(PostCreator):
    
    _template = 'desk/create_edit_workshop.html'
    _form_class = WorkshopForm

    def __init__(s, request, post_id=None, blog_slug=None):
        PostCreator.__init__(s, request, post_id, blog_slug)
        s.workshop = None

    def _edit_existing(s):
        super(WorkshopCreator, s)._edit_existing()
        # now read stuff from the instance into the workshop fields
        if s._form:
            s._form.fill_other_fields_from_instance()
        s.workshop = s.thePost.workshop
        s.workshop.owners.add(s._request.user)
        # if the teaser text exists in the post, then it is an existing
        # post being moved over.
        # copy it to the description.
        defpost = s.workshop.defining_post
        if len(defpost.teaser_text) > 0 and len(defpost.text) == 0:
            defpost.description = defpost.teaser_text
            defpost.save()
            # update form to reflect this (should be done automagically somehow?)
            #todo

    def _on_valid_form(s):
        super(PostCreator, s)._on_valid_form()
        if not s._instance.is_workshop():
            s._instance.post_style = s._instance.POST_STYLE_WORKSHOP
            s._instance.save()

    def _makeRenderDictionary(s):
        super(WorkshopCreator, s)._makeRenderDictionary()
        s._render_dict.update({
            'workshop':s.workshop,
            'site':Site.objects.get_current().name
            })

#------------ WorkshopEvent editor ----------------------

def create_edit_workshop_event( request, workshop_slug=None, we_id=None):
    return WorkshopEventCreator(request, workshop_slug, we_id).response()
create_edit_workshop_event = login_needed(create_edit_workshop_event)

class WorkshopEventCreator(Responder):
    _template = 'desk/create_edit_workshop_event.html'
    _form_class = WorkshopEventForm

    def _get_instance(self):
        # don't really need workshop_slug if we_id is filled, do I?
        if self.we_id is not None:
            self._instance = get_object_or_404(WorkshopEvent, id=self.we_id)
            self.workshop_slug = self._instance.workshop.slug
            self.workshop = self._instance.workshop

    def _create_new(self):
        # TODO: check that user has permissions (easy to do here, but must make sure its actually
        # set at the right point.

        # take initial values from another event of the same workshop first
        base_event = None
        if self.workshop.workshopevent_set.count() > 0:
            events = self.workshop.workshopevent_set.order_by('-workshopeventpart__start_time')
            if len(events) > 0:
                base_event = events[0]
        if base_event is None:
            # last, take initial values from the default workshop event
            default_workshop = Workshop.get_default_workshop()
            base_event = default_workshop.workshopevent_set.get()
        self._initial.update(base_event.get_new_event_dict())

    def _makeRenderDictionary(self):
        self._render_dict.update({
            'workshop':self.workshop,
            'event': self._instance
            })

    def _post_new(self):
        # must set self._instance on exit
        we = WorkshopEvent()
        we.workshop = self.workshop
        self._instance = we

    def __init__(self, request, workshop_slug, we_id):
        self.workshop_slug = workshop_slug
        self.we_id = we_id
        if workshop_slug is not None:
            self.workshop = get_object_or_404(Workshop, slug=workshop_slug)
        super(WorkshopEventCreator, self).__init__(request)

    def _on_valid_form(s):
        def strptime_datetime(s, format):
            st = strptime(s, format)
            return datetime(year=st.tm_year, month=st.tm_mon, day=st.tm_mday, hour=st.tm_hour, minute=st.tm_min, second=st.tm_sec)

        for part_id_key in [k for k in s.new_data.keys() if k.startswith('part_id')]:
            part_id = s.new_data[part_id_key]
            form_part_num = part_id_key.rsplit('_',1)[1]
            if len(WorkshopEventPart.objects.filter(id=part_id)) == 0:
                # create new
                part = WorkshopEventPart()
                part.workshop_event = self._instance
            else:
                # edit existing
                part = WorkshopEventPart.objects.get(id=part_id)
            get = lambda x: s.new_data['part_%s_%s' % (x, form_part_num)]
            start_date = get('start_date')
            start_time = get('start_time')
            end_time   = get('end_time')
            # python 2.4 - datetime has no strptime function
            part.start_time = strptime_datetime('%s %s' % (start_date, start_time), '%Y-%m-%d %H:%M:%S')
            part.end_time = strptime_datetime('%s %s' % (start_date, end_time), '%Y-%m-%d %H:%M:%S')
            part.save()

def delete_workshop_event(request, we_id):
    we = get_object_or_404(WorkshopEvent, id=we_id)
    redir = we.workshop.get_absolute_edit_url()
    we.delete()
    return HttpResponseRedirect( redir )

delete_workshop_event = login_needed(delete_workshop_event)

