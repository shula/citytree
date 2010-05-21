# -*- coding: utf-8 -*-

# Django settings for citytreesite project.

DEFAULT_CHARSET = 'utf-8'

ADMINS = (
    ('Tami', 'tami@citytree.dreamhosters.com'),
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

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

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'oag2x*xysf_-@$-w^as@tv4+7dg2#xb5!ru4h6$d__v!luqy#o'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
#    'staticgenerator.middleware.StaticGeneratorMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
# TODO: django is killing my cache, says anon means having to put auth first. well it is! wtf?!
#    'django.middleware.cache.CacheMiddleware',
]

try:
    import debug_toolbar
    use_debug_toolbar = True
except:
    print "no debug toolbar"
    use_debug_toolbar = False


ROOT_URLCONF = 'citytree.urls'

TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.auth','citytree.context_processors.media_url', 'citytree.context_processors.citytree_context')

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.comments',
    'django.contrib.markup',
    'django.contrib.redirects',
    'citytree.accounts',
    'citytree.forum',
    'citytree.comment_utils',
    'citytree.cityblog',
    'citytree.desk',
    'citytree.frontpage',
    'citytree.ajax',
    'citytree.spamdetector',
    'citytree.workshop',
    'citytree.mailinglist',
    'citytree.citycomments',
    # contrib apps
    'citytree.nesh.thumbnail',
    'citytree.citymail',
    # back to django (XXX: move upward? does it matter?)
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
]

try:
    import django_evolution
    INSTALLED_APPS.append('django_evolution')
except:
    pass

if use_debug_toolbar:
    MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INSTALLED_APPS.append('debug_toolbar')

#LOGIN_URL = '/'

# Fix for gallery problem?
#APPEND_SLASH=False

AUTH_PROFILE_MODULE='accounts.UserProfile'
#LOGIN_REDIRECT_URL='/'

#-------------------------- Comments -----------------------
COMMENTS_HIDE_REMOVED = True
COMMENTS_APP = 'citytree.citycomments'

#-------------------------- Cache --------------------------
# add to MIDDLEWARE_CLASSES (at the correct place!)
#django.middleware.cache.CacheMiddleware
CACHE_BACKEND = 'file:///home/tamizori/django_cache/citytree.net'
CACHE_MIDDLEWARE_SECONDS = 1800
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_KEY_PREFIX = ''

#-------------------------- StaticGenerator-----------------
# Instead of Cache - this is supposed to be even faster.
# installation: add 'staticgenerator.middleware.StaticGenerator'
#  to middleware, and set STATIC_GENERATOR_URLS and WEB_ROOT
STATIC_GENERATOR_URLS = (
    r'^/$',
)

#WEB_ROOT set in settings_local.py

#-------------------------- Citytree specific (i.e. the app, and the site) Site Settings ------------------
HEADER_MASK = '/home/tamizori/django/django_projects/citytree/frontpage/mask.png' #mask for main page header logo
SITE_LOGO   = '' #site logo
SHOW_WORKSHOPS_WITH_NO_EVENTS = False # True will add them at after the workshops with events - not very visible, but there.
CITYTREE_FEEDBACK_CONTACTS = ['tree@citytree.net']
NEW_MEMBERS_FRONTPAGE_TITLE = 'ברוכים המצטרפים לעץבעיר,'
MAX_NEXT_EVENTS = 3

# This user gets an email every time someone registers to a workshop.
WORKSHOP_REGISTRATION_NOTIFICATION_EMAIL = 'tree@citytree.net'

# -------------------------- Development Stuff -------------
# Leave this as None for default - sending to the blog author
SEND_EMAIL_ON_COMMENT = None
SERVE_SITEMEDIA_FROM_DJANGO = False

# -------------------------- Debug Toolbar -------------------
INTERNAL_IPS = ('127.0.0.1',)


#---------------------- DEVELOPMENT COMPROMISE ---------------
# this is the only difference between a development environment
# and production - in that settings_local.py file:
# change database, email addresses, turn on debugging flags.
from settings_local import *

