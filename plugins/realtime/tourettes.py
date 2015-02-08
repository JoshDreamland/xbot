# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import random
class pluginClass(plugin):
    def __init__(self):
        self.counter = 0
    def gettype(self):
        return "realtime"
    def action(self, complete):
        if self.counter > 0:
            self.counter -= 1
        if self.counter == 0 and random.randint(0,40) == 0:
            msg = random.choice(['CUNT','GODDAMN','DICKS','SON OF A BITCH', 'ASSHOLE','MOTHERFUCKER','VAGINAS','ASS','FUUUUCK','FUCK'])
            self.counter = random.randint(3,10)
            return ["PRIVMSG $C$ :%s!" % msg]
        return []
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !say module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!say [input]"]
