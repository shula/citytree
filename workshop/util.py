import datetime
from citytree.workshop.models import WorkshopEventPart
from utils.hebDate import date2hebdate

def makeHebCalLinks(start_date=None):
    retLinks = {}
    if start_date is None:
        start_date = datetime.date.today()
    end_date = date2hebdate(datetime.date.today())
    end_date.setHebDate(day=end_date.getDaysInHebMonth()-1,month=end_date.hebMonth,year=end_date.hebYear)
    end_date = end_date.getEngDate()
    evps = WorkshopEventPart.objects.filter(start_time__gte=start_date).exclude(start_time__gte=end_date)
    for evp in evps:
        retLinks[date2hebdate(evp.start_time).hebDayOfMonth - 1] = evp.workshop_event.workshop.get_absolute_url()
    return retLinks

