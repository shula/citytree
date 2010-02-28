
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^update$', 'mailinglist.views.join'),
    (r'^join$' , 'mailinglist.views.join'),
#    (r'^confirm/(?P<confirm_code>.*)$','citytree.mailinglist.views.confirm'),
   
    (r'^thankyou$' , 'mailinglist.views.joindone'),
    
    (r'^remove$' , 'mailinglist.views.unjoin'),
  
    (r'^removeok$' , 'mailinglist.views.unjoinok'),
   
    (r'^joinerror$ ', 'mailinglist.views.joinerror'),
)

