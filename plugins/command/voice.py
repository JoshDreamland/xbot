# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import random
from userlevelHandler import getLevel
from securityHandler import isAllowed
import re
class pluginClass(plugin):
    def gettype(self):
        return "command"
    def __level__(self):
        return 100
    def action(self, complete):
        msg=complete.message()
        if isAllowed(complete.userMask())>=getLevel(complete.cmd()[0]):
            users = msg.split()
            n = len(users)
            return ["MODE $C$ +%s %s" % ('v' * n, ' '.join(users))]
        else:
            return ["PRIVMSG $C$ :How about no."]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !kick module","PRIVMSG $C$ :Usage: (Requires Elevated Bot Privileges)","PRIVMSG $C$ :!kick [user]"]
