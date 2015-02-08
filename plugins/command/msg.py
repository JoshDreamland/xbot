# -*- coding: utf-8 -*-
from plugins import plugin
import globalv

from datetime import datetime

class pluginClass(plugin):
    def __init__(self):
        self.history = {}
    def gettype(self):
        return "command"
    def action(self, complete):
        tokens = complete.message().split()
        msg=' '.join(tokens[1:])
        source=complete.user()
        destination=tokens[0].lower()
        yeahNo=["chanserv","nickserv","memoserv",globalv.nickname.lower()]
        if destination in yeahNo: return

        if destination not in self.history:
            self.history[destination] = []

        now = datetime.now()

        if destination == '-who':
            destination=complete.channel()
            target = complete.channel() if len(tokens)==1 else tokens[1]
            result = set()
            if target.lower() in self.history:
                history = self.history[target.lower()]
                for item in history:
                    delta_time = (now-item['timestamp'])
                    delta_time_seconds = delta_time.seconds + delta_time.days * 24 * 3600
                    if delta_time_seconds < 2.3 * 3600:
                        result.add(item['source'])
            return ["PRIVMSG "+destination+" :The following people made me say stuff to %s in the last few hours: %s" % (target, ', '.join(list(result)))]

        history = self.history[destination]

        doAdd = True
        for i, item in enumerate(history):
            if item['source'] == source:
                delta = now - item['timestamp']
                if delta.seconds < 15*60:
                    doAdd = False
                    history[i] = {
                        'timestamp': now,
                        'source': source
                    }

        if doAdd:
            history.append({
                'timestamp': datetime.now(),
                'source': source,
            })

        if len(history) > 100:
            self.history[destination] = history[1:]

        return ["PRIVMSG "+destination+" :"+msg]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !say module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!say [input]"]
