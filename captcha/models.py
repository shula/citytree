# Copyright (c) 2007 Brandon Low
# Licensed under the GPL v2
from datetime import datetime, timedelta
from django.db import models
from settings import TIMEOUT

#------------------------------------------------------------------------------ 
class Captcha(models.Model):
    text = models.CharField(maxlength=10)
    date = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def clean_expired():
        # Clean out expired Captchas first
        expired_before = datetime.now()-timedelta(minutes=TIMEOUT)
        Captcha.objects.filter(date__lt=expired_before).delete()

    class Admin:
        pass