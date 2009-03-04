from django.shortcuts import render_to_response, get_object_or_404

from spamdetector.models import BannedIp, AllowedBanRequests
from cityblog.models import HashPoint
from citycomments.models import CityComment

def ban_request( request, hash ):
    b = get_object_or_404(AllowedBanRequests, hash=hash)
    ip_address = b.ip_address
    BannedIp(ip_address=ip_address).save()
    b.delete()
    return render_to_response('spamdetector/ban_request_successful.html', {'ip_address': ip_address})

def hide_comment( request, hash ):
    hp = get_object_or_404(HashPoint, hash=hash)
    comment_id = int(hp.data)
    comment = get_object_or_404(CityComment, id=comment_id)
    comment.is_public = 0
    comment.is_removed = 1
    comment.save()
    return render_to_response('spamdetector/hide_comment_successful.html', {'comment_id': comment_id})
