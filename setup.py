#!/usr/bin/env python3

import sys
import setuptools

if sys.version_info.major == 2:
    if sys.version_info < (2, 7):
        sys.exit('Python version not supported.')
    entry_points = None
    install_requires = ['enum34>=1.0']
    print("Note that you need Python3 to execute kspalculator script.")
elif sys.version_info.major == 3:
    if sys.version_info < (3, 4):
        sys.exit('Python version not supported.')
    entry_points = {'console_scripts': ['kspalculator=kspalculator.__main__:main']}
    install_requires = None
else:
    sys.exit('Python version not supported.')

setuptools.setup(
    name='kspalculator',
    version='0.10',
    packages=['kspalculator'],
    url='https://github.com/aandergr/kspalculator',
    license='MIT',
    author='Alexander Graf, André Koch-Kramer',
    author_email='mail@agraf.me, koch-kramer@web.de',
    description='Determine the best rocket propulsion designs for one stage of a rocket, given a '
                'set of constraints and preferences (Kerbal Space Program).',
    long_description=open('README.rst').read(),
    entry_points=entry_points,
    zip_safe=True,
    install_requires=install_requires,
    test_suite="tests",
    keywords='ksp kerbal space program kerbalspaceprogram calculator calculate optimize engine fuel propellant',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
