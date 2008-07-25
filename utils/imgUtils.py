from PIL import Image
from cityblog.models import Post
from django.template import Context, loader
import re

_REPLACE_IMG_MARKUP_RE = r'\[s*img\s+%s\s*\]'

def maskImage( inImgPath, inMaskPath, inLogoPath, outImgPath ):
    img = Image.open(inImgPath)
    mask = Image.open(inMaskPath)
    
    assert( img.size == mask.size )
    
    #if( inLogoPath ):
    #    logo = Image.open(inLogoPath)
    #    img.paste( logo, (650,25) )
    
    #out = img.convert('RGBA')
    #out.putalpha(mask)
    bg  = Image.new( 'RGBA', img.size,'#b6e3ab' )
    out = Image.composite( img, bg, mask )
    
    out.save(outImgPath, "JPEG")
    
def replacePostImages( text, postId, theTemplate ):
        """
        replace values of type [IMG n] with the relevant image from the post.

        usage: {{value|replacePostImages:"PostID"}}
        """

        #----------- Convert [img n] tags ------------------
        thePost = Post.objects.filter( id=postId )[0]
        
        t = loader.get_template(theTemplate)

        for img in thePost.postimage_set.all():
            idx = str(img.index)

            replaceStr =  t.render(Context({
                'imgUrl': img.get_image_url(),
                'imgLabel': img.label,
                'imgCaption': img.caption
            }))

            pattern = re.compile(_REPLACE_IMG_MARKUP_RE % idx, re.IGNORECASE)
            text = re.sub(pattern, '</p>'+replaceStr+"<p>", text )

        return text
