from unittest.mock import Mock

from nowplaying.input.handler import InputHandler


def test_register_observer():
    input_handler = InputHandler()
    mock_observer = Mock(name="observer")

    input_handler.register_observer(mock_observer)

    assert mock_observer in input_handler._observers


def test_remove_observer():
    input_handler = InputHandler()
    mock_observer = Mock(name="observer")

    input_handler.register_observer(mock_observer)
    input_handler.remove_observer(mock_observer)

    assert mock_observer not in input_handler._observers


def test_update():
    input_handler = InputHandler()
    mock_observer = Mock(name="observer")

    input_handler.register_observer(mock_observer)
    input_handler.update(1)

    mock_observer.update.assert_called_once_with(1)
