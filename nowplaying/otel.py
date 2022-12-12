"""OpenTelemetry for nowplaying.

This sets up our logging stack to use OpenTelemetry.
"""

import logging
import os
from datetime import datetime

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    ConsoleLogExporter,
    SimpleLogRecordProcessor,
)
from opentelemetry.sdk.resources import Resource


def _log_formatter(record):  # pragma: no cover
    return f"{datetime.fromtimestamp(record.timestamp/1000000000)} - {record.severity_text[:4]:4} - {record.attributes['source']['name'][11:]:14} - {record.body} - {record.attributes['source']['pathname']}:{record.attributes['source']['lineno']}\n"


class SourceAttributeFilter(logging.Filter):  # pragma: no cover
    """Used on the handler to ensure that some attributes are carried over to otel."""

    def filter(self, record) -> bool:
        record.source = {
            "name": record.name,
            "pathname": os.path.relpath(
                record.pathname, os.path.dirname(os.path.dirname(__file__))
            ),
            "lineno": record.lineno,
        }
        return True


def setup_otel(otlp_enable=False):  # pragma: no cover
    """Configure opentelemetry logging to stdout and collector."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    logger_provider = LoggerProvider(
        resource=Resource.create(
            {
                "service.name": "nowplaying",
            },
        )
    )
    set_logger_provider(logger_provider)

    console_exporter = ConsoleLogExporter(
        formatter=lambda record: _log_formatter(record)
    )
    logger_provider.add_log_record_processor(SimpleLogRecordProcessor(console_exporter))

    if otlp_enable:
        oltp_exporter = OTLPLogExporter(insecure=True)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(oltp_exporter))

    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    handler.addFilter(SourceAttributeFilter())

    root.addHandler(handler)

    logger = logging.getLogger(__name__)
    logger.info("Opentelemetry Configured (OTLP: %s)", otlp_enable)
