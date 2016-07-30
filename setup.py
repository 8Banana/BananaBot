#!/usr/bin/env python3
import setuptools

from bananabot import __version__

setuptools.setup(
    name="bananabot",
    version=__version__,
    description="A very simple Python IRC bot",
    url="https://github.com/8Banana/BananaBot",
    author="8Banana",
    install_requires=[],
    packages=["bananabot"]
)
