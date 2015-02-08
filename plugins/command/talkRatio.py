# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import time
import re
import os
class pluginClass(plugin):
    def gettype(self):
        return "command"
    def help(self):
        return ["PRIVMSG $C$ :Usage: %stalkRatio [-days Number of days to search] [-num Number of users to return] [-channel Channel to search] [-not Users to exclude] [-find Users to return results for] [-search Strings to search for (comma-seperated) | -searchRegex Regex to search for]"%globalv.commandCharacter]

    def action(self, complete):
        today=time.gmtime()
        currentYear=today[0]
        currentDay=today[7]
        users={}
        total=0
        days=5
        numUsers=3
        channel=complete.channel().lower()
        userBlacklist=[]
        userWhitelist=[]
        nextCommand=""
        wordSearch="";
        regexSearch="";
        for command in complete.message().split():
            if nextCommand=="":
                if command=="-days":
                    nextCommand="days"
                elif command.startswith("-nu"):
                    nextCommand="numUsers"
                elif command=="-channel":
                    nextCommand="channel"
                elif command=="-not":
                    nextCommand="blacklist"
                elif command=="-find":
                    nextCommand="whitelist"
                elif command=="-searchRegex":
                    nextCommand="searchRegex"
                elif command=="-search":
                    nextCommand="search"
                elif command.startswith('-h'):
                    return self.help()
            else:
                if nextCommand=="days":
                    days=int(command)
                elif nextCommand=="numUsers":
                    numUsers=int(command)
                elif nextCommand=="channel":
                    channel=command.lower()
                elif nextCommand=="blacklist":
                    userBlacklist=command.split(',')
                elif nextCommand=="whitelist":
                    userWhitelist=command.split(',')
                elif nextCommand=="searchRegex":
                    regexSearch+=" "+command
                    continue
                elif nextCommand=="search":
                    wordSearch+=" "+command
                    continue

                nextCommand=""
        wordSearch = wordSearch[1:]
        regexSearch = regexSearch[1:]
        errors = 0
        for offset in xrange(days):
            day=currentDay-offset
            year=currentYear
            if day <= 0:
                day+=366
                year-=1
            path=os.path.join("logs","LogFile - "+channel+"-"+str(year)+"-"+str(day))
            if not os.path.exists(path):
                print path
                errors += 1
                if errors > 5: break
                continue
            errors = 0
            data=open(path).readlines()
            for line in data:
                match=re.search(r"^\[.*?\] (?:\* (\S+)|<(\S+)>)\s+(.*)", line)
                if match is None:
                    continue
                nickname=(match.group(1) or match.group(2))
                line = match.group(3)
                foundOne=False
                if len(wordSearch):
                    searches = wordSearch.split(',')
                    for search in searches:
                        if search.lower() in line.lower():
                            foundOne=True
                            break
                    if not foundOne:
                        continue
                elif len(regexSearch):
                    if re.search(regexSearch, line, re.I) is not None:
                        foundOne = True
                    else:
                        continue
                if nickname in users:
                    users[nickname]+=1
                else:
                    users[nickname]=1
                total+=1
        userArray=[[key, users[key]] for key in users.keys()]
        userArray.sort(key=lambda x:x[1])
        print userBlacklist
        userArray=filter(lambda x:x[0] not in userBlacklist, userArray)
        if userWhitelist!=[]:
            userArray=filter(lambda x:x[0] in userWhitelist, userArray)
        toReturn="PRIVMSG $C$ :%s total lines from the past %s days! Rankings:"%(total, days)
        if len(userArray) == 0:
            toReturn+=" Nothing returned!"
        for index in range(1,min(numUsers+1,len(userArray)+1)):
            numLines=userArray[-index][1]
            name=userArray[-index][0]
            percentage=(numLines/float(total))*100
            if percentage>1:
                percentage=int(percentage)
            toReturn+=" %s with %s%% of the chat (%s lines);"%(name, percentage, numLines)
        return [toReturn]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !talkRatio module"] + self.help()
