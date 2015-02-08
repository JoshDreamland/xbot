# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import time
import re
import os
class pluginClass(plugin):
    def gettype(self):
        return "command"
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
        minLineCount = 6
        maxPeriod = 60
        for command in complete.message().split():
            if nextCommand=="":
                if command=="-days":
                    nextCommand="days"
                elif command.startswith("-nu"):
                    nextCommand="numUsers"
                elif command=="-channel":
                    nextCommand="channel"
                elif command=="-minlinecount":
                    nextCommand="minlinecount"
                elif command=="-maxperiod":
                    nextCommand="maxperiod"
                elif command=="-not":
                    nextCommand="blacklist"
                elif command=="-find":
                    nextCommand="whitelist"
                elif command.startswith('-h'):
                    return ["PRIVMSG $C$ :Usage: %s%s [-days Number of days to search] [-num Number of users to return] [-channel Channel to search] [-not Users to exclude] [-find Users to return results for]"%(globalv.commandCharacter, complete.cmd()[0])]
            else:
                if nextCommand=="days":
                    days=int(command)
                elif nextCommand=="numUsers":
                    numUsers=int(command)
                elif nextCommand=="channel":
                    channel=command.lower()
                elif nextCommand=="minlinecount":
                    try:
                        minLineCount = int(command)
                    except:
                        pass
                elif nextCommand=="maxperiod":
                    try:
                        maxPeriod = int(command)
                    except:
                        pass
                elif nextCommand=="blacklist":
                    userBlacklist=command.split(',')
                elif nextCommand=="whitelist":
                    userWhitelist=command.split(',')

                nextCommand=""
        last = ''
        lastTime = 0
        lineCount = 0
        for offset in xrange(days):
            day=currentDay-offset
            year=currentYear
            if day <= 0:
                day+=365
                year-=1
            path=os.path.join("logs","LogFile - "+channel+"-"+str(year)+"-"+str(day))
            if not os.path.exists(path):
                break
            data=open(path).readlines()

            for line in data:
                match=re.search("^\[(\d+)\]\s<(\S*)>", line)
                if match is None:
                    continue
                nickname=match.group(2)
                newtime=int(match.group(1))

                if last==nickname and newtime - lastTime < maxPeriod:
                    lineCount += 1
                    if lineCount == minLineCount:
                        print path
                        if nickname in users:
                            users[nickname]+=1
                        else:
                            users[nickname]=1
                        total+=1
                else:
                    last = nickname
                    lineCount = 1
                lastTime = newtime

        userArray=[[key, users[key]] for key in users.keys()]
        userArray.sort(key=lambda x:x[1])
        print userBlacklist
        userArray=filter(lambda x:x[0] not in userBlacklist, userArray)
        if userWhitelist!=[]:
            userArray=filter(lambda x:x[0] in userWhitelist, userArray)
        toReturn="PRIVMSG $C$ :%s total monologues from the past %s days! Rankings:"%(total, days)
        if len(userArray) == 0:
            toReturn+=" Nothing returned!"
        for index in range(1,min(numUsers+1,len(userArray)+1)):
            numLines=userArray[-index][1]
            name=userArray[-index][0]
            percentage=(numLines/float(total))*100
            if percentage>1:
                percentage=int(percentage)
            toReturn+=" %s with %s%% of the chat (%s monologue%s);"%(name, percentage, numLines, 's' if numLines != 1 else '')
        return [toReturn]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !say module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!say [input]"]

