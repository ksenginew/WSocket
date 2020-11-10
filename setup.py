#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils

from setuptools import setup
from os import path

import wsocket
devstatus=[
'Planning',
'Pre-Alpha',
'Alpha',
'Beta',
'Production/Stable',
'Mature',
'Inactive'
]

here = path.dirname(__file__)
# Get the long description from the README file
long_description = open(path.join(here, 'README.md')).read()

setup(

    # https://packaging.python.org/specifications/core-metadata/#name
    name='WSocket',
    
    # https://www.python.org/dev/peps/pep-0440/
    # https://packaging.python.org/en/latest/single_source_version.html
    version=wsocket.__version__,
    
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='Simple WSGI Websocket Server, Framework, Middleware And App',
    
    # https://packaging.python.org/specifications/core-metadata/#description-optional
    long_description=long_description,
    
    # text/plain, text/x-rst, and text/markdown
    # https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
    long_description_content_type="text/markdown",
    
    author=wsocket.__author__,
    author_email='kavindusanthusa@gmail.com',
    
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    url='https://github.com/Ksengine/wsocket/',
    
    keywords='sample, setuptools, development',  # Optional

    py_modules=['wsocket'],
    scripts=['wsocket.py'],
    license='MIT',
    platforms='any',
    classifiers=['Development Status :: {} - {}'.format(wsocket.__status__, devstatus[wsocket.__status__-1]),
               "Operating System :: OS Independent",
               'Intended Audience :: Developers',
               'License :: OSI Approved :: MIT License',
               'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
               'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
               'Topic :: Internet :: WWW/HTTP :: WSGI',
               'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
               'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
               'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
               'Topic :: Software Development :: Libraries :: Application Frameworks',
               'Programming Language :: Python',
               'Programming Language :: Python :: 2',
               'Programming Language :: Python :: 2.3',
               'Programming Language :: Python :: 2.4',
               'Programming Language :: Python :: 2.5',
               'Programming Language :: Python :: 2.6',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Programming Language :: Python :: 3.0',
               'Programming Language :: Python :: 3.1',
               'Programming Language :: Python :: 3.2',
               'Programming Language :: Python :: 3.3',
               'Programming Language :: Python :: 3.4',
               'Programming Language :: Python :: 3.5',
               'Programming Language :: Python :: 3.6',
               'Programming Language :: Python :: 3.7',
               'Programming Language :: Python :: 3.8',
               'Programming Language :: Python :: 3.9',
               'Programming Language :: Python :: 3.10',
               'Programming Language :: Python :: Implementation',
               'Programming Language :: Python :: Implementation :: CPython',
               'Programming Language :: Python :: Implementation :: IronPython',
               'Programming Language :: Python :: Implementation :: Jython',
               'Programming Language :: Python :: Implementation :: PyPy',
               'Programming Language :: Python :: Implementation :: Stackless',
               'Framework :: WSocket',
               'Topic :: Communications :: Chat',
               'Topic :: Internet',
               'Topic :: Internet :: WWW/HTTP',
               'Topic :: Internet :: WWW/HTTP :: Browsers',
               'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
               'Topic :: Internet :: WWW/HTTP :: WSGI',
               'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
               'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
               'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
               ],
               
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    project_urls={
        'Bug Reports': 'https://github.com/Ksengine/wsocket/issues/',
        'Documentation': 'https://wsocket.gitbook.io/',
        'Source': 'https://github.com/Ksengine/wsocket/',
    },

    )
    
