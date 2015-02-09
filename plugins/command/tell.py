# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import settingsHandler
import time
from securityHandler import isAllowed
from userlevelHandler import getLevel
import re

class pluginClass(plugin):
    def gettype(self):
        return "command"
    def __append_seperator__(self):
        return True
    def action(self, complete):
        msg = complete.message().strip()
        firstspace = msg.index(' ')
        message = msg[firstspace+1:]
        recipients = msg[0:firstspace].lower();
        recipients = list(set(recipients.split(',')))
        recipients = [re.sub('[^0-9a-z-[\]*?]', '?', x) for x in recipients]
        sender=complete.user()
        senderMask=complete.userMask()
        timestamp=str(int(time.time()))
        message = message.replace('$U$','$recipient$')
        for recipient in recipients:
            print recipient
            lastid = int(settingsHandler.readSetting("laterd", "COUNT(id)"))
            id = str(lastid + 1)
            settingsHandler.writeSetting("laterd",
                [ "id", "recipient", "sender", "senderMask", "timestamp",
                    "message", "channel", "anonymous",  "sent"],
                [ id,    recipient,   sender,   senderMask,   timestamp,
                    message, "", "0", "0"])
            settingsHandler.db.commit()
        msg = ', '.join(recipients[:-1]) + ((" and " + recipients[-1]
            if len(recipients) > 1 else recipients[-1])
            + " will be informed when they next speak.")
        return ["PRIVMSG $C$ :" + msg]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !tell module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!tell [recipients] [message]"]

