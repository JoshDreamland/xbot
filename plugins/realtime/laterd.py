# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import settingsHandler
import datetime
from pluginArguments import pluginArguments
from pluginFormatter import formatOutput, formatInput
import time
import sys
import traceback
def correctChannel(messageChannel, channel):
    return (channel.lower() in [messageC.lower() for messageC in messageChannel.split('|')] or messageChannel=="")
def setMessageSent(id):
    print "Attempting to set complete"
    settingsHandler.updateSetting("laterd", "sent", "1", where="id='%s'"%id)
    print "Set complete!"

def totalSeconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def GetTimeUntilDatetime(toDiff):
    times = [
            ("week", 7 * 24 * 60 * 60),
            ("day", 24 * 60 * 60),
            ("hour", 60*60),
            ("minute", 60)
            ]
    difference = totalSeconds((toDiff - datetime.datetime.now()))
    isFuture = difference > 0
    difference = abs(difference)
    timeDif = [0, 0, 0, 0]
    retString = []

    for timeIndex, timeEntry in enumerate(times):
        while difference > timeEntry[1]:
            difference-=timeEntry[1]
            timeDif[timeIndex]+=1
        if (timeDif[timeIndex] > 0):
            retString.append("%s %s%s"%(str(timeDif[timeIndex]), timeEntry[0], ("s" if timeDif[timeIndex]!=1 else "")))


    if (difference > 0):
        retString.append("%s %s%s"%(str(int(difference)), "second", ("s" if difference!=1 else "")))

    if len(retString) > 1:
        retString = ", ".join(retString[:-1]) + " and " + retString[-1]
    else:
        retString = retString[0]
    if not isFuture:
        retString += " ago"
    return retString

def readAllActions(user):
    return settingsHandler.readSettingRaw(
        "laterd", "id,sender,senderMask,timestamp,message,channel,anonymous",
        where="('%s' GLOB recipient OR recipient GLOB '*|%s|*' OR recipient GLOB '%s|*' OR recipient GLOB '*|%s') AND sent='0'" % (user.lower(), user.lower(), user.lower(), user.lower()))


class pluginClass(plugin):
    def gettype(self):
        return "realtime"
    def __init_db_tables__(self, name):
        settingsHandler.newTable("laterd", "id", "recipient","sender","senderMask","timestamp","message", "channel", "anonymous",  "sent")
    def action(self, complete):
        user=complete.user()
        if complete.type()!="PRIVMSG":
            return [""]
        returns=[]

        messages = readAllActions(user);
        if (user.lower() == "joshdreamland"):
            messages += readAllActions("josh");
       	if (user.lower() == "ismavatar"):
            messages += readAllActions("ism");
       	if (user.lower() == "goombert"):
            messages += readAllActions("robert");

        if messages!=[]:
            dispatches=[]

            for message in messages:
                wipeMessage=True

                messageID=str(message[0])
                sender=message[1]
                senderMask=message[2]
                timestamp=datetime.datetime.fromtimestamp(int(message[3]))
                messageText=message[4]
                messageChannel=message[5]
                anonymous=message[6]=="1"
                if not correctChannel(messageChannel, complete.channel()):
                    continue

                try:
                    plugin=messageText.split()[0]
                    messageTextNew = messageText
                    messageTextNew = messageTextNew.replace('$recipient$', user)
                    messageTextNew = messageTextNew.replace('$*$', complete.fullMessage().decode('utf-8'))

                    if plugin=="dispatch":
                        senderName=""
                        if not anonymous:
                            senderName=sender
                        dispatches.append("%s: [%s] <%s>: %s" % (user, GetTimeUntilDatetime(timestamp), senderName, ' '.join(messageTextNew.split(' ')[1:])))
                        setMessageSent(messageID)
                        continue

                    if plugin not in globalv.loadedPlugins.keys():
                        plugin = 'say'
                        messageTextNew = 'say ' + messageTextNew
                    arguments=pluginArguments(':'+senderMask+" PRIVMSG "+complete.channel()+" :!"+messageTextNew)
                    arguments=formatInput(arguments)
                    try:
                        message=globalv.loadedPlugins[plugin].action(arguments)
                    except:
                        message=["PRIVMSG $C$ :%s" % messageText]
                    if message in [[],[""]]:
                        wipeMessage=False
                    #returns+=[m.decode('utf-8') for m in message]
                    returns+=message
                    if message!=[""] and message!=[]:
                        msg=message[0]
                        if msg.split()[0]=="PRIVMSG" or msg.split()[0]=="NOTICE":
                            location=msg.split()[1]
                        else:
                            location="$C$"
                        if not anonymous:
                            returns.append("PRIVMSG "+location+" :From "+sender+" to "+user+" "+GetTimeUntilDatetime(timestamp))
                    if wipeMessage:
                        setMessageSent(messageID)
                    if len(returns) >= 13:
                        break
                except Exception as detail:
                    print "There was an error in one of the later messages:",detail
                    traceback.print_tb(sys.exc_info()[2])
                    setMessageSent(messageID)

            target="$C$"
            if len(dispatches) > 1:
                target=user
                returns.append("PRIVMSG $C$ :%s: Messages incoming" % user)
            returns += ["PRIVMSG %s :%s" % (target, dispatch) for dispatch in dispatches]

        return returns
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !say module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!say [input]"]
