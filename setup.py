#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'amtool>=0.1.9', 'wxPython>=4.0.6']

setup_requirements = []

test_requirements = []

setup(
    author="Kenneth E. Bellock",
    author_email='ken@bellock.net',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="A user interface to the Artifact Management Tool",
    entry_points='''
        [amt.plugins]
        gui=amtui.cli:gui
    ''',
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='amtui',
    name='amtui',
    packages=find_packages(include=['amtui']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/bellockk/amtui',
    version='0.1.2',
    zip_safe=False,
)
