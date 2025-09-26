"""Options for Nowplaying."""

from __future__ import annotations

from typing import Self

import configargparse  # type: ignore[import-untyped]

from nowplaying.track.observers.dab_audio_companion import (
    DabAudioCompanionTrackObserver,
)
from nowplaying.track.observers.icecast import IcecastTrackObserver
from nowplaying.track.observers.smc_ftp import SmcFtpTrackObserver
from nowplaying.track.observers.ticker import TickerTrackObserver


class Options:
    """Contain all hardcoded and loaded from configargparse options."""

    """How many seconds the main daemon loop sleeps."""
    sleep_seconds = 1

    """Default socket of 2 minutes, to prevent endless hangs on HTTP requests."""
    socket_default_timeout = 120

    def __init__(self: Self) -> None:
        """Configure configargparse."""
        self.__args = configargparse.ArgParser(
            default_config_files=["/etc/nowplaying/conf.d/*.conf", "~/.nowplayingrc"],
        )
        # TODO(hairmare): v3 remove this option
        # https://github.com/radiorabe/nowplaying/issues/179
        self.saemubox_ip: str | None = None
        self.__args.add_argument(
            "-b",
            "--saemubox-ip",
            dest="saemubox_ip",
            help="IP address of SAEMUBOX",
            default="",
        )
        # TODO(hairmare): v3 remove this option
        # https://github.com/radiorabe/nowplaying/issues/179
        self.check_saemubox_sender: bool = True
        self.__args.add_argument(
            "--check-saemubox-sender",
            dest="check_saemubox_sender",
            help="Check SRC SAEMUBOX IP",
            default=True,
        )

        self.icecast: list[str] = []
        self.icecast_password: str = ""
        IcecastTrackObserver.Options.args(self.__args)

        self.dab: list[str] = []
        self.dab_send_dls: bool = False
        DabAudioCompanionTrackObserver.Options.args(self.__args)

        self.dab_smc: bool = False
        self.dab_smc_ftp_hostname: str = ""
        self.dab_smc_ftp_username: str = ""
        self.dab_smc_ftp_password: str = ""
        SmcFtpTrackObserver.Options.args(self.__args)

        self.ticker_output_file: str = ""
        TickerTrackObserver.Options.args(self.__args)

        self.current_show_url: str = ""
        self.__args.add_argument(
            "-s",
            "--show",
            dest="current_show_url",
            help="Current Show URL e.g. 'https://libretime.int.example.org/api/live-info-v2/format/json'",
        )
        # TODO(hairmare): v3 remove this option
        # https://github.com/radiorabe/nowplaying/issues/179
        self.input_file: str = "/home/endlosplayer/Eingang/now-playing.xml"
        self.__args.add_argument(
            "--input-file",
            dest="input_file",
            help=(
                "XML 'now-playing' input file location, "
                "disable input by passing empty string, ie. --input-file=''"
            ),
            default="/home/endlosplayer/Eingang/now-playing.xml",
        )
        self.api_bind_address: str = "127.0.0.1"
        self.__args.add_argument(
            "--api-bind-address",
            dest="api_bind_address",
            help="Bind address for the API server",
            default="127.0.0.1",
        )
        self.api_port: int = 8080
        self.__args.add_argument(
            "--api-port",
            type=int,
            dest="api_port",
            help="Bind port for the API server",
            default=8080,
        )
        self.api_auth_users: dict[str, str] = {}
        self.__args.add_argument(
            "--api-auth-users",
            dest="api_auth_users",
            help="API Auth Users",
            default={"rabe": "rabe"},
        )
        self.otlp_enable: bool = False
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
        self.debug: bool = False
        self.__args.add_argument(
            "--debug",
            type=bool,
            nargs="?",
            const=True,
            dest="debug",
            help="Show debug messages",
            default=False,
        )

    def parse_known_args(self: Self) -> None:
        """Parse known args with configargparse."""
        self.__args.parse_known_args(namespace=self)
