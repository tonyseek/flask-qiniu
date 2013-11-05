#!/usr/bin/env python

from setuptools import setup


setup(
    name="Flask-Qiniu",
    version="0.1.0",
    author="Jiangge Zhang",
    author_email="tonyseek@gmail.com",
    description="the flask extension of Qiniu storage service.",
    url="https://github.com/tonyseek/flask-qiniu",
    requires=[
        "sevencow",
        "Flask",
    ],
)
