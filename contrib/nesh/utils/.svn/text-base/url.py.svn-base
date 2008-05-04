import urllib
import urllib2

def urljoin(root, *args, **kwargs):
    """ join urls like os.path.join """
    
    ret = [root.strip('/')]
    
    for arg in args:
        # strip trailing/starting slashes and add
        ret.append(str(arg).strip('/'))
    #
    #ret.append('') # add trailing slash
    ret = ('/' + '/'.join(ret)).replace('//', '/')
    if 'server' in kwargs:
        server = kwargs.get('server', '')
        return server.rstrip('/') + urllib.quote(ret)
    #
    return urllib.quote(ret)
#

def url_normalize(url, strip_get=True):
    """ add / at end, unqoute, strip GET parameters """
    url = urllib.unquote(url)
    
    # cut off post arguments
    if strip_get and ('?' in url):
        url = url.split('?')[0]
    #
    
    if not url.endswith('/'):
        url += '/'
    #
    
    return url
# url_normalize

def check_url(url):
    print 'URL: Check for', url,
    import urllib2
    try:
        u = urllib2.urlopen(url)
    except ValueError, e:
        print e
        return False
    except urllib2.HTTPError, e:
        # 401s are valid; they just mean authorization is required.
        if e.code not in ('401',):
            print e
            return False
    except Exception, e: # urllib2.URLError, httplib.InvalidURL, etc.
        print e
        return False
    print 'OK'
    return True
#