import sys
sys.path.append('../../')
import settings
import os

user=settings.DATABASE_USER
pwd=settings.DATABASE_PASSWORD

os.system('mysqldump -u%(user)s -p"%(pwd)s" %(dbname)s > db_backup.pre' % {'user':user, 'pwd':pwd, 'dbname':settings.DATABASE_NAME})
os.system('mysql -u%(user)s -p%(pwd)s %(dbname)s < %(script)s' % {'user':user, 'pwd':pwd, 'dbname':settings.DATABASE_NAME, 'script':'comments_update_script_django_1.0.sql'})

#os.system('mysql -u%(user)s -%(pwd)s %(dbname)s' % {'user':user, 'pwd':pwd, 'dbname':settings.DATABASE_NAME})


