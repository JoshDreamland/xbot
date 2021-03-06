# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import settingsHandler
from pluginArguments import pluginArguments
from pluginFormatter import formatOutput, formatInput
import time
class pluginClass(plugin):
    def gettype(self):
        return "realtime"
    def __init_db_tables__(self, name):
        settingsHandler.newTable("greetd","channel","greet")
    def action(self, complete):
        user=complete.user()
        if complete.type()!="JOIN":
            return [""]
        returns=[]
        messages=settingsHandler.readSettingRaw("greetd","channel,greet")
        if complete.channel().lower() in [message[0].lower() for message in messages]:
            greetPlugin=settingsHandler.readSetting("greetd","greet",where="channel='%s'"%complete.channel())
            senderMask=complete.userMask()
            arguments=pluginArguments(str(':'+senderMask+" PRIVMSG "+complete.channel()+" :!"+greetPlugin+" "+complete.user()))
            arguments=formatInput(arguments)
            print [arguments.complete()]
            arguments.argument = str(arguments.argument)
            message=globalv.loadedPlugins[greetPlugin].action(arguments)
            print message
            message = formatOutput(message, arguments)
            returns+=message

        return returns
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !say module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!say [input]"]
