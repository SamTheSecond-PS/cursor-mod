from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="cursorx",
    version="2.0",
    packages=find_packages(),
    install_requires=[],
    author="Sarvesh",
    long_description=Path("README.md").read_text(),
    description="Lightweight text navigation cursor"
)
