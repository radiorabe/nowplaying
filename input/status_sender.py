#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import select
import socket

import input.observer

logger = logging.getLogger("now-playing")


class StatusSender(input.observer.InputObserver):
    """Observer that opens a TCP port and sends the current Saemubox ID to all connected clients.

    The sent message is exacly one byte long, and contains nothing more than
    the Saemubox ID.

    To receive the Saemubox status do the following:
    >>> import socket
    >>> sock = socket.socket()
    >>> sock.connect((SERVER_IP, PORT))
    >>> current_id = sock.recv(1)[0]

    Use select/selector for asynchronous processing.
    """

    def __init__(self, bind_ip="0.0.0.0", port=9999):
        self.clients = []
        self.current_saemubox_id = None
        self.bind_ip = bind_ip
        self.port = port
        self.setup_socket()

    def setup_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.bind_ip, self.port))
            self.sock.listen(5)
            logger.info("StatusSender: bound to %s:%i." % (self.bind_ip, self.port))
        except socket.error:
            self.sock = None
            logger.error(
                "StatusSender: cannot bind to %s:%i." % (self.bind_ip, self.port)
            )

    def update(self, saemubox_id):  # noqa ignore=C901
        # gets called once a second
        # TODO: refactor for less complexity re noqa above
        if self.sock is None:
            self.setup_socket()

        if saemubox_id != self.current_saemubox_id:
            self.current_saemubox_id = saemubox_id
            logger.info(
                "Sending new Saemubox status (%i) to %i clients."
                % (saemubox_id, len(self.clients))
            )
            for client in self.clients:
                try:
                    client.sendall(bytearray([saemubox_id]))
                except socket.error:
                    logger.warn("Connection closed.")
                    client.close()
                    self.clients.remove(client)

        # Poll server socket (for new client connections) and clients (for disconnects)
        reads, _, _ = select.select([self.sock] + self.clients, [], [], 0)
        if self.sock in reads:
            try:
                (client, addr) = self.sock.accept()
                logger.info("Accepted connection from %s:%i." % addr)
                self.clients.append(client)
                try:
                    client.sendall(bytearray([saemubox_id]))
                except socket.error:
                    logger.warn("Connection closed.")
                    client.close()
                    self.clients.remove(client)
            except socket.error:
                logger.error("Cannot accept client.")

        for client in set(self.clients) & set(reads):
            res = client.recv(1)
            if len(res) == 0:
                logger.info("Connection closed.")
                client.close()
                self.clients.remove(client)
            else:
                logger.warn("Got unexpected data from %s:%i." % client.getpeername())


if __name__ == "__main__":
    import time
    import random
    import sys

    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)
    s = StatusSender()
    while True:
        s.update(random.randint(1, 6))
        time.sleep(1)
