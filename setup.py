from setuptools import setup

setup(
    name='validation',
    version='0.0.1',
    description='Validation Tool for Python Data Structures',
    long_description="""
Validation Tool for Python Data Structures

Copyright (c) 2015, Stephan Schultchen.

License: MIT (see LICENSE for details)
    """,
    packages=['validation'],
    url='https://github.com/schlitzered/validation',
    license='MIT',
    author='schlitzer',
    author_email='stephan.schultchen@gmail.com',
    test_suite='test',
    platforms='posix',
    classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3'
    ],
    keywords=[
        'validation, validator, validate'
    ]
)
