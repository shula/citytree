from PIL import Image
from cityblog.models import Post
from django.template import Context, loader
import re
import StringIO

_REPLACE_IMG_MARKUP_RE = r'\[s*img\s+%s\s*\]'

def maskImage( img_as_image_field_file, inMaskPath, inLogoPath ):
    """ Returns a masked version of the given image.
    doesn't write anything to disk. reads the inMaskPath and inLogoPath images.
    """
    mask = Image.open(inMaskPath)
    img_as_image_field_file.close()
    img_as_image_field_file.open()
    data = img_as_image_field_file.read()
    img_data = StringIO.StringIO(data)
    img = Image.open(img_data)
    
    assert( img.size == mask.size )
    
    #if( inLogoPath ):
    #    logo = Image.open(inLogoPath)
    #    img.paste( logo, (650,25) )
    
    #out = img.convert('RGBA')
    #out.putalpha(mask)
    bg  = Image.new( 'RGBA', img.size,'#b6e3ab' )
    out = Image.composite( img, bg, mask )
    
    out_sio = StringIO.StringIO()
    out.save(out_sio, 'jpeg')
    #out.save(outImgPath, "JPEG")
    img_as_image_field_file.close()
    img_as_image_field_file.open('w')
    out_data = out_sio.getvalue()
    img_as_image_field_file.write(out_data)
    img_as_image_field_file.close()
    img_as_image_field_file.file.size=len(out_data)
    return img_as_image_field_file
    
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
                'imgUrl': img.image.url,
                'imgLabel': img.label,
                'imgCaption': img.caption
            }))

            pattern = re.compile(_REPLACE_IMG_MARKUP_RE % idx, re.IGNORECASE)
            text = re.sub(pattern, '</p>'+replaceStr+"<p>", text )

        return text
