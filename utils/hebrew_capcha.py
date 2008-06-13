# -*- coding:utf-8 -*-

""" God, I should learn some doctests.

>>> assert(all([rev_alphabet[alphabet[i]]==i for i in xrange(len(alphabet))]))

"""

from random import randint
import PIL.Image
import os
from StringIO import StringIO
import struct
import binascii

alphabet='אבגדהוזחטיכלמנסעפצקרשת'.decode('utf-8')
rev_alphabet = dict([(c, i) for i, c in enumerate(alphabet)])
num = len(alphabet)
aleph_code_point = ord('א'.decode('utf-8'))

def write_hebrew_alphabet():
    """ writes a py file with uuencode64-ed png files
    """
    import make_font_png
    output_file = 'generated_hebrew_alphabet.py'
    fd = open(output_file, 'w+')
    fd.write('images = [\n')
    for i, letter in enumerate(alphabet):
        filename='hebrew_%s.png' % i
        make_font_png.render_title(letter, size=20, filename=filename)
        img = PIL.Image.open(filename)
        s = binascii.b2a_base64(img.tostring('raw'))
        os.unlink(filename)
        fd.write('(%s, r"%s"),\n' % (repr(img.size), s.strip()))
    fd.write(']\n')
    fd.close()

def make_alphabet_dict():
    try:
        import generated_hebrew_alphabet
    except:
        write_hebrew_alphabet()
    from generated_hebrew_alphabet import images
    d = {}
    for i, letter in enumerate(alphabet):
        d[i] = dict(letter=letter,
          image=PIL.Image.fromstring('RGBA', images[i][0],
              binascii.a2b_base64(images[i][1]), 'raw'))
        d[i]['width'] = d[i]['image'].size[0]
    return d


def make_alphabet_dict_old():
    d = {}
    for i, letter in enumerate(alphabet):
        filename='images/hebrew_%s.png' % i
        if not os.path.exists(filename):
            import make_font_png
            make_font_png.render_title(letter,size=20, filename = filename)
        d[i] = dict(letter=letter, image=PIL.Image.open(filename))
        d[i]['width'] = d[i]['image'].size[0]
    return d

def get_random_hebrew_alphabet_string(num_chars=6):
    return ''.join([alphabet[randint(0, num - 1)] for i in xrange(num_chars)])

def get_random_hebrew_string_with_end_of_word_letters(num_chars=6):
    # This isn't really good, since it doesn't fit the generated capcha, which
    # uses my shortened only "regular" letters alphabet. But I think the code
    # is cool :)
    return ''.join([struct.pack('<h', aleph_code_point + randint(0, num - 1))
            for i in xrange(num_chars)]).decode('utf-16') # I have no idea how to generate a valid utf-8 encoding for hebrew. utf-16 is easier - its just the code point in big endian. or is that little?

def generate_capcha(letters):
    # letters is a unicode string. could have been simpler - but this will ease debugging, I think.
    assert(type(letters) is unicode)
    d = make_alphabet_dict()

    height = max([l['image'].size[1] for l in d.values()])
    #return ha.crop((int(i*pxf), 0, int((i+1)*pxf), height))

    x_sep = 2
    capcha = [d[rev_alphabet[c]] for c in letters]
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
    s = get_random_hebrew_alphabet_string()
    open('test.png','wb+').write(generate_capcha(s))
    assert(all([rev_alphabet[alphabet[i]]==i for i in xrange(len(alphabet))]))

