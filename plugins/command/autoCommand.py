# -*- coding: utf-8 -*-
from plugins import plugin
from userlevelHandler import getLevel
from securityHandler import isAllowed
import globalv
import pickle
import re
import difflib

class pluginClass(plugin):
    def gettype(self):
        return "command"

    def __level__(self):
        return 100

    def action(self, complete):
        sender=complete.userMask()
        if isAllowed(sender)<getLevel(complete.cmd()[0]):
            return ["PRIVMSG $C$ :I can't let you do that, $U$"]
        try:
            with open("autoCommands.dat") as file:
                regexes = pickle.load(file)
        except:
            regexes = {}
            with open("autoCommands.dat", "w") as file:
                pickle.dump(regexes, file)
                print "couldn't open autoCommands.dat :("

        message = complete.message()
        args = message.split()

        if args[0] == "list":
            regex_lines = []
            regexes = list(regexes)
            line = '"%s"' % regexes[0]
            for regex in regexes[1:]:
                new_line = line + ', "%s"' % regex
                if len(new_line) > 200:
                    regex_lines.append("PRIVMSG $C$ :%s" % line)
                    line = '"%s"' % regex
                else:
                    line = new_line
            regex_lines.append("PRIVMSG $C$ :%s" % line)

            return ["PRIVMSG $C$ :The following regular expressions trigger autocommands:"] + regex_lines

        if args[0] == "add":
            if len(args) < 3:
                return []
            regex = args[1]
            exists = regex in regexes
            regexes[regex] = ' '.join(args[2:])
            with open("autoCommands.dat", "w") as file:
                pickle.dump(regexes, file)
            if exists:
                return ["PRIVMSG $C$ :Autocommand for regex %s updated!" % regex]
            else:
                return ["PRIVMSG $C$ :Autocommand for regex %s added!" % regex]

        if args[0] == "change":
            if len(args) < 3:
                return []
            regex = args[1]
            new_regex = args[2]
            if regex in regexes:
                regexes[new_regex] = regexes[regex]
                del regexes[regex]
                with open("autoCommands.dat", "w") as file:
                    pickle.dump(regexes, file)
                return ["PRIVMSG $C$ :Autocommand regex updated to %s!" % new_regex]
            else:
                new_regex = re.sub("\W", "", regex)
                regexes2 = {}
                for regex in regexes:
                    stripped_regex = re.sub("\W", "", regex)
                    if stripped_regex not in regexes2: regexes2[stripped_regex] = []
                    regexes2[stripped_regex] = regex

                alts = difflib.get_close_matches(new_regex, regexes2, 3, 0.5)
                ret = []
                for alt in alts:
                    for i in regexes2[alt]:
                        ret.append("\x02%s\x02" % i)
                if len(ret):
                    ret = "PRIVMSG $C$ :Did you mean: %s" % (', '.join(ret))
                else:
                    ret = ""
                return ["PRIVMSG $C$ :That regex is not an autocommand!", ret]

        if args[0] == "remove":
            if len(args) < 2:
                return []
            regex = args[1]
            if regex in regexes:
                del regexes[regex]
                with open("autoCommands.dat", "w") as file:
                    pickle.dump(regexes, file)
                return ["PRIVMSG $C$ :Autocommand removed!"]
            else:
                new_regex = re.sub("\W", "", regex)
                regexes2 = {}
                for regex in regexes:
                    stripped_regex = re.sub("\W", "", regex)
                    if stripped_regex not in regexes2: regexes2[stripped_regex] = []
                    regexes2[stripped_regex].append(regex)

                alts = difflib.get_close_matches(new_regex, regexes2, 3, 0.5)
                ret = []
                for alt in alts:
                    for i in regexes2[alt]:
                        ret.append("\x02%s\x02" % i)
                if len(ret):
                    ret = "PRIVMSG $C$ :Did you mean: %s" % (', '.join(ret))
                else:
                    ret = ""
                return ["PRIVMSG $C$ :That regex is not an autocommand!", ret]
        return []

    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !say module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!say [input]"]
