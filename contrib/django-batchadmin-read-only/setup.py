#!/usr/bin/env python
from ez_setup import use_setuptools
use_setuptools()
from os import path
from setuptools import setup, find_packages

VERSION = open(path.join(path.dirname(__file__), 'VERSION')).read().strip()

setup(
    name = "django-batchadmin",
    version = VERSION,
    url = "http://code.google.com/p/django-batchadmin/",
    author = "Brian Beck",
    author_email = "exogen@gmail.com",
    license = "MIT License",
    description = "Batch actions in the change list views of your Django admin site.",
    packages = ['batchadmin'],
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: Site Management'
    ],
    long_description = """
    This Django app provides a ModelAdmin subclass that will render the
    model's change list with selectable items and actions.

    One design goal of this project is to do as little as possible. The 
    only action actually included in the project is a batch delete action. 
    Changes to ModelAdmin behavior and template structure are minimal. 
    """
)
