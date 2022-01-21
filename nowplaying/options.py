import configargparse


class Options(object):
    """Contain all hardcoded and loaded from configargparse options."""

    """How many seconds the main daemon loop sleeps."""
    sleepSeconds = 1

    """Default socket of 2 minutes, to prevent endless hangs on HTTP requests."""
    socketDefaultTimeout = 120

    def __init__(self):
        """Configure configargparse."""
        self.__args = configargparse.ArgParser(
            default_config_files=["/etc/nowplaying/conf.d/*.conf", "~/.nowplayingrc"]
        )
        self.__args.add_argument(
            "-m",
            "--icecast-base",
            dest="icecastBase",
            help="Icecast base URL",
            default="http://stream-master.audio.int.rabe.ch:8000/admin/",
        )
        self.__args.add_argument(
            "--icecast-password", dest="icecastPassword", help="Icecast Password"
        )
        self.__args.add_argument(
            "-i",
            "--icecast",
            action="append",
            help="Icecast base URL, allowed multiple times",
            default=[
                "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-hd.mp3",
                "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-high.mp3",
                "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-mid.mp3",
                "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-low.mp3",
                "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-ultra-low.mp3",
                "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-high.opus",
                "http://stream-master.audio.int.rabe.ch:8000/admin/metadata.xsl?mount=/livestream/rabe-low.opus",
            ],
        )
        self.__args.add_argument(
            "-d",
            "--dab",
            action="append",
            help="DAB audio companion base URL, allowed multiple times (ie. http://dab.example.org:8080)",
            default=[],
        )
        # TODO v3 remove when stable
        self.__args.add_argument(
            "--dab-send-dls",
            type=bool,
            nargs="?",
            dest="dab_send_dls",
            help="Send artist/title to DAB companions dls endpoint (default: True)",
            default=True,
        )
        self.__args.add_argument(
            "-s",
            "--show",
            dest="currentShowUrl",
            help="Current Show URL",
            default="https://airtime.service.int.rabe.ch/api/live-info-v2/format/json",
        )
        self.__args.add_argument(
            "--input-file",
            dest="inputFile",
            help="XML 'now-playing' input file location",
            default="/home/endlosplayer/Eingang/now-playing.xml",
        )
        self.__args.add_argument(
            "--xml-output",
            dest="tickerOutputFile",
            help="ticker XML output format",
            default="/var/www/localhost/htdocs/songticker/0.9.3/current.xml",
        )
        self.__args.add_argument(
            "--debug",
            type=bool,
            nargs="?",
            const=True,
            dest="debug",
            help="Show debug messages",
            default=False,
        )

    def parse_known_args(self):
        """Parse known args with configargparse."""
        self.__args.parse_known_args(namespace=self)
