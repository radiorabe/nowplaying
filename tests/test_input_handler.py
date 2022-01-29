from queue import Queue

from cloudevents.http.event import CloudEvent

from nowplaying.input.handler import InputHandler
from nowplaying.input.observer import InputObserver


class ShuntInputObserver(InputObserver):
    def __init__(self):
        super().__init__(current_show_url="https://example.org")
        self.event_queue = Queue()
        self.update_call = None

    def update(self, saemubox_id: int, event: CloudEvent = None):
        self.update_call = (saemubox_id, event)

    def handles(self, event: CloudEvent) -> bool:
        return super().handles(event)

    def event(self, event: CloudEvent):
        return super().event(event)

    def handle_id(self, saemubox_id: int, event: CloudEvent = None):
        return super().handle_id(saemubox_id, event=event)

    def handle(self, event: CloudEvent = None):
        return super().handle(event)


def test_register_observer():
    """Test the register_observer function."""
    handler = InputHandler()
    observer = ShuntInputObserver()
    handler.register_observer(observer)
    assert observer in handler._observers


def test_remove_observer():
    """Test the remove_observer function."""
    handler = InputHandler()
    observer = ShuntInputObserver()
    handler.register_observer(observer)
    handler.remove_observer(observer)
    assert observer not in handler._observers


def test_update():
    """Test the update function."""
    handler = InputHandler()
    observer = ShuntInputObserver()
    handler.register_observer(observer)

    event = CloudEvent(
        attributes={
            "specversion": "1.0",
            "type": "ch.rabe.api.events.track.v1.trackStarted",
            "source": "https://github.com/radiorabe/nowplaying",
            "id": "my-id",
            "datacontenttype": "application/json",
        },
        data={"item.artist": "Test", "item.title": "Test"},
    )
    handler.update(1, event)
    assert observer.update_call == (1, event)