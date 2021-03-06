from citytree.spamdetector.models import BannedIp

class SpamDetector(object):
    def moderate(self, comment, content_object):
        """ Just like the moderate method of moderators.CommentModerators

        uses ip lists, currently hard coded

        returns True if comment is to be set non-public, False otherwise
        """
        #if comment.ip_address in ['89.149.197.252']:
        if len(BannedIp.objects.filter(ip_address=comment.ip_address)) > 0:
            return True
        return False

spamDetector = SpamDetector()

