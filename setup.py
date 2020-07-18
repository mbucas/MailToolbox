#!/usr/bin/env python
# coding:utf8

import sys
from distutils.core import setup

if sys.platform == 'win32':
    import py2exe
    sys.path.append("C:\\Program Files\\Calibre2\\Microsoft.VC90.CRT")

setup(
    name='MailToolbox',
    version='1.0',
    description='A toolbox to move mail',
    long_description='A toolbox to move mail',
    author=u'Mickaël Bucas',
    author_email='mbucas@gmail.com',
    url='https://mickael.bucas.name/',
    license='GPLv3+',
    keywords=[
        'mail', 'email', 'e-mail', 'utility', 'utilities', 'move',
        'migration', 'extract', 'backup'
    ],
    platforms=['Linux', 'Windows'],
    scripts=[
        'MailToolboxRunner.py',
        'MailToolboxStudio.py',
    ],
    console=[
        'MailToolboxRunner.py',
    ],
    windows=[
        'MailToolboxStudio.py',
    ],
    packages=[
        'config',
        'engine',
        'project',
        'storage',
        'transformations',
        'ui',
    ],
    package_data={'ui': ['icon.png', 'mainwindow.ui']},
    data_files=[
        ('ui', ['ui\\icon.png', ]),
        ('ui', ['ui\\mainwindow.ui', ]),
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Qt'
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Utilities',
    ],
)
