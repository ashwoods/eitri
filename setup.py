#!/usr/bin/env python
# type: ignore
"""
eitri: cli wrapper for docker-compose based toolkit environments
"""
from setuptools import setup, find_packages


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


TEST_DEPS = parse_requirements("req-test.txt")
INSTALL_DEPS = parse_requirements("req-install.txt")
EXTRAS = {
    "test": TEST_DEPS,
}


setup(
    name="eitri",
    version="0.1.0.dev",
    author="Ashley Camba Garrido",
    author_email="ashwoods@gmail.com",
    url="https://github.com/ashwoods/eitri",
    description="Manage docker-compose based toolkits",
    long_description=__doc__,
    packages=find_packages(exclude=("tests", "tests.*")),
    entry_points={"console_scripts": ["eitri = eitri:cli"]},
    # PEP 561
    package_data={"eitri": ["py.typed"]},
    zip_safe=False,
    license="MIT",
    tests_require=TEST_DEPS,
    extras_require=EXTRAS,
    install_requires=INSTALL_DEPS,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)