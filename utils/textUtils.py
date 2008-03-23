import re
from cleanhtml import sanitize


def wikiSub( inStr ):
    """
    Implement a small subset of wiki syntax:
    ''italic''
    '''bold'''
    [http://foo an external link]
    """
    from cityblog.models import post
    
    #First sanitize input string
    
    inStr = sanitize( unicode(inStr,encoding='utf_8') ).encode('utf-8')
    
    boldItRE       = re.compile( "''''(?P<txt>[^']+)''''", re.M)
    boldRE         = re.compile( "'''(?P<txt>[^']+)'''", re.M)
    italicRE       = re.compile( "''(?P<txt>[^']+)''", re.M)
    linkRE         = re.compile( "\[(?P<url>http://\S+)\s+(?P<txt>[^\]]+)\]")
    internalLinkRE = re.compile( "\[\[(?P<post_num>\d+)\s*\|\s*(?P<link_text>[^\|]+)\]\]" )
    newLineRE      = re.compile( r'\r\n|\n\n', re.M)
    
    #Switch tags and external links
    inStr = re.sub( boldItRE, "<i><b>\g<txt></b></i>",inStr) 
    inStr = re.sub( boldRE, "<b>\g<txt></b>",inStr) 
    inStr = re.sub( italicRE, "<i>\g<txt></i>",inStr)
    inStr = re.sub( linkRE, "<a href='\g<url>'>\g<txt></a>",inStr)
    
    #Handle internal links
    m = re.search( internalLinkRE, inStr )
    while m:
        post_num = m.group('post_num')
        link_txt = m.group('link_text')
        
        pre  =  inStr[:m.start()]
        after =  inStr[m.end():]
        
        #try to find posts with a matching ID
        thePosts = post.objects.filter(id=post_num)
        
        if( len(thePosts) != 1):
            print post_num,thePosts
            inStr = pre+"<!-- Invalid Link -->"+after
        else:
            theUrl = thePosts[0].get_absolute_url()
            inStr = "".join( [pre,"<a href='%s'>%s</a>" % (theUrl, link_txt),after] )
        
        m = re.search( internalLinkRE, inStr )
        
     
    #change \n\n to a paragraph start   
    parts = re.split( newLineRE, inStr )
    inStr = ''.join( ['<p>', '</p><p>'.join( parts ), '</p>'] )

    
        
    return inStr