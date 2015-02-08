# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import pickle
import os
from pluginFormatter import formatInput, formatOutput
from pluginArguments import pluginArguments
from securityHandler import isAllowed
from userlevelHandler import getLevel
class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        msg=complete.message().split()
        if len(msg)>1:
            if isAllowed(complete.userMask())>=getLevel(complete.cmd()[0]):
                try:
                    current = int(globalv.variables[msg[0]])
                    globalv.variables[msg[0]]=current + int(msg[1])
                    print globalv.variables
                    with open(os.path.join("config","variables"),'w') as file:
                        pickle.dump(globalv.variables,file,pickle.HIGHEST_PROTOCOL)
                except Exception as detail:
                    return ["PRIVMSG $C$ :Variable setting failure with expression !var %s: %s"%(complete.message(), detail)]

        else:
            if msg[0] in globalv.variables.keys():
                return ["PRIVMSG $C$ :%s"%globalv.variables[msg[0]]]
            else:
                return ["PRIVMSG $C$ :Undefined"]
        return [""]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !say module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!say [input]"]
