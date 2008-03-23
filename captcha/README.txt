Prerequisites:

* Django >= 0.96 and using newforms

* PIL (Python Imaging Library)

* At least one TrueType font installed

To use Captcha:

* Expand the archive (you've probably alreaedy done this)

* Put the resulting directory in a subdirectory of your Django project

* Modify the settings.py file in the directory, specifically you will probably
  need to specify a font and the base_url that you intend to use for Captcha

* Add Captcha to your installed apps and include its urls file in yours.

* Syncdb

* Make any form that you want Captcha'd extend CaptchaForm

Caveats:

* I still haven't tested this other than using form_for_model(form=CaptchaForm)

* I'm new to Django/Python, so I'm sure I have some dumb things in here

Copyright (c) 2007 Brandon Low
Licensed under the GPL v2

With ideas from http://code.google.com/p/django-captcha/

See COPYING for license details
