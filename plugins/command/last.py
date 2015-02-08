# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import time
import re
import os
import datetime

class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        msg=str(complete.message()).strip()
        ttime=time.gmtime()
        result=""
        year=time.gmtime()[0]
        day=time.gmtime()[7]
        ignoreControlCharacters=True
        controlCharacters=['\x02', '\x1F', '\x16', '\x0F', '\x03']
        is_re = re.search('-r\s+(.+)', msg)
        if is_re:
            try:
                regex = re.compile(is_re.group(1))
            except:
                return ["PRIVMSG $C$ :Regex contains syntax error!"]

        for letter in msg:
            if letter in controlCharacters:
                ignoreControlCharacters=False
        while not result:
            if not os.path.exists(os.path.join("logs","LogFile - "+complete.channel()+"-"+str(year) + "-" + str(day))):
                return ["PRIVMSG $C$ :No matches!"]
            with open(os.path.join("logs","LogFile - "+complete.channel()+"-"+str(year) + "-" + str(day))) as file:
                text=file.read()
            text=text.split('\n')
            for line in text:
                oline=line
                if ignoreControlCharacters:
                    line=re.sub("\x03\d*(,\d*)?","",line)
                    line=line.translate(None,''.join(controlCharacters))
                m = re.search('^\[(\d+?)\] (.+)',line)
                if m is None:
                    continue
                line = m.group(2)
                if '!last' in line or '| last' in line or 'chain last' in line or '&& last' in line:
                    continue

                if (is_re and regex.search(line, re.I)) or line.lower().find(msg.lower())!=-1:
                    if line.strip().startswith(globalv.commandCharacter)==False:
                        result=oline

            day-=1
            if day==0:
                year-=1
                day=365

        timestamp = int(re.search('\[(\d+)\]', result).group(1))
        delta = time.time() - timestamp
        if delta < 60:
            delta = "%d seconds ago" % delta if delta != 1 else "1 second ago"
        elif delta < 3600:
            minutes = delta / 60
            delta = "%d minutes ago" % (minutes) if minutes != 1 else "1 minute ago"
        elif delta < 24 * 3600:
            hours = delta / 3600
            delta = "%d hours ago" % (hours) if hours != 1 else "1 hour ago"
        else:
            hours = delta / 3600
            days = hours / 24
            hours = hours % 24
            delta = "%d day%s and %d hour%s ago" % (days, "s" if days != 1 else "", hours, "s" if hours != 1 else "")
        result = re.sub("\[(\d+)\]","[%s]" % delta, result)

        return ["PRIVMSG $C$ :"+result]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !last module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!last [phrase]"]
