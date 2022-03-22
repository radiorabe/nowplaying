import logging
from typing import Optional
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)


def parse_icecast_url(
    url: str,
) -> tuple[str, Optional[str], Optional[str], Optional[str]]:
    """Parse an Icecast URL into the componets relevant to the :class:`IcecastTrackObserver`.

    Use it to grab the username, password, and mountpoint from the URL.

    >>> parse_icecast_url("http://user:password@localhost:80/?mount=foo.mp3")
    ('http://localhost:80/', 'user', 'password', 'foo.mp3')

    It returns None values for missing parts.

    >>> parse_icecast_url("http://localhost/")
    ('http://localhost:80/', None, None, None)

    It supports https URLs.

    >>> parse_icecast_url("https://localhost/")
    ('https://localhost:443/', None, None, None)

    Args:
        url (str): The Icecast URL to parse.
    Returns:
        Tuple[str, Optional[str], Optional[str], Optional[str]]: The URL, username, password, and mountpoint.
    """
    parsed = urlparse(url)
    port = parsed.port or parsed.scheme == "https" and 443 or 80
    url = parsed._replace(query="", netloc=f"{parsed.hostname}:{port}").geturl()
    username = parsed.username
    password = parsed.password
    mount = None
    try:
        mount = parse_qs(parsed.query)["mount"][0]
    except KeyError:
        logger.warning("Missing mount parameter in URL %s" % url)
    return (url, username, password, mount)
