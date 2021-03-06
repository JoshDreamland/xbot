# -*- coding: utf-8 -*-
from plugins import plugin
import time
import globalv
import shlex
import re
import urllib2
class asyncInput(object):
    def __init__(self,Queue,inputQueue, channel):
        self.Queue=Queue
        latestFeedItem = {}
        checkFrequencies=[10,20,30,60,120,180,240,300,600,1200,3600]
        lastReadWasBlank=0
        checkFrequency=3
        feeds = []
        running = True
        initComplete = False
        while running:
            while not inputQueue.empty():
                data = inputQueue.get()
                if data=="stop":
                    running = False
                    break
                if data.split()[0]=="add":
                    data = ' '.join(data.split()[1:])
                    data = shlex.split(data)
                    name = data[0]
                    url = data[1]
                    regex = data[2]
                    latestFeedItem[(name, url, regex)]=""
                    feeds.append((name, url, regex))
                    if initComplete:
                        Queue.put("#PRIVMSG %s :Scraping '%s' for regex '%s'\r\n"%(channel, url, regex))
                if data=="list":
                    Queue.put("#PRIVMSG %s :Regex Reader for %s reading:\r\n"%(channel, channel))
                    for name, url, regex in feeds:
                        Queue.put("#PRIVMSG %s :%s: %s (%s)\r\n"%(channel, name, regex, url))
                if data=="--init--":
                    initComplete = True

            try:
                for feedItem in feeds:
                    name, url, regex = feedItem
                    print "-"*20
                    print feedItem
                    print name, url, regex
                    print "-"*20
                    feed=urllib2.urlopen(url).read()
                    try:
                        newFeedItem=re.findall(regex,feed.replace('\n','').replace('\r',''))[0]
                    except:
                        print "Failed to find new entry. Rolling with the old one"
                        print re.findall(regex,feed.replace('\n','').replace('\r',''))
                        newFeedItem=latestFeedItem[feedItem]
                    if newFeedItem!=latestFeedItem[feedItem]:
                        try:
                            float(newFeedItem)
                            float(latestFeedItem[feedItem])
                            areInts=True
                        except:
                            areInts=False
                        if areInts:
                            if newFeedItem>latestFeedItem[feedItem]:
                                direction=" (increasing)"
                            else:
                                direction=" (decreasing)"
                        else:
                            direction=""
                        latestFeedItem[feedItem]=newFeedItem
                        Queue.put("#PRIVMSG "+channel+" :\x0312"+name+"\x03: \x0311"+newFeedItem+direction+"\r\n")
                        if checkFrequency>0:
                            checkFrequency-=1
                            checkFrequency=0 if checkFrequency<0 else checkFrequency
                    else:
                        if checkFrequency<len(checkFrequencies)-1 and lastReadWasBlank:
                            checkFrequency+=1
                            lastReadWasBlank=0
                        lastReadWasBlank=1
                    time.sleep(checkFrequencies[checkFrequency])
            except Exception as detail:
                print "Regex Grabbing failure! Bad feed?"
                Queue.put("#PRIVMSG "+globalv.owner+" :"+name+" shutting down: "+str(detail)+"\r\n")
                time.sleep(60)
        Queue.put("#PRIVMSG "+channel+" :Site Reader "+name+" Shut down.\r\n")
    def gettype(self):
        return "input"
    def describe(self, complete):
        return ["PRIVMSG $C$ :I watch RSS feeds and talk about new entries!"]
