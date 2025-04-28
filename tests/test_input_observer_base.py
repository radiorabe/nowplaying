from __future__ import annotations

from typing import TYPE_CHECKING

from nowplaying.input.observer import InputObserver

if TYPE_CHECKING:
    from cloudevents.http.event import CloudEvent


class ShuntObserver(InputObserver):
    def handles(self, _: CloudEvent):
        return True

    def event(self, event: CloudEvent): ...

    def handle_id(
        self,
        saemubox_id: int,  # noqa: ARG002
        event: CloudEvent | None = None,  # noqa: ARG002
    ) -> bool:
        return True

    def handle(self, event: CloudEvent | None = None) -> None:  # noqa: ARG002
        self.handle_called = True


def test_init():
    show_url = "http://www.rabe.ch/klangbecken/"
    observer = ShuntObserver(show_url)

    assert observer.current_show_url == show_url


def test_add_track_handler():
    show_url = "http://www.rabe.ch/klangbecken/"
    observer = ShuntObserver(show_url)

    track_handler = object()
    observer.add_track_handler(track_handler)

    assert observer.track_handler == track_handler


def test_update():
    show_url = "http://www.rabe.ch/klangbecken/"
    observer = ShuntObserver(show_url)

    saemubox_id = 1
    observer.update(saemubox_id)

    assert observer.handle_called
