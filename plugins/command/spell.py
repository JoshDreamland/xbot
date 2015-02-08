# -*- coding: utf-8 -*-
from plugins import plugin
from pyaspell import Aspell
import re
class pluginClass(plugin):
    def __init__(self):
        self.a = Aspell(("lang", "en"))

    def gettype(self):
        return "command"

    def action(self, complete):
        words = complete.message().split()
        result = []

        if len(words) == 1:
            suggestions = self.a.suggest(words[0])
            if len(suggestions) == 0:
                return ["PRIVMSG $C$ :No spelling corrections found."]
            else:
                return ["PRIVMSG $C$ :Possible spelling corrections: " + ', '.join(suggestions)]

        for word in words:
            if self.a.check(word):
                result.append(word)
                continue
            p = re.search('(.*)\b(.+)\b(.*)', word)
            if p is None:
                suggestions = self.a.suggest(word)
                if len(suggestions) == 0:
                    result.append('<%s>?' % word)
                else:
                    result.append(self.a.suggest(word)[0])
                continue
            result.append(p.group(1)+self.a.suggest(p.group(2))+p.group(3))

        return ["PRIVMSG $C$ :"+(' '.join(result)).decode('utf-8')]

    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !spell module","PRIVMSG $C$ :I do spell checks!"]
