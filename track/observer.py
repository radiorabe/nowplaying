#! /usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "$Revision$"
# $Id$

import logging
import logging.handlers
import urllib
import urllib2
import datetime
import pytz
import calendar
import uuid
from elementtree.SimpleXMLWriter import XMLWriter

# http://code.google.com/p/pylast/
import pylast

# http://pypi.python.org/pypi/isodate
import isodate

logger = logging.getLogger('now-playing')

class TrackObserver():
    name = 'TrackObserver'

    def get_name(self):
        return self.name

    def track_started(self, track):
        pass

    def track_finished(self, track):
        pass


class ScrobblerTrackObserver(TrackObserver):
    name = 'Audioscrobbler'

    lastfm_api_key    = ""
    lastfm_api_secret = ""

    librefm_api_key    = ""
    librefm_api_secret = ""


    def __init__(self, user, password):
       
        password = pylast.md5(password)

        self.lastfm  = pylast.get_lastfm_network("", "", None, user, password)
        self.librefm = pylast.get_librefm_network("", "", None, user, password)

        self.scrobblers = {'lastfm':  self.lastfm.get_scrobbler('tst', '1.0'),
                           'librefm': self.librefm.get_scrobbler('tst', '1.0')}


    def track_started(self, track):

        if track.has_default_artist() or track.has_default_title():
            logger.error('Default artist or title, skip now-playing scrobble')
            return False

        logger.info('AS now-playing notification for track: %s - %s' %
                        (track.artist, track.title))


        # scrobble to all networks
        #
        # Note that track.get_duration() returns a timedelta object, which
        # could (theoretically) also contain minutes, hours and days, however
        # the track.set_duration() method only accepts seconds, therefore it's
        # safe to read track.get_duration().seconds. Python 2.7 will bring the
        # proper solution with its timedelta.total_seconds() method.
        for k, scrobbler in self.scrobblers.iteritems():
            scrobbler.report_now_playing(track.artist,
                                         track.title,
	                                 track.album, 
			                 str(track.get_duration().seconds),
			                 str(track.track))


    def track_finished(self, track):
        logger.info("Track duration was: %s" % track.get_duration().seconds)

        #if track.get_duration() < datetime.timedelta(seconds=30):
        if track.get_duration().seconds < 30:
            # respecting last.fm minimum song lenght policy of 30 seconds
            logger.info('Track duration is < 30s, skip scrobble submit')
            return False

        if track.has_default_artist() or track.has_default_title():
            logger.error('Default artist or title, skip scrobble submit')
            return False

        logger.info('AS submit for track: %s - %s' %
                       (track.artist, track.title))

        # Get UTC unix timestamp without daylight saving informations
        # http://stackoverflow.com/questions/1077285/how-to-specify-time-zone-utc-when-converting-to-unix-time-python
        timestamp = calendar.timegm(track.starttime.utctimetuple())

        # scrobbling to all networks
        #
        # Note that track.get_duration() returns a timedelta object, which
        # could (theoretically) also contain minutes, hours and days, however
        # the track.set_duration() method only accepts seconds, therefore it's
        # safe to read track.get_duration().seconds. Python 2.7 will bring the
        # proper solution with its timedelta.total_seconds() method.
        for k, scrobbler in self.scrobblers.iteritems():
            scrobbler.scrobble(track.artist,
                               track.title,
                               int(timestamp),
                               'P',
                               '',
                               str(track.get_duration().seconds),
                               track.album,
                               str(track.track))


class IcecastTrackObserver(TrackObserver):
    name = 'Icecast'

    def __init__(self, baseUrl):
        self.baseUrl = baseUrl + '&mode=updinfo&charset=utf-8&song='


    def track_started(self, track):
        logger.info('Updating Icecast Metadata for track: %s - %s' %
                        (track.artist, track.title))

        title = track.title

        if track.has_default_title() and track.has_default_artist():
            logger.info('%s: Track has default info, using show instead' %
                        self.__class__)

            title = track.show.name


        # artist is an unicode string which we have to encode into UTF-8
        # http://bugs.python.org/issue216716
        song_string = urllib.quote_plus('%s - %s' %
                          (track.artist.encode('utf8'),
                           title.encode('utf8')))

        update_url = self.baseUrl + song_string

        logger.info('Icecast Update URL: ' + update_url)

        fp = urllib2.urlopen(update_url)


    def track_finished(self, track):
        return True


class PseudoRssTrackObserver(TrackObserver):
    '''Writes the RSS feed file, which will be consumed by the song-ticker
       on the RaBe website. Unfortunately the ticker expects some broken RSS
       format, therefore we can't use a proper RSS generator such as PyRSS2Gen'''
    name = 'RSS'

    # Crappy non-standard RSS XML string with string replacement patterns
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<rss xmlns:xs="http://www.w3.org/2001/XMLSchema" version="2.0"><title>RaBe Songticker</title><link>http://rabe.ch</link><description>playlist</description><language>de</language><ttl>1</ttl><generator>now-playing</generator><docs>http://blogs.law.harvard.edu/tech/rss</docs><lastBuildDate>%s</lastBuildDate><item><guid>rabe-songticker-%s</guid><title>%s</title><link/><description>%s</description><pubDate>%s</pubDate></item></rss>'


    def __init__(self, rssFilePath):
        self.rssFilePath = rssFilePath     


    def track_started(self, track):
        #Artist and title are unicode strings which we have to encode into UTF-8
        artist    = track.artist.encode('utf8')
        title     = track.title.encode('utf8')

        # Get ISO 8601 date string (2012-04-28T18:00:00+0200)
        starttime = \
          track.starttime.astimezone(pytz.timezone('Europe/Zurich')).isoformat()


        logger.info('Updating RSS file for track: %s - %s' % (artist, title))

        if track.has_default_title():
            if track.has_default_artist():
                logger.info('%s: Track has default info, using show instead' %
                            self.__class__)

                title = track.show.name


            else:
                logger.info('%s: Replacing default title with empty string' %
                            self.__class__)
                title = ''


        # @TODO: Timezone should be configurable
        now = isodate.datetime_isoformat(
                  datetime.datetime.now(pytz.timezone('Europe/Zurich')))


        rssFile = open(self.rssFilePath, 'w')

        # substitue all patterns within the XML with their actual values
        rssFile.write(self.xml % (starttime, now, title, artist, starttime))
        rssFile.close()


    def track_finished(self, track):
        return True


class TickerTrackObserver(TrackObserver):
    '''Writes the new ticker feed file, which will be consumed by the
       song-ticker on the RaBe website. This is the successor of the
       PseudoRssTrackObserver format'''

    name = 'Ticker'


    def __init__(self, ticker_file_path):
        self.ticker_file_path = ticker_file_path


    def track_started(self, track):
        logger.info('Updating Ticker XML file for track: %s - %s' %
            (track.artist, track.title))

        now = isodate.datetime_isoformat(
                  datetime.datetime.now(pytz.timezone('Europe/Zurich')))


        xml = XMLWriter(self.ticker_file_path, 'utf-8')

        xml.declaration()
        ticker = xml.start('ticker',
                           {'xmlns':       "http://rabe.ch/schema/ticker.xsd",
                            'xmlns:xlink': "http://www.w3.org/1999/xlink"})


        xml.element('identifier', 'ticker-%s' % uuid.uuid4())
        xml.element('creator', 'now-playing daemon')
        xml.element('date', now)

        xml.start('show', id=track.show.uuid)
        xml.element('name', track.show.name)
        xml.element('link', track.show.url, 
                    {'xlink:type': 'simple',
                     'xlink:href': track.show.url,
                     'xlink:show': 'replace'})

        # Get ISO 8601 date string (2012-04-28T18:00:00+0200)
        xml.element('startTime', isodate.datetime_isoformat(
            track.show.starttime.astimezone(pytz.timezone('Europe/Zurich'))))

        # Get ISO 8601 date string (2012-04-28T18:00:00+0200)
        xml.element('endTime', isodate.datetime_isoformat(
            track.show.endtime.astimezone(pytz.timezone('Europe/Zurich'))))

        xml.end()


        xml.start('track', id=track.uuid)
        xml.element('show', track.show.name, ref=track.show.uuid)
        xml.element('artist', track.artist)
        xml.element('title', track.title)

        # Get ISO 8601 date string (2012-04-28T18:00:00+0200)
        xml.element('startTime', isodate.datetime_isoformat(
            track.starttime.astimezone(pytz.timezone('Europe/Zurich'))))

        # Get ISO 8601 date string (2012-04-28T18:00:00+0200)
        xml.element('endTime', isodate.datetime_isoformat(
            track.endtime.astimezone(pytz.timezone('Europe/Zurich'))))

        xml.end()

        xml.close(ticker)


    def track_finished(self, track):
        return True


class DabAudioCompanionTrackObserver(TrackObserver):
    name = 'DAB+ Audio Companion'

    def __init__(self, baseUrl):
        self.baseUrl = baseUrl + '/api/setDLS?dls='      


    def track_started(self, track):
        logger.info('Updating DAB+ DLS for track: %s - %s' %
                        (track.artist, track.title))

        title = track.title

        if track.has_default_title() and track.has_default_artist():
            logger.info('%s: Track has default info, using show instead' %
                        self.__class__)

            title = track.show.name


        # artist is an unicode string which we have to encode into UTF-8
        # http://bugs.python.org/issue216716
        song_string = urllib.quote_plus('%s - %s' %
                          (track.artist.encode('utf8'),
                           title.encode('utf8')))

        update_url = self.baseUrl + song_string

        logger.info('DAB+ Audio Companion URL: ' + update_url)

        fp = urllib2.urlopen(update_url)


    def track_finished(self, track):
        return True
