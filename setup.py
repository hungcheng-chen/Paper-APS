#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

setup(
    author="HungCheng Chen",
    author_email="hcchen.nick@gmail.com",
    name="paper_aps",
    keywords="paper_aps",
    packages=find_packages(
        include=["paper_aps", "paper_aps.*"]
    ),
    test_suite="tests",
    license="MIT license",
    version="0.1.0",
)
