from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()


setup(
    name="cazy-parser",
    version="2.0.1",
    description="A way to extract specific information from CAZy",
    long_description=long_description,
    url="https://github.com/rodrigovrgs/cazy-parser",
    author="Rodrigo Honorato",
    author_email="rvhonorato@protonmail.com",
    license="GPL3",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="cazy database datamining",
    packages=find_packages("src"),
    install_requires=required,
    extras_require={},
    package_data={"cazy-parser": []},
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "cazy-parser=cazy_parser.cli:maincli",
        ],
    },
)
