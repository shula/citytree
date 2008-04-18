from django.contrib.syndication.feeds import Feed
from cityblog.models import post

class LatestPosts(Feed):
    title = "Citytree Latest Posts"
    link = "/latestposts/"
    description = "Post updates for www.citytree.net"
    def items(self):
        return post.objects.order_by('-post_date')[:10]
