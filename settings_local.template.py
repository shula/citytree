# settings that change when we move the site from host to host
# - the database
# - the on disk absolute location (relative locations don't change)

#DEBUG = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'mysql'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'tami_citytree_django'             # Or path to database file if using sqlite3.
DATABASE_USER = 'tami'             # Not used with sqlite3.
DATABASE_PASSWORD = 'DZey9TQt'         # Not used with sqlite3.
DATABASE_HOST = 'mysql.citytree.dreamhosters.com'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

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

# handy for stuff that doesn't fall under media but still would
# change if site is moved to another domain
SITE_HOSTNAME = 'www.citytree.net'

TEMPLATE_DIRS = (
    '/home/tamizori/django/django_projects/citytree/templates'
)

#-------------------------- Site Settings ------------------
HEADER_MASK = '/home/tamizori/django/django_projects/citytree/frontpage/mask.png' #mask for main page header logo

#-------------------------- Email Settings -----------------
DEFAULT_FROM_EMAIL='noreply@citytree.net'


