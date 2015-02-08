# -*- coding: utf-8 -*-
from plugins import plugin
import globalv, urllib2,urllib
import time
import datetime
import os
import re
import sys
sys.path.append("/home/py/.python/")
import datetime
class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        arguments=complete.message().split()
        channel=complete.channel()
        msg=0
        perm=0
        timeFrom="00:00"
        hideUrls = False
        userPrint=[]
        print arguments

        extra = ''
        for argument in arguments:
            if re.match('\d{4}-\d{2}-\d{2}', argument):
                extra = argument
                break
            if argument.isdigit():
                extra = argument + '/days/ago'
                break
        return ['PRIVMSG $C$ :http://irc.64digits.com/logs/%s' % extra ]

    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !pastebinLogs module. I return a pastebin URL with the logs of today - [msg].","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!pastebinLogs [offset]"]
