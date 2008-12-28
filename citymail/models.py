from django.db import models

class SentEmail(models.Model):
    mail_to=models.CharField(max_length=512)
    mail_from=models.CharField(max_length=512)
    mail_subject=models.CharField(max_length=1024)
    mail_contents=models.TextField()
    mail_sent_date=models.DateTimeField(auto_now_add=True)

