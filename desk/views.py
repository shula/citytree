from datetime import datetime

from django.contrib.auth.models import User
#from django import forms
from django import newforms as forms
from django.newforms import ModelForm
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list as generic_object_list
from django.views.generic.create_update import create_object  as generic_create_object
from django.views.generic.create_update import update_object  as generic_update_object
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.template import RequestContext 
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
 
MAIN_SECTION       = 1
HELP_SECTION       = 2

NO_BLOG_POSTS_MESSAGE = 1 #message to display when there are no posts in the blog
BLOG_POST_DELETED     = 2

NEW_POST_CREATED_SUCCESSFULLY = 3
NEW_POST_CREATED_SUCCESSFULLY_CONTINUE_EDITING = 4


NUM_POSTS_PER_PAGE    = 30
NUM_IMAGES_IN_POST    = 12 #Number of pictures that can be attached to a post

#get login/logout to work with correct urls
login_needed = user_passes_test(lambda u: not u.is_anonymous(), login_url='/desk/login/')

from citytree.cityblog.models import blog, post, flag, postImage

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

class PostForm(ModelForm):
    class Meta:
        model = post

def fix_boolean_fields(data, fields):
    # in newforms, there are two options for a BooleanField:
    #  as a multiple choice - in that case we fix BooleanField not handling '0' as False
    #  as a checkbox - if it is False it just doesn't appear - we fix that too.
    for field in fields:
        if not data.has_key(field) or data[field] == '0':
            data[field] = False

def create_edit_blog_post( request, post_id=None, blog_slug=None ):
  """
  Creates a new post for the specified blog
  """
  userId     = request.user.id
  user_blogs = blog.objects.filter( authors=userId)
  thePost    = None
  postImages = None
  theBlog    = None
  message    = None
  form       = None # not sure why I can't initialize it once somewhere.
  nullImages = range(0, NUM_IMAGES_IN_POST)
  
  #------------ Edit --------------
  if post_id:
    try:
        thePost = post.objects.get(id=post_id)
    except post.DoesNotExist:
        raise Http404()
    
    theBlog    = thePost.blog
    imageObj   = thePost.image
    postImages = thePost.postimage_set.all().order_by( 'index' )
    nullImages = range(len(postImages), NUM_IMAGES_IN_POST)
    
    #check that user has the right to edit this post
    if( thePost.author.id != userId ):
      raise Http404()
    
    form = PostForm(instance=thePost)

    #return generic_update_object( request, model=post, 
                #post_save_redirect=theBlog.get_edit_absolute_url(),
                #template_name='desk/create_post.html',
                #object_id=post_id,
                #extra_context={'blog_id':theBlog.id} )
  
   #------------ Create New --------------        
  else:
    #Check if this user has the rights to post to this blog
    try:
      theBlog = blog.objects.all().filter(slug=blog_slug)[0]
      theUser = theBlog.authors.filter(id=userId)[0]
    except Exception, e:
      raise Http404
      
    form = PostForm()
  
  #--------------------- Now Render response ------------
  if request.method == 'POST':
        new_data = request.POST.copy()
        fix_boolean_fields(new_data, ['draft', 'enable_comments'])
        
        def isSet( theHash, theKey ):
            return (theHash.has_key( theKey ) and len( theHash[theKey] ) > 0 )
        
        if not isSet(new_data, 'post_date'):
            new_data['post_date'] = datetime.now()

        #for k,v in new_data.iteritems():
        #    print "--------"
        #    print "[%s] [%s]" % (k,v)
        
        new_data['author'] = str(userId)
        new_data['blog']   = str(theBlog.id)
    
        if not post_id:
            # once again, we have a problem with ImageWithThumbnail, so the fix is:
            # make sure the post has an id first, then add image.
            thePost = post()
            thePost.blog = theBlog
            thePost.author = theUser
            thePost.post_date = datetime.now()
            thePost.save()
            post_id = thePost.id
            
        form = PostForm(new_data, files=request.FILES, instance=thePost)
        new_data.update(request.FILES)

        if form.is_valid():
            newPost = form.save()
            post_id = newPost.id
            
            if post_id:
                # XXX: save images (not really required?)
                #if request.FILES.has_key('image'):
                #    newPost.save_image_file(newPost.image, request.FILES['image']['content'])
                
                #-------------- Append Images ----------------
                handleImageUploads( newPost, new_data )
              
            # Do a post-after-redirect so that reload works, etc.
            if( new_data.has_key('create_new_item_after_edit')):
                return HttpResponseRedirect("/desk/blogs/%s/createPost/?new=2" % (newPost.blog.slug))
            else:
                return HttpResponseRedirect("/desk/editPost/%d/?new=1" % (newPost.id))
        else: # form is not valid
            errors = form.errors
        #manipulator.do_html2python(new_data)
        
  else:
        if( request.GET.has_key('new') ):
            if( int(request.GET['new']) == 1):
                message = NEW_POST_CREATED_SUCCESSFULLY
            else:
                message = NEW_POST_CREATED_SUCCESSFULLY_CONTINUE_EDITING
        errors = {}
        # This makes sure the form accurate represents the fields of the place.
        #new_data = manipulator.flatten_data()

  #------- Filter Flags ------------
  legalFlags = flag.objects.filter( Q(blog__isnull=True) | Q(blog=theBlog.id) )
  renderFlags = []
  postFlags = {}  #Flags that this post currently contains
  
  def stam( id ): postFlags[id] = True
  
  if( thePost != None ):
       [ stam(f.id) for f in thePost.flags.all() ]
  
  
  class FlagProxy( object ):
      def __init__(self, id, name, sel ): 
        self.id = id
        self.name = name
        self.selected = sel
        
  for f in legalFlags:
     a = FlagProxy( f.id, f.name, postFlags.has_key(f.id) )
     renderFlags.append(a)
     
  #-------------- Render Response ------------
  return render_to_response('desk/create_edit_post.html', 
                {'form'       : form, 
                 'post'       : thePost,
                 'postImages' : postImages,
                 'nullImages' : nullImages, #blank places to add extra images to a blog post
                 'blog'       : theBlog,
                 'user_blogs' : user_blogs,
                 'message'    : message,
                 'blogFlags'  : renderFlags,
                 'section'    : MAIN_SECTION ,
                 }, 
                context_instance=RequestContext(request))
  
    #return generic_create_object( request, model=post, 
                #post_save_redirect=theBlog.get_edit_absolute_url(),
                #template_name='desk/create_post.html',
                #extra_context={'blog_id':theBlog.id} )
                
create_edit_blog_post = login_needed(create_edit_blog_post)
