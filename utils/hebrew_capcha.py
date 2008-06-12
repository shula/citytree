# -*- coding:utf-8 -*-

import random
import PIL.Image
import os
from StringIO import StringIO

def make_alphabet_dict():
    alphabet='אבגדהוזחטיכלמנסעפצקרשת'.decode('utf-8')
    d = {}
    for i, letter in enumerate(alphabet):
        filename='images/hebrew_%s.png' % i
        if not os.path.exists(filename):
            import make_font_png
            make_font_png.render_title(letter,size=20, filename = filename)
        d[i] = dict(letter=letter, image=PIL.Image.open(filename))
        d[i]['width'] = d[i]['image'].size[0]
    return d

def generate_capcha(num_chars=6):
    d = make_alphabet_dict()
    num = len(d)

    height = max([l['image'].size[1] for l in d.values()])
    #return ha.crop((int(i*pxf), 0, int((i+1)*pxf), height))

    x_sep = 2
    capcha = [d[random.randint(0, num - 1)] for i in xrange(10)]
    width = sum([x['width']+x_sep for x in capcha])

    #target=PIL.Image.new('RGB',(width, height))
    target=PIL.Image.fromstring('RGB',(width, height), '\xff\xff\xff'*width*height)
    x = 0
    for l in capcha:
        target.paste(l['image'], (x, 0))
        x += l['width'] + x_sep

    s = StringIO()
    target.save(s, format='PNG')
    return s.getvalue() # the png is returned

if __name__ == '__main__':
    generate_capcha()

