# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import pickle
import datetime
from pluginArguments import pluginArguments
from pluginFormatter import formatOutput, formatInput
import re
import sys, traceback

class pluginClass(plugin):
    def gettype(self):
        return "realtime"

    def action(self, complete):
        user=complete.user()
        if complete.type()!="PRIVMSG":
            return [""]

        try:
            with open("autoCommands.dat") as file:
                regexes = pickle.load(file)
        except:
            return []

        message = complete.fullMessage()
        response = []
        for regex in regexes:
            try:
                m = re.search(regex, message, re.I)
                if m:
                    if not regex.startswith('^!') and message.startswith('!'):
                        continue
                    command = regexes[regex]
                    for i, g in enumerate(m.groups()):
                        command = command.replace(r'\%d' % (i+1), g if g else '')
                    plugin=command.split(' ')[0]

                    if plugin in globalv.loadedPlugins.keys():

                        arguments=pluginArguments(':'+complete.userMask()+" PRIVMSG "+complete.channel()+" :!"+command.replace('$*$', message).replace('$U$', complete.user()))
                        arguments=formatInput(arguments)
                        result = globalv.loadedPlugins[plugin].action(arguments)
                        if not isinstance(result, list):
                            result = [result]
                        response += result
            except:
                print "Failed to execute regex %s with command %s" % (regex, regexes[regex])
                traceback.print_exc(file=sys.stdout)

        return response
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !say module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!say [input]"]
