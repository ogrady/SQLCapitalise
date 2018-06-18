#!/usr/bin/env python

from setuptools import setup

setup(name='SQLCapitalise',
      version='0.1',
      description='Utility to capitalise keywords in the PostgreSQL dialect.',
      url='',
      author='Daniel O\'Grady',
      author_email='',
      license='MIT',
      python_requires='>=3',
      install_requires=[
          'psqlparse'
      ],
      zip_safe=False)