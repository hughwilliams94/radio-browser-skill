#!/usr/bin/env python3

import re
import json
import inflect

from pyradios import RadioBrowser
from word2number import w2n

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from mycroft.util.log import LOG


def match_station_name(phrase):
    try:
        rb = RadioBrowser()
    except Exception as e:
        LOG.exception('Failed to load pyradios' + repr(e))
    LOG.info(f"Searching for {phrase}")
    results = rb.search(name=phrase)
    parsed_results = json.loads(json.dumps(results))

    if len(parsed_results) > 0:
        LOG.info(f"Found {parsed_results[0]['name']} URL: {parsed_results[0]['url_resolved']}")
        return phrase, CPSMatchLevel.EXACT, {"url": parsed_results[0]['url_resolved']}
    elif re.search(' [0-9]+ ', phrase):
        # Replace any digits (1,2,3) with text (one,two,three) and repeat search.
        num = re.findall('[0-9]+', phrase)
        inf_eng = inflect.engine()
        for number in num:
            phrase = phrase.replace(num, inf_eng.number_to_words(number))
        match_station_name(phrase)
    elif re.search(r'\b(one|two|three|four|five|six| seven|eight|nine)\b', phrase):
        # As above but reversed: change strings to ints and repeat search.
        num = re.findall(r'\b(one|two|three|four|five|six| seven|eight|nine)\b', phrase)
        for number in num:
            phrase = phrase.replace(number, str(w2n.word_to_num(number)))
        match_station_name(phrase)
    else:
        return None


def match_genre(phrase):
    # Strip 'a' and 'station' from phrases like 'Play a jazz station.' to get genre.
    stripped_phrase = phrase.lower().replace('a ', '').replace(' station', '')
    try:
        rb = RadioBrowser()
    except Exception as e:
        LOG.exception('Failed to load pyradios' + repr(e))
    LOG.info(f"Searching for a {stripped_phrase} station")
    results = rb.search(tag=stripped_phrase, order="votes")
    parsed_results = json.loads(json.dumps(results))

    if len(parsed_results) > 0:
        LOG.info(f"Found {parsed_results[0]['name']} URL: {parsed_results[0]['url_resolved']}")
        return phrase, CPSMatchLevel.EXACT, {"url": parsed_results[0]['url_resolved']}
    else:
        match_station_name(phrase)


class RadioBrowserSkill(CommonPlaySkill):
    def __init__(self):
        super().__init__(name="RadioBrowser")

    def CPS_match_query_phrase(selfself, phrase):
        search_phrase = phrase.lower()

        if "a " and " station" in search_phrase

            return match_genre(search_phrase)
        else:
            return match_station_name(phrase)

    def CPS_start(self, phrase, data):
        pass

    def initialize(self):
        self.add_event('mycroft.stop', self.stop)


def create_skill():
    return RadioBrowserSkill()
