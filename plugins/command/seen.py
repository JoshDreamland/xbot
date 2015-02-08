# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import time
import datetime
import os
import fnmatch
import re

class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        msg=complete.message().strip()
        sender=complete.channel()
        ttime=time.gmtime()
        result=""
        year=time.gmtime()[0]
        day=time.gmtime()[7]
        while not result:
            if not os.path.exists(os.path.join("logs","LogFile - "+sender+"-"+str(year) + "-" + str(day))):
                return ["PRIVMSG $C$ :No matches!"]
            with open(os.path.join("logs","LogFile - "+sender+"-"+str(year) + "-" + str(day))) as file:
                text=file.read()
            text=text.split('\n')
            text.reverse()
            for line in text:
                nick = None
                for regex in ['\* (\S+)', '<(\S+)>', '(?:=-=|<--\||\|<--|-->\|) ([^\s!~]+)', '=-= \S+ kicked (\S+):', '=-= \S+ is now known as (\S+)']:
                    m = re.search('^\[\d+\] %s' % regex, line)
                    if m is None:
                        continue
                    if fnmatch.fnmatch(m.group(1).lower(), msg.lower()):
                        timestamp = int(re.search('\[(\d+)\]', line).group(1))
                        delta = int(time.time() - timestamp)
                        if delta > 0.5:
                            result = line
                            break
                if result:
                    break
            day-=1
            if day==0:
                year-=1
                day=365

        timestamp = int(re.search('\[(\d+)\]', result).group(1))
        delta = int(time.time() - timestamp)
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
        msg=complete.message()
        sender=complete[0].split(' ')
        sender=sender[2]
        return ["PRIVMSG $C$ :I am the !seen module. I find out when the last time a user was seen was.","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!seen [user]"]
