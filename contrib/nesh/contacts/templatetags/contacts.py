# pylint: disable-msg=R0913,W0612,W0613
from django.template import (
                             TemplateSyntaxError, 
                             Library, 
                             Node, 
                             )
from nesh.contacts.models import Country, City, Contact

register = Library()

#=========================================================================================
# get all countries
#=========================================================================================
class GetCountriesNode(Node):
    def __init__(self, variable):
        super(GetCountriesNode, self).__init__()
        self.variable = variable

    def render(self, context):
        context[self.variable] = tuple(Country.objects.all())
        return ''

@register.tag
def get_countries(parser, token): #IGNORE:W0613
    args = token.contents.split()
    
    if len(args) != 3 or args[1] != 'as':
        raise TemplateSyntaxError, "syntax error (got %r)" % args

    return GetCountriesNode(args[2])

#=========================================================================================
# get all countries
#=========================================================================================
class GetCitiesNode(Node):
    def __init__(self, variable):
        super(GetCitiesNode, self).__init__()
        self.variable = variable

    def render(self, context):
        context[self.variable] = tuple(City.objects.all())
        return ''

@register.tag
def get_cities(parser, token): #IGNORE:W0613
    args = token.contents.split()
    
    if len(args) != 3 or args[1] != 'as':
        raise TemplateSyntaxError, "syntax error (got %r)" % args

    return GetCitiesNode(args[2])

#=========================================================================================
# get all contacts
#=========================================================================================
class GetContactsNode(Node):
    def __init__(self, variable):
        super(GetContactsNode, self).__init__()
        self.variable = variable

    def render(self, context):
        context[self.variable] = tuple(Contact.objects.all())
        return ''

@register.tag
def get_contacts(parser, token): #IGNORE:W0613
    args = token.contents.split()
    
    if len(args) != 3 or args[1] != 'as':
        raise TemplateSyntaxError, "syntax error (got %r)" % args

    return GetContactsNode(args[2])
