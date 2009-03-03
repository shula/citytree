import sys, os
from datetime import datetime

home = os.environ['HOME']
BASE_PATH = home # amber
base_path_citytree = os.path.join(home, 'django/django_projects')
if os.path.exists(base_path_citytree):
    BASE_PATH = base_path_citytree

sys.path.append(BASE_PATH)
sys.path.append(os.path.join(BASE_PATH, 'citytree'))

import citytree.utils.litrom as litrom
from citytree.utils.register_utils import register_new_user, DUPLICATE_ERROR
from django.contrib.auth.models import User

TEMP_FILE='/tmp/litrom_output.csv'

log_filename = os.path.join(BASE_PATH, 'citytree/cron/litrom.log')
log_file = open(log_filename, 'a+')
def log(s):
    log_file.write('%s\n' % s)

if __name__ == '__main__':
    #litrom.get_csv()
    if os.path.exists(TEMP_FILE):
        txt = open(TEMP_FILE).read()
    else:
        log('# contacting litrom - %s' % (datetime.now()))
        print ">>> contacting litrom"
        try:
            txt = litrom.get_csv_html()
        except Exception,e:
            log("# error - problem getting csv from litrom. probably site updated.")
            log("# %s" % repr(e))
            raise SystemExit
        print "<<<"
    print "start out:", User.objects.count()
    log('# registring - %s - %s users' % (datetime.now(), User.objects.count()))
    for donor in litrom.get_donors(txt):
        error = register_new_user(donor, really_send_email=True)
        if error in [DUPLICATE_ERROR]: continue
        log('%s, %s' % (str(donor['email']), error))

    log('# done %s - %s users' % (datetime.now(), User.objects.count()))
        
    print "going out:", User.objects.count()

