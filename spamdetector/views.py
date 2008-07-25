from django.shortcuts import render_to_response, get_object_or_404

from spamdetector.models import BannedIp, AllowedBanRequests

def ban_request( request, hash ):
    b = get_object_or_404(AllowedBanRequests, hash=hash)
    ip_address = b.ip_address
    BannedIp(ip_address=ip_address).save()
    b.delete()
    return render_to_response('spamdetector/ban_request_successful.html', {'ip_address': ip_address})
 
