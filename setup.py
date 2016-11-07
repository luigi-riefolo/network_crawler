#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Setup script for network_crawler project.

Also installs included versions of third party libraries,
if those libraries are not already installed.
"""

from __future__ import print_function

import sys
from setuptools import setup, find_packages
import network_crawler


if sys.version_info < (2, 6):
    print('network_crawler API requires '
          'python version >= 2.6.', file=sys.stderr)
    sys.exit(1)


setup(
    name='Network Operator',
    version=network_crawler.__version__,
    author='Luigi Riefolo',
    author_email='luigi.riefolo@gmail.com',
    url='http://github.com/luigi-riefolo/network_crawler',
    description='Network operator Python application',
    long_description=open('README.md').read(),
    license='MIT License',
    packages=find_packages(exclude=['*tests*']),
    include_package_data=True,
    install_requires=map(str.strip, open('requirements.txt')),
    tests_require=['pytest>=2.8.0', 'coverage-4.2', 'pytest-cov-2.4.0'],
    platforms=['Linux'],
    scripts=['scripts/network_crawler'],
    data_files=[('network_crawler', ['requirements.txt'])],
    classifiers=(
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 1 - Production/Stable',
        'Environment :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ),
    keywords='network operator calling costs'
)
