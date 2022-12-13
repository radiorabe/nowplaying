import configargparse


class Options:
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
            "-b",
            "--saemubox-ip",
            dest="saemubox_ip",
            help="IP address of SAEMUBOX",
            default="",
        )
        # TODO v3 remove this option
        self.__args.add_argument(
            "-m",
            "--icecast-base",
            dest="icecastBase",
            help="Icecast base URL",
            default="http://icecast.example.org:8000/admin/",
        )
        # TODO v3 remove this option
        self.__args.add_argument(
            "--icecast-password", dest="icecastPassword", help="Icecast Password"
        )
        self.__args.add_argument(
            "-i",
            "--icecast",
            action="append",
            help="""Icecast endpoints, allowed multiple times. nowplaying will send metadata updates to each
            of the configured endpoints. Specify complete connection data like username and password in the
            URLs e.g. 'http://source:changeme@icecast.example.org:8000/admin/metadata.xsl?mount=/radio'.""",
            default=[],
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
            help="Current Show URL e.g. 'https://libretime.int.example.org/api/live-info-v2/format/json'",
        )
        # TODO v3 remove this option
        self.__args.add_argument(
            "--input-file",
            dest="inputFile",
            help="XML 'now-playing' input file location, may be disabled by passing an empty string, ie. --input-file=''",
            default="/home/endlosplayer/Eingang/now-playing.xml",
        )
        self.__args.add_argument(
            "--xml-output",
            dest="tickerOutputFile",
            help="ticker XML output format",
            default="/var/www/localhost/htdocs/songticker/0.9.3/current.xml",
        )
        self.__args.add_argument(
            "--api-bind-address",
            dest="apiBindAddress",
            help="Bind address for the API server",
            default="0.0.0.0",
        )
        self.__args.add_argument(
            "--api-port",
            type=int,
            dest="apiPort",
            help="Bind port for the API server",
            default=8080,
        )
        self.__args.add_argument(
            "--api-auth-users",
            dest="apiAuthUsers",
            help="API Auth Users",
            default={"rabe": "rabe"},
        )
        self.__args.add_argument(
            "--instrumentation-otlp-enable",
            type=bool,
            nargs="?",
            const=True,
            dest="otlp_enable",
            help="Enable OpenTelemetry Protocol (OTLP) exporter (default: False)",
            default=False,
            env_var="NOWPLAYING_INSTRUMENTATION_OTLP_ENABLE",
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
