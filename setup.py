#!/usr/bin/env python

from distutils.core import setup

setup(
    name='srvmon',
    version='1.0',
    description='Server Monitoring Tool',
    author='Davide Gessa',
    author_email='gessadavide@gmail.com',
    url='https://github.com/dakk/srvmon',
    setup_requires='setuptools',
    packages=['srvmon'],
    #package_data={'gweatherrouting': ['data/*', 'data/boats/*', 'data/boats/*/*', 'ui/gtk/*.glade']},
    entry_points={
        'console_scripts': [
            'srvmon=srvmon.srvmon:main',
        ],
    },
    install_requires=open ('requirements.txt', 'r').read ().split ('\n')
)