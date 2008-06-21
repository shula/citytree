import sys, os
BASE_PATH = os.path.join(os.environ['HOME']) # amber
sys.path.append(BASE_PATH)
sys.path.append(os.path.join(BASE_PATH, 'citytree'))
import citytree.utils.litrom as litrom
from citytree.utils.register_utils import register_new_user
from django.contrib.auth.models import User

TEMP_FILE='/tmp/litrom_output.csv'

if __name__ == '__main__':
    #litrom.get_csv()
    if os.path.exists(TMP_FILE):
        txt = open(TMP_FILE).read()
    else:
        print ">>> contacting litrom"
        txt = litrom.get_csv_html()
        print "<<<"
    print "start out:", User.objects.count()
    for donor in litrom.get_donors(txt):
        register_new_user(donor)
    print "going out:", User.objects.count()
