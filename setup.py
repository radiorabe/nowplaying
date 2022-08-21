"""Set up nowplaying."""

from setuptools import find_packages, setup

with open("requirements.txt") as file:
    requirements = file.read().splitlines()


setup(
    name="rabe-nowplaying",
    description="Now Playing RaBe Songticker",
    url="http://github.com/radiorabe/nowplaying",
    author="RaBe IT-Reaktion",
    author_email="it@rabe.ch",
    license="AGPL-3",
    setuptools_git_versioning={"enabled": True},
    setup_requires=["setuptools-git-versioning"],
    install_requires=requirements,
    packages=find_packages(exclude=("tests",)),
    entry_points={"console_scripts": ["nowplaying=nowplaying.__main__:main"]},
    zip_safe=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
)
