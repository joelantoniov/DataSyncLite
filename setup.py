#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="datasync_lite",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyspark==3.3.0",
        "azure-identity==1.12.0",
        "pyodbc==4.0.39",
        "great-expectations==0.15.50",
        "pyyaml==6.0",
        "azure-monitor-opentelemetry==1.0.0",
        "retry==0.9.2",
        "circuitbreaker==2.0.0"
    ],
    author="DataSyncLite Team",
    author_email="ops@company.com",
    description="Production-grade ETL pipeline for sales data processing",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License"
    ]
)
