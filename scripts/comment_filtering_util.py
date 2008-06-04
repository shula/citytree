from django.contrib.comments import models as comment_models

bad_ips = ['89.149.197.252']

def all_from_ip(ip):
    return comment_models.FreeComment.objects.filter(ip_address=ip)

#all_from_ip('89.149.197.252').delete()

def byip():
    all=comment_models.FreeComment.objects.all()
    x={}
    for c in all:
        x[c.ip_address]=x.get(c.ip_address,[])+[c]
    return x

x = byip()
ips=sorted(zip(map(len,x.values()),x.keys()))
print ips[-10:]

