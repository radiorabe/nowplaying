"""Nowplaying entrypoint."""

import socket
from typing import Self

from .daemon import NowPlayingDaemon
from .options import Options
from .otel import setup_otel


class NowPlaying:
    """Nowplaying main class."""

    def run(self: Self) -> None:
        """Load configuration, initialize environment and start nowplaying daemon."""
        self.options = Options()
        self.options.parse_known_args()

        self._setup_otel()
        socket.setdefaulttimeout(self.options.socket_default_timeout)
        self._run_daemon()

    def _setup_otel(self: Self) -> None:  # pragma: no cover
        if not self.options.debug:
            setup_otel(otlp_enable=self.options.otlp_enable)

    def _run_daemon(self: Self) -> None:
        """Start nowplaying daemon."""
        NowPlayingDaemon(self.options).main()


if __name__ == "__main__":  # pragma: no cover
    NowPlaying().run()
