# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import time
class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        msg=complete.message()
        return ["PRIVMSG $C$ :" + repr(globalv.channelUsers[complete.channel()])]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !time module. I return a user's local time.","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!time [user]"]
