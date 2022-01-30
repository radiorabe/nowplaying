import socket

from .daemon import NowPlayingDaemon
from .options import Options
from .otel import setup_otel


class NowPlaying:
    def run(self):
        """Load configuration, initialize environment and start nowplaying daemon."""
        self.options = Options()
        self.options.parse_known_args()

        self._setup_otel()
        socket.setdefaulttimeout(self.options.socketDefaultTimeout)
        self._run_daemon()

    def _setup_otel(self):  # pragma: no cover
        if not self.options.debug:
            setup_otel(self.options.otlp_enable)

    def _run_daemon(self):
        """Start nowplaying daemon."""
        NowPlayingDaemon(self.options).main()


if __name__ == "__main__":  # pragma: no cover
    NowPlaying().run()
