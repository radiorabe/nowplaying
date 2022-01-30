from cloudevents.http.event import CloudEvent

from nowplaying.input.observer import InputObserver


class ShuntObserver(InputObserver):
    def handles(self, event: CloudEvent):
        return True

    def event(self, event: CloudEvent):
        return super().event(event)

    def handle_id(self, saemubox_id: int, event: CloudEvent):
        return True

    def handle(self, event: CloudEvent):
        self.handle_called = True
        return super().event(event)


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
