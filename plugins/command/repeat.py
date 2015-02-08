# -*- coding: utf-8 -*-
from plugins import plugin
from pluginArguments import pluginArguments
from pluginFormatter import formatInput, formatOutput
import globalv
class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        command=complete.message()
        print "To repeat:", command
        commands=command.split()

        repeatTimes = int(commands[0])
        plugin = commands[1]

        command = ' '.join(commands[1:])
        arguments=pluginArguments(complete.complete())
        firstBit=arguments.complete().split(' :')[0]
        arguments.setComplete(firstBit+" :"+globalv.commandCharacter+command)
        arguments=formatInput(arguments)

        if plugin in globalv.loadedPlugins:
            result = []
            for i in xrange(repeatTimes):
                result += globalv.loadedPlugins[plugin].action(arguments)
            return result

        return []
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !say module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!say [input]"]
