from setuptools import setup

setup(
    name='mtgreatest-py',
    version='0.0',
    url='http://github.com/oelarnes/mtgreatest',
    author='Joel Barnes',
    author_email='mtgreatest@gmail.com',
    install_requires=[
        'bs4',
        'distance',
        'requests',
        'python-dateutil',
        'MySQL-python'
    ],
    licence='MIT',
    packages=[
        'mtgreatest',
        'mtgreatest.scrape',
        'mtgreatest.rdb'
    ],
    zipsafe=False
)   
    
