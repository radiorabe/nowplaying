"""Abstract base for TrackObservers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self, TypeVar

if TYPE_CHECKING:  # pragma: no cover
    import configargparse  # type: ignore[import-untyped]

    from nowplaying.track.track import Track

TTrackObserverOptions = TypeVar("TTrackObserverOptions", bound="TrackObserver.Options")


class TrackObserver(ABC):
    """Abstract base class for all TrackObservers."""

    name = "TrackObserver"

    class Options(ABC):
        """Abstract base class for add TrackObserver.Options."""

        @classmethod
        @abstractmethod
        def args(
            cls: type[TTrackObserverOptions],
            args: configargparse.ArgParser,
        ) -> None:  # pragma: no cover
            """Get args for Options."""

    def get_name(self: Self) -> str:
        """Get name."""
        return self.name

    @abstractmethod
    def track_started(self: Self, track: Track) -> None:  # pragma: no cover
        """Track started."""

    @abstractmethod
    def track_finished(self: Self, track: Track) -> None:  # pragma: no cover
        """Track finished."""
