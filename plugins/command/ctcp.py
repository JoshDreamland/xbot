# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        msg=complete.message()
        parts = msg.split()
        destination = parts[0]
        command = parts[1].upper()
        params = (' '.join(parts[2:])).decode('utf-8')
        return ["PRIVMSG %s :\01%s %s\01" % (destination, command, params)]
    def describe(self, complete):
        msg=complete.message()
        sender=complete[0].split(' ')
        sender=sender[2]
        return ["PRIVMSG $C$ :I am the !say module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!say [input]"]
