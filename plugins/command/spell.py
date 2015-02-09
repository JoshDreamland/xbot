# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import aspell
class pluginClass(plugin):
    s = aspell.Speller('lang', 'en')
    def gettype(self):
        return "command"
    def action(self, complete):
        msg = complete.message().decode('utf-8');
        if self.s.check(msg):
            msg = '"' + msg + '" is spelled correctly'
        else:
            suggs = self.s.suggest(msg)
            if len(suggs) > 0:
                msg = ', '.join(suggs)
            else:
                msg = 'No spelling suggestions.';
        return ["PRIVMSG $C$ :" + msg]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !spell module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!spell [word]"]
