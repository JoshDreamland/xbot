# -*- coding: utf-8 -*-
#[11 May 10 11:12] * James * Hi everyone
from plugins import plugin
import globalv
import time
import calendar
import os
import settingsHandler
class pluginClass(plugin):
    def gettype(self):
        return "realtime"
    def __init_db_tables__(self, name):
        settingsHandler.newTable("logd","ignore")
    def action(self, arguments):

        ignores=[x[0].lower() for x in settingsHandler.readSettingRaw("logd","ignore")]
        if arguments.channel().lower() in ignores or arguments.user().lower() in ignores:
            print "Channel or User Ignored"
            return [""]
        complete=arguments.complete()[1:].split(' :',1)
        if len(complete)>1:
            msg=complete[1]
        else:
            msg=""
            if len(complete[0].split())<2:
                print "Message Not Long Enough, exiting"
                return [""]
        try:
            sender=complete[0].split(' ')
            channel=arguments.channel()
            userMask=arguments.userMask()
            user=arguments.user()
            msgType=sender[1]
            ttime=time.gmtime()
            message=""
            if not os.path.exists("logs"):
                os.makedirs("logs")
            if os.path.exists(os.path.join("logs","LogFile - "+channel+"-"+str(ttime[0]) + "-" + str(ttime[7]))):
                file=open(os.path.join("logs","LogFile - "+channel.lower()+"-"+str(ttime[0]) + "-" + str(ttime[7])),"a")
            else:
                file=open(os.path.join("logs","LogFile - "+channel.lower()+"-"+str(ttime[0]) + "-" + str(ttime[7])),"w")
            if msgType=="PRIVMSG":
                if msg.split()[0]=="ACTION":
                    msg=' '.join(msg.split()[1:])[:-1]
                    message="[%(time)d] * %(user)s %(umessage)s" % {"time":time.time(), "user":user,"umessage":msg}
                else:
                    message="[%(time)d] <%(user)s> %(umessage)s" % {"time":time.time(), "user":user,"umessage":msg}
            if msgType=="JOIN":
                message="[%(time)d] -->| %(user)s has joined" % {"time":time.time(), "user":userMask}
            if msgType=="PART":
                message="[%(time)d] <--| %(user)s has left" % {"time":time.time(), "user":userMask}
            if msgType=="KICK":
                message="[%(time)d] =-= %(user)s kicked %(kicked)s: %(reason)s" % {"time":time.time(), "user":user, "kicked":complete[0].split()[3], "reason":complete[1]}
            if msgType=="MODE":
                message="[%(time)d] =-= %(user)s set mode %(mode)s on %(person)s" % {"time":time.time(), "user":user, "mode":complete[0].split()[3], "person":', '.join(complete[0].split()[4:])}
            if msgType=="TOPIC":
                message="[%(time)d] =-= %(user)s changed the topic to: %(topic)s" % {"time":time.time(), "user":user, "topic":complete[1]}
            if message!="":
                file.write(message+"\n")
                file.flush()
            file.close()
            if msgType=="QUIT":
                for channel in set(globalv.channels):
                    if channel in globalv.channelUsers.keys():
                        if not user in globalv.channelUsers[channel]:
                            continue
                        if os.path.exists(os.path.join("logs","LogFile - "+channel+"-"+str(ttime[0]) + "-" + str(ttime[7]))):
                            file=open(os.path.join("logs","LogFile - "+channel+"-"+str(ttime[0]) + "-" + str(ttime[7])),"a")
                        else:
                            file=open(os.path.join("logs","LogFile - "+channel+"-"+str(ttime[0]) + "-" + str(ttime[7])),"w")
                        message="[%(time)d] |<-- %(user)s has quit: %(reason)s" % {"time":time.time(), "user":userMask,"reason":msg}
                        file.write(message+"\n")
                        file.close()
            if msgType=="NICK":
                for channel in set(globalv.channels):
                    if not user in globalv.channelUsers[channel]:
                        continue
                    if os.path.exists(os.path.join("logs","LogFile - "+channel+"-"+str(ttime[0]) + "-" + str(ttime[7]))):
                        file=open(os.path.join("logs","LogFile - "+channel+"-"+str(ttime[0]) + "-" + str(ttime[7])),"a")
                    else:
                        file=open(os.path.join("logs","LogFile - "+channel+"-"+str(ttime[0]) + "-" + str(ttime[7])),"w")
                    user = complete[0].split()[0].split('!')[0]
                    newNick = complete[1]
                    message="[%(time)d] =-= %(user)s is now known as %(newnick)s" % {"time":time.time(), "user":user,"newnick":newNick}
                    file.write(message+"\n")
                    file.close()
        except Exception as detail:
            print "Log failure: %s"%detail
        return [""]
    def describe(self, complete):
        msg=complete.message()
        sender=complete[0].split(' ')
        sender=sender[2]
        return ["PRIVMSG $C$ :I am the logging module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :I log your text so I can use it for nefarious means."]

