#!/bin/sh
export DJANGO_SETTINGS_MODULE=citytree.settings
export PYTHONPATH=:/home/tamizori/pythonlibs/lib/python2.4/site-packages/:/home/tamizori/pythonlibs/lib/python2.4/site-packages/PIL/:/home/tamizori/django/django_src:/home/tamizori/django/django_projects:/home/tamizori/pythonlibs/lib/python2.4/site-packages/ipython-0.8.2-py2.4.egg/
# TODO: cd to the directory in which the file being executed (well, 
# not executed, not bash, but this script) is in.
cd $HOME/django/django_projects/citytree/cron
python2.4 read_litrom.py
