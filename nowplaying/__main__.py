"""Entrypoint for nowplaing module.

This module is the entrypoint for the nowplaying module.

You can run it via `python3 -mnowplaying` or after installation using the `nowplaying` command.
"""
from .main import NowPlaying


def main():
    NowPlaying().run()


if __name__ == "__main__":  # pragma: no cover
    main()
