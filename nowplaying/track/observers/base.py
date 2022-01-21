from abc import ABC, abstractmethod


class TrackObserver(ABC):
    """Abstract base class for all TrackObservers."""

    name = "TrackObserver"

    def get_name(self):
        return self.name

    @abstractmethod
    def track_started(self, track):  # pragma: no cover
        pass

    @abstractmethod
    def track_finished(self, track):  # pragma: no cover
        pass
