#! /usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "$Revision$"
# $Id$

import logging
import logging.handlers
import select
import socket
import time

logger = logging.getLogger("now-playing")


class SaemuBoxError(Exception):
    """SaemuBox related exception."""

    pass


class SaemuBox:

    output_mapping = {
        1: "Klangbecken",
        2: "Live + Replay",
        3: "Frei",
        4: "Vorproduktion",
        5: "Hörmal",
        6: "Studio Live",
    }

    def __init__(self):
        self.output = ""

        # listening ip adress (all)
        self.bind_ip = "0.0.0.0"

        # listening port
        self.port = 4001

        # allowed sender ip addresses
        self.senders = set(["10.130.225.6", "10.130.225.7"])

        # valid saemubox ids
        self.valid_ids = [str(i) for i in self.output_mapping]

        self._setup_socket()

        # wait for some data to arrive
        time.sleep(0.2)

    def _setup_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.bind_ip, self.port))
            logger.info("SaemuBox: listening on %s:%i." % (self.bind_ip, self.port))
        except socket.error as e:
            self.sock = None
            logger.error("SaemuBox: cannot bind to %s:%i." % (self.bind_ip, self.port))
            raise SaemuBoxError(e.message)

    def __update(self):
        if self.sock is None or (hasattr(self.sock, "_closed") and self.sock._closed):
            logger.warn("SaemuBox: socket closed unexpectedly, retrying...")
            self._setup_socket()

        output = None
        seen_senders = set([])

        # read from socket while there is something to read (non-blocking)
        while select.select([self.sock], [], [], 0)[0]:
            data, addr = self.sock.recvfrom(1024)
            if addr[0] not in self.senders:
                logger.warn("SaemuBox: receiving data from invalid host: %s " % addr[0])
                continue

            ids = data.split()  # several saemubox ids might come in one packet
            if ids:
                if ids[-1] in self.valid_ids:  # only take last id
                    seen_senders.add(addr[0])
                    output = ids[-1]
                else:
                    logger.warn("SaemuBox: received invalid data: %s" % data)

        if output is None:
            logger.error("SaemuBox: could not read current status.")
            output = 0
            raise SaemuBoxError("Cannot read data from SaemuBox")
        elif seen_senders != self.senders:
            for missing_sender in self.senders - seen_senders:
                logger.warn("SaemuBox: missing sender: %s" % missing_sender)

        self.output = int(output)

    def get_active_output_id(self):
        self.__update()
        return self.output

    def get_active_output_name(self):
        self.__update()
        return self.output_mapping[self.output]

    def get_id_as_name(self, number):
        return self.output_mapping[number]


if __name__ == "__main__":
    # Test code
    from random import randint
    import sys

    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)

    sb = SaemuBox()
    localhost = socket.gethostbyname(socket.gethostname())
    sb.senders.add(localhost)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (localhost, 4001)

    sock.sendto(b"\n", addr)
    sock.sendto(b"1", addr)
    sock.sendto(b"gugus", addr)  # invalid
    sock.sendto(b"1\n2\n1\n", addr)

    while True:
        sock.sendto(b"%d" % randint(1, 6), addr)
        sock.sendto(b"\n", addr)
        sock.sendto(b"\n", addr)
        sock.sendto(b" %d \n%d\n" % (randint(1, 6), randint(1, 6)), addr)
        sock.sendto(b"\n", addr)
        logger.info("Current status: %s" % sb.get_active_output_name())
        sock.sendto(b"\n", addr)
        sock.sendto(b"\n", addr)
        sock.sendto(b"%d" % randint(0, 7), addr)  # sometimes invalid
        time.sleep(1)