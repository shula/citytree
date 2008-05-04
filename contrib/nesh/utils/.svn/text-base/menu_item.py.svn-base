from django.utils.translation import gettext

class MenuItem(object):
    """ menu item """
    def __init__(self, name, url, leaf=False):
        super(MenuItem, self).__init__()

        self._sub = []
        self._url = url
        self._name = name
        self._leaf = leaf
    #

    def add_sub(self, sub):
        self._sub.append(sub)
    #

    def link(self, url, name, add_styles=None):
        """ create link """
        styles = []

        if add_styles is not None:
            styles += add_styles
        #
        if styles:
            styles = ' class="%s"' % ' '.join(styles)
        else:
            styles = ''
        #

        return '<a href="%s"%s>%s</a>' % (url, styles, name)
    # link

    def render(self, current_url):
        # cut off post arguments
        if '?' in current_url:
            current_url, _ = current_url.split('?')

        if self._url.startswith('/') and not current_url.startswith('/'):
            # add leading /
            current_url = '/' + current_url
        elif not self._url.startswith('/') and current_url.startswith('/'):
            # strip leading /
            current_url = current_url[1:]
        #

        if self._url.endswith('/') and not current_url.endswith('/'):
            # add trailing /
            current_url += '/'
        elif not self._url.endswith('/') and current_url.endswith('/'):
            # strip trailing /
            current_url = current_url[:-1]
        #

        # item is current ?
        if self._url == current_url:
            current = True
        else:
            current = False

        ret = []
        if len(self._sub):
            ret.append('<li>')
            ret.append(self.link(self._url, self._name, ['title']))

            ret.append('<ul>\n')
            if self._url != '#':
                ret.append(current and '<li class="current title_link">' or '<li class="title_link">')
                ret.append(self.link(self._url, gettext('show list of %s') % self._name))
                ret.append('</li>')
            #

            for sub in self._sub:
                ret.append(sub.render(current_url))
            # for
            ret.append('</ul>\n')
        else: # no submenu
            ret.append(current and '<li class="current">' or '<li>')
            ret.append(self.link(self._url, self._name))

        # if
        ret.append('</li>\n')
        return ''.join(ret)
    # render
#
