from abc import ABC, abstractmethod

import configargparse


class TrackObserver(ABC):
    """Abstract base class for all TrackObservers."""

    name = "TrackObserver"

    class Options(ABC):
        @classmethod
        @abstractmethod
        def args(cls, args: configargparse.ArgParser) -> None:  # pragma: no cover
            pass

    def get_name(self):
        return self.name

    @abstractmethod
    def track_started(self, track):  # pragma: no cover
        pass

    @abstractmethod
    def track_finished(self, track):  # pragma: no cover
        pass
