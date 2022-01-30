import logging
import socket
import sys

from .daemon import NowPlayingDaemon
from .options import Options


class NowPlaying:
    def run(self):
        """Load configuration, initialize environment and start nowplaying daemon."""
        self.options = Options()
        self.options.parse_known_args()

        self.setup_logging()
        socket.setdefaulttimeout(self.options.socketDefaultTimeout)
        self._run_daemon()

    def _run_daemon(self):
        """Start nowplaying daemon."""
        NowPlayingDaemon(self.options).main()

    def setup_logging(self):
        """Configure logging to stdout."""
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        stdout_handler = logging.StreamHandler(sys.stdout)

        stdout_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        stdout_handler.setLevel(logging.INFO)
        if self.options.debug:
            stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(stdout_formatter)

        root.addHandler(stdout_handler)


if __name__ == "__main__":  # pragma: no cover
    NowPlaying().run()
