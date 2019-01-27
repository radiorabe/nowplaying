#! /usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "$Revision$"
# $Id$

import logging
import logging.handlers

from nowplaying import input, misc

logger = logging.getLogger("now-playing")


class InputHandler:
    """Inform all registered input-event observers about an input status.

    This is the subject of the classical observer pattern.
    """

    def __init__(self):
        self.__observers = []
        self.last_input = 1

        self.saemubox = misc.saemubox.SaemuBox()

    def register_observer(self, observer):
        if not isinstance(observer, input.observer.InputObserver):
            raise Exception("Only InputObserver objects can be registered")

        self.__observers.append(observer)

    def remove_observer(self, observer):
        self.__observers.remove(observer)

    def update(self):
        saemubox_id = self.saemubox.get_active_output_id()
        logger.debug("Sämubox id: %i" % saemubox_id)

        if self.last_input != saemubox_id:
            logger.info(
                'Sämubox changed from "%s" to "%s"'
                % (
                    self.saemubox.get_id_as_name(self.last_input),
                    self.saemubox.get_id_as_name(saemubox_id),
                )
            )

        self.last_input = saemubox_id

        for observer in self.__observers:
            logger.debug("Sending update event to observer %s" % observer.__class__)

            try:
                observer.update(saemubox_id)
            except Exception as e:
                logger.error("InputObserver (%s): %s" % (observer.__class__, e))
                logger.exception(e)
