# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import time
from datetime import datetime, timedelta
import os
import shlex
import re
class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        ttime=time.gmtime()
        current_day = datetime.strptime('%d-%d' % (ttime[0], ttime[7]), '%Y-%j')
        for delta in range(0,3):
            filename = 'LogFile - %s-%s-%d' % (complete.channel(), current_day.strftime('%Y'), int(current_day.strftime('%j')))
            file = open(os.path.join("logs", filename))
            lines=file.readlines()
            lines.reverse()
            print "message=", complete.message()
            try:
                toFind=re.compile(shlex.split(complete.message())[0], re.I)
                toReplace=' '.join(shlex.split(complete.message())[1:])
            except Exception as detail:
                return ["PRIVMSG $C$ :%s"%detail]
            print "s starting: Matching %s"%repr(toFind.pattern)
            print u"and replacing with %s"%repr(toReplace)
            for line in lines:
                m = re.search('\[\d+\] (<\S+>|\* \S+)\s+(.*)', line)
                if m is None:
                    continue
                first_part = m.group(1)
                message = m.group(2)
                if message.startswith(globalv.commandCharacter):
                    continue
                m = re.search(toFind, message)
                if m is None:
                    continue
                message = toFind.sub(toReplace, message)
                line = first_part + ' ' + message
                return ["PRIVMSG $C$ :%s"%line[:600].decode('utf-8')]
            current_day -= timedelta(days=1)

        return ["PRIVMSG $C$ :Could not find %s in today's logs!"%toFind.pattern]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !say module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!say [input]"]
