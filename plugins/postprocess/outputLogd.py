# -*- coding: utf-8 -*-
#[11 May 10 11:12] * James * Hi everyone
from plugins import plugin
import globalv
import time
import calendar
import os
import traceback
class pluginClass(plugin):
    def gettype(self):
        return "postprocess"
    def action(self, arguments):
        complete=arguments
        if complete.split()[0]=="PONG":
            return arguments
        try:
            user=globalv.nickname.encode('utf-8')
            channel=complete.split()[1]
            msg=':'.join(complete.split(':')[1:]).strip().encode('utf-8')
            ttime=time.gmtime()
            if os.path.exists(os.path.join("logs","LogFile - "+channel+"-"+str(ttime[0]) + "-" + str(ttime[7]))):
                file=open(os.path.join("logs","LogFile - "+channel+"-"+str(ttime[0]) + "-" + str(ttime[7])),"a")
            else:
                file=open(os.path.join("logs","LogFile - "+channel+"-"+str(ttime[0]) + "-" + str(ttime[7])),"w")
            if msg.split()[0]=="ACTION":
                msg=' '.join(msg.split()[1:])[:-1]
                message="[%(time)d] * %(user)s %(umessage)s" % {"time":time.time(), "user":user,"umessage":msg}
            else:
                message="[%(time)d] <%(user)s> %(umessage)s" % {"time":time.time(), "user":user,"umessage":msg}
            if message!="":
                file.write(message+"\n")
            file.close()
        except Exception as detail:
            print traceback.format_exc()
            print detail
        return arguments
    def describe(self, complete):
        msg=complete.message()
        sender=complete[0].split(' ')
        sender=sender[2]
        return ["PRIVMSG $C$ :I am the logging module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :I log your text so I can use it for nefarious means."]
