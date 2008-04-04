#--------------------------- Overrides ---------------------

# add the following line at the end of settings.py:
#from settings_amber import *

#
# Overriding stuff for local testing - remove when copying
# back into citytree.net
import os
try:
    if open('/etc/hostname').read().strip() == 'amber.saymoo.org':
	DATABASE_HOST = ''
	DATABASE_USER = 'root'
	DATABASE_PASSWORD = 'sarduakar'
	BASE_DIR = '/home/alon/src/citytree/citytree'
	MEDIA_ROOT = BASE_DIR + '/siteMedia'
	MEDIA_URL = 'http://localhost:8001/siteMedia/'
	ADMIN_MEDIA_PREFIX = 'http://localhost:8001/admin_media/'
        TEMPLATE_DIRS = (
            BASE_DIR + '/templates'
        )
        HEADER_MASK = BASE_DIR + '/frontpage/mask.png' #mask for main page header logo
        DEBUG = True 
        TEMPLATE_DEBUG = DEBUG
except:
    pass

