# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import urllib2, urllib
import re
from settingsHandler import readSetting
import random
class pluginClass(plugin):
    def __init_db_tables__(self,name):
        import settingsHandler
        settingsHandler.newTable(name, "url", "regex","matchText")
        settingsHandler.writeSetting(name,["url","regex","matchText"],["http://google.com/complete/search?output=toolbar&q=$*$",".*","Autocomplete Results:"])
    def gettype(self):
        return "command"
    def action(self, complete):
        argument=urllib.quote(complete.message())
        url=readSetting(complete.cmd()[0],"url")
        regex=readSetting(complete.cmd()[0],"regex")
        url = url.replace('$*$', argument)
        print url
        page=urllib2.urlopen(urllib2.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }))
        print page
        page = page.read()
        matches=re.findall(regex,page, re.DOTALL)
        try:
            matches=[re.sub("<br\s?/?>", " ", match) for match in matches]
            matches=[re.sub("<.*?>","",match).replace('\n',' ').replace('\r',' ') for match in matches]
            matches=[re.sub("\s+"," ",match) for match in matches]
            #matches=[re.sub("x3c.*?x3e","",match) for match in matches]
        except Exception as detail:
            print detail
            print "printRandomRegexMatchFromWebpage didn't go so well in the removing HTML tags thing"
        ret=[]
        print regex
        if readSetting(complete.cmd()[0],"matchText")!="":
            ret.append(readSetting(complete.cmd()[0],"matchText"))
        for i in range(len(matches)):
            if type(matches[i])==str:
                ret.append(re.sub("[^a-zA-Z0-9.,{}()[\]?\\/!\"$%^&*:;_@'~#<>=+\-\s]","",matches[i]))
            elif type(matches[i])==tuple:
                ret.append(' '.join(matches[i]))
        if ret==[]:
            ret.append("No matches.")
        ret = random.choice(ret)
        ret=["PRIVMSG $C$ :"+ret.decode('utf-8')]
        return ret
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !printRandomRegexMatchFromWebpage module. I print out strings from a web page that match a regular expression.","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!printRandomRegexMatchFromWebpage [input]"]
