#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='bb8',
    version='0.2.4.dev',
    description='BB8 - A robot to support developer',
    author='Thong Dong',
    author_email='thongdong7@gmail.com',
    url='https://github.com/thongdong7/mydev',
    packages=find_packages(exclude=["build", "dist", "tests*"]),
    install_requires=[
        'jinja2==2.8',
        'pyyaml==3.11',
        'click==6.6',
        'tornado==4.3',
        'python-dateutil==2.5.3'
    ],
    # extras_require={
    #     'cli': [
    #         'click==6.6',
    #         'pyyaml==3.11'
    #     ],
    # },
    entry_points={
        'console_scripts': [
            'bb8=bb8.script.main:bb8_script',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: Python Software Foundation License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        # "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    include_package_data=True,
)
