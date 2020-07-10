#!/usr/bin/env python3

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel

class RadioBrowserSkill(CommonPlaySkill):
    def __init__(self):
        super().__init__(name="RadioBrowser")

    def CPS_match_query_phrase(selfself, phrase):
        pass
    
    def CPS_start(self, phrase, data):
        pass

    def initialize(self):
        self.add_event('mycroft.stop', self.stop)


def create_skill():
    return RadioBrowserSkill()
