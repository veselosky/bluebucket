#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import sys

# Add all required libraries to requirements.txt
with open('requirements.txt') as f:
    requirements = [line for line in f.read().split('\n') if line]

test_requirements = [
    'pytest',
    'mock',
]

about = {}
with open("bluebucket/__about__.py") as fp:
    exec(fp.read(), about)

if sys.argv[-1] == 'info':
    for k, v in about.items():
        print('%s: %s' % (k, v))
    sys.exit()

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name=about['__name__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=[
        'bluebucket',
    ],
    package_dir={'bluebucket':
                 'bluebucket'},
    include_package_data=True,
    install_requires=requirements,
    license=about['__license__'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
