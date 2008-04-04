# Django settings for citytreesite project.

DEBUG = False 
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Tami', 'tami@citytree.net'),
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'tami_citytree_django'             # Or path to database file if using sqlite3.
DATABASE_USER = 'tami'             # Not used with sqlite3.
DATABASE_PASSWORD = 'DZey9TQt'         # Not used with sqlite3.
DATABASE_HOST = 'mysql.citytree.dreamhosters.com'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/tamizori/citytree.net/siteMedia/'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = 'http://www.citytree.net/siteMedia/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://www.citytree.net/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'oag2x*xysf_-@$-w^as@tv4+7dg2#xb5!ru4h6$d__v!luqy#o'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'citytree.urls'

TEMPLATE_DIRS = (
    '/home/tamizori/django/django_projects/citytree/templates'
)

TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.auth','citytree.context_processors.media_url', 'citytree.context_processors.citytree_context')

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.comments',
    'citytree.comment_utils',
    'citytree.cityblog',
    'citytree.desk',
    'citytree.frontpage',
    'citytree.nesh.thumbnail',
    'citytree.ajax',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
)

#-------------------------- Site Settings ------------------
HEADER_MASK = '/home/tamizori/django/django_projects/citytree/frontpage/mask.png' #mask for main page header logo
SITE_LOGO   = '' #site logo

#--------------------------- Overrides ---------------------
# Overriding stuff for local testing - remove when copying
# back into citytree.net

import os
try:
    hostname = open('/etc/hostname'),read().strip()
    if hostname == 'eeepc-alon':
        DATABASE_HOST = ''
        DATABASE_USER = 'root'             # Not used with sqlite3.
        DATABASE_PASSWORD = 'tioxul'         # Not used with sqlite3.
        BASE_DIR = '/home/user/src/citytree/citytree'
        MEDIA_ROOT = BASE_DIR + '/siteMedia'
        MEDIA_URL = 'http://localhost:8001/siteMedia'
        ADMIN_MEDIA_PREFIX = 'http://localhost:8001/admin_media/'
        TEMPLATE_DIRS = (
            BASE_DIR + '/templates'
        )
        HEADER_MASK = BASE_DIR + '/frontpage/mask.png' #mask for main page header logo
        DEBUG = True 
        TEMPLATE_DEBUG = DEBUG
    elif hostname == 'amber.saymoo.org':
        DATABASE_HOST = ''
        DATABASE_USER = 'root'
        DATABASE_PASSWORD = 'sarduakar'
        BASE_DIR = '/home/alon/src/citytree/citytree'
        MEDIA_ROOT = BASE_DIR + '/siteMedia'
        MEDIA_URL = 'http://localhost:8001/siteMedia'
        ADMIN_MEDIA_PREFIX = 'http://localhost:8001/admin_media/'
    elif hostname == 'lini':
        DATABASE_HOST = ''
        DATABASE_USER = 'root'
        DATABASE_PASSWORD = 'yy*8383'
        BASE_DIR = '/home/tami/citytree_code/citytree'
        MEDIA_ROOT = BASE_DIR + '/siteMedia'
        MEDIA_URL = 'http://lini:81/siteMedia/'
        ADMIN_MEDIA_PREFIX = 'http://lini:81/admin_media/'
        TEMPLATE_DIRS = (
            BASE_DIR + '/templates'
        )
        HEADER_MASK = BASE_DIR + '/frontpage/mask.png' #mask for main page header logo
        DEBUG = True
        TEMPLATE_DEBUG = DEBUG
except:
    pass

