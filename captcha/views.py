# Copyright (c) 2007 Brandon Low
# Licensed under the GPL v2
#
# Some ideas in this file from http://code.google.com/p/django-captcha/
from cStringIO import StringIO
from django.http import HttpResponse
from models import Captcha
from settings import *
from captcha.generator.Visual import Tests
from settings import CAPTCHA_WIDTH, CAPTCHA_HEIGHT

def captcha_image(request,id):
    c = Captcha.objects.get(pk=id)
    text = c.text
    
    # begin drawing
#    font = ImageFont.truetype(FONT_PATH,FONT_SIZE)
#    # Size of the rendered text
#    (xs,ys) = font.getsize(text)
#    # 2 pixel border around the text
#    (x_size, y_size) = (xs+4,ys+4)
#    image = Image.new('RGB', (x_size, y_size), BGCOLOR)
#    draw = ImageDraw.Draw(image)
#    # Draw the text, starting from (2,2) so the text won't be edge
#    draw.text((2, 2), text, font=font, fill=COLOR)
#    # Make some messes on the image
#    draw.arc((0,y_size/3,x_size,y_size*2), 220, 320, fill=LINE_COLOR)
#    draw.line((0,0)+image.size, fill=LINE_COLOR)
    # end drawing
    
    image = Tests.PseudoGimpy(word=text).render(size=(CAPTCHA_WIDTH, CAPTCHA_HEIGHT))
    
    # Saves the image in a StringIO object, so you can write the response
    # in a HttpResponse object
    file = StringIO()
    image.save(file,"PNG")
    response = HttpResponse()
    response['Content-Type'] = 'image/png'
    response['Content-Length'] = str(file.tell())
    file.seek(0)
    response.write(file.read())
    file.close()
    return response 
