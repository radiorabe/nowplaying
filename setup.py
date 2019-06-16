from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name="nowplaying",
    description="Now Playing RaBe Songticker",
    url="http://github.com/radiorabe/nowplaying",
    author="RaBe IT-Reaktion",
    author_email="it@rabe.ch",
    license="AGPL-3",
    install_requires=requirements,
    packages=[
        "nowplaying",
        "nowplaying.misc",
        "nowplaying.input",
        "nowplaying.track",
        "nowplaying.show",
    ],
    entry_points={"console_scripts": ["now-playing=nowplaying.cli:main"]},
    zip_safe=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: AGPL License",
    ],
)
