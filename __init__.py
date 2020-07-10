#!/usr/bin/env python3
import re
import json
import inflect
from mycroft import intent_file_handler

from pyradios import RadioBrowser
from word2number import w2n

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from mycroft.util.log import LOG


def match_station_name(phrase):
    """Takes the user utterance and attempts to match a specific station

    :param phrase: User utterance
    :type phrase: str

    :return: A tuple containing the original phrase, the CPS.MatchLevel,
    and a dictionary containing the resolved stream URL.
    :rtype: tuple
    """
    numbers_regex = r"\b(one|two|three|four|five|six|seven|eight|nine)\b"
    try:
        rb = RadioBrowser()
    except Exception as e:
        LOG.exception("Failed to load pyradios" + repr(e))
    LOG.info(f"Searching for {phrase}")
    results = rb.search(name=phrase)
    parsed = json.loads(json.dumps(results))

    if len(parsed) > 0:
        # If an exatch match has been found return.
        LOG.info(f"Found {parsed[0]['name']} ({parsed[0]['url_resolved']})")
        return phrase, CPSMatchLevel.EXACT, {"url": parsed[0]["url_resolved"]}
    elif re.search(" [0-9]+ ", phrase):
        # If no match has been found, replace any digits (1,2,3) with text
        # (one, two, three) and repeat search.
        num = re.findall("[0-9]+", phrase)
        inf_eng = inflect.engine()
        for number in num:
            phrase = phrase.replace(num, inf_eng.number_to_words(number))
        match_station_name(phrase)
    elif re.search(numbers_regex, phrase):
        # As above but reversed: change strings to ints and repeat search.
        num = re.findall(numbers_regex, phrase)
        for number in num:
            phrase = phrase.replace(number, str(w2n.word_to_num(number)))
        match_station_name(phrase)
    else:
        return None


def match_genre(phrase):
    """Takes the user utterance and attempts to match a genre of station,
    returning the most popular of that genre.

    :param phrase: User utterance
    :type phrase: str

    :return: A tuple containing the original phrase, the CPS.MatchLevel,
    and a dictionary containing the resolved stream URL.
    :rtype: tuple
    """
    # Strip 'a' and 'station' from phrases like 'Play a jazz station.'.
    stripped_phrase = phrase.lower().replace("a ", "").replace(" station", "")
    try:
        rb = RadioBrowser()
    except Exception as e:
        LOG.exception("Failed to load pyradios" + repr(e))
    LOG.info(f"Searching for a {stripped_phrase} station")
    results = rb.search(tag=stripped_phrase, order="votes")
    parsed = json.loads(json.dumps(results))

    if len(parsed) > 0:
        LOG.info(f"Found {parsed[0]['name']} ({parsed[0]['url_resolved']})")
        return phrase, CPSMatchLevel.EXACT, {"url": parsed[0]["url_resolved"]}
    else:
        match_station_name(phrase)


class RadioBrowserSkill(CommonPlaySkill):
    def __init__(self):
        super().__init__(name="RadioBrowser")

    def CPS_match_query_phrase(self, phrase):
        search_phrase = phrase.lower()

        if "a " and " station" in search_phrase:
            return match_genre(search_phrase)
        else:
            return match_station_name(phrase)

    def CPS_start(self, phrase, data):
        if self.audioservice.is_playing:
            self.audioservice.stop()
        url = data["url"]
        LOG.info(f"Playing from {url}")
        self.audioservice.play(url)

    def handle_intent(self, message, type):
        # Generic method for handling intents
        matched_station = match_station_name(message.data[type])
        LOG.info(f"Playing from {matched_station[2]['url']}")
        self.CPS_play(matched_station[2]["url"])

    @intent_file_handler("radio.station.intent")
    def handle_radio_station(self, message):
        # Handles requests for specific stations
        self.handle_intent(message, "station")

    @intent_file_handler("radio.genre.intent")
    def handle_radio_genre(self, message):
        # Handles requests for genres
        self.handle_intent(message, "genre")

    def initialize(self):
        self.add_event("mycroft.stop", self.stop)


def create_skill():
    return RadioBrowserSkill()
