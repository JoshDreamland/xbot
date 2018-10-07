# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import re
import json
import urllib
import urllib2
import xml.sax.saxutils
from bitlyServ import bitly
import mimetypes
import time
import settingsHandler
def fixXMLEntities(match):
    value=int(match.group()[2:-1])
    return chr(value)
def parseYoutube(url, pageData):
    if re.search("watch\?.*?v=", url) is not None:
        print "Trying %s" % url
        title=re.search("<title>(.*?) - YouTube</title>", pageData, re.I)
        if title is None: title = '??'
        else: title = title.group(1)
        uploader=re.search('http://schema.org/Person">\s+<link itemprop="url" href="http://www.youtube.com/user/(.+?)"', pageData, re.I)
        if uploader is not None: uploader = uploader.group(1)
        else:
            uploader = re.search('data-name="watch">([^<]+)</a><span class="yt-user-separator"', pageData)
            if uploader is not None: uploader = uploader.group(1)
            else: uploader = '??'
        length_seconds = re.search('"length_seconds": (\d+)', pageData)
        if length_seconds is None:
            length = '??:??'
        else:
            length_seconds = int(length_seconds.group(1))
            seconds = length_seconds % 60
            minutes = (length_seconds / 60) % 60
            hours = length_seconds / 3600
            length = '%02d:%02d' % (minutes, seconds)
            if hours > 0:
                length = '%d:%s' % (hours, length)

        return ["PRIVMSG $C$ :Video: %s by %s (%s)"%(title.decode('utf-8'),uploader,length)]
    else:
        title=re.findall("<\s*title\s*>(.*?)</title\s*>", pageData, re.I)[0]
        domain = re.search("(?P<url>https?://[^/\s]+)", url).group("url")
        return ["PRIVMSG $C$ :Title: %s (at %s)" % (title.decode('utf-8'), domain.decode('utf-8'))]

def doNothing(url, pageData):
    return [""]
def parseAdfly(url, pageData):
    realUrl = re.findall("var url = '(.*?)'",pageData)[0]
    Req = urllib2.Request(realUrl,None,{"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"})
    response=urllib2.urlopen(Req,None, 15)
    page=response.read(50000)
    page=page.replace('\n','')
    fullURL=response.geturl()
    title=re.findall("<\s*title\s*>(.*?)</title\s*>", page, re.I)
    if len(title)>0:
        title=title[0]
        title=re.sub("\s\s+", " ", title).strip()
        domain = re.search("(?P<url>https?://[^/\s]+)", fullURL).group("url")
        return ['PRIVMSG $C$ :Title: '+title.decode('utf-8')+ ' (at '+domain.decode('utf-8')+')']
    else:
        return ['PRIVMSG $C$ :Target URL: %s'%fullURL]

def isIgnored(sender):
    name = sender.lower()
    return name == "travis-ci"

class pluginClass(plugin):
    headers = {
        '.*soundcloud.com': {},
        '.*youtube.com': {},
        '': {"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
    }
    def __init__(self):
        self.specialDomains={
          "http://www.youtube.com":  parseYoutube,
          "https://www.youtube.com": parseYoutube,
          "http://youtube.com":      parseYoutube,
          "https://youtube.com":     parseYoutube,
          "https://youtu.be":        parseYoutube,
          "http://youtu.be":         parseYoutube,
          "http://adf.ly": parseAdfly
        }
    def gettype(self):
        return "realtime"
    def __init_db_tables__(self, name):
        settingsHandler.newTable(name, "showDomainLink")
        settingsHandler.writeSetting(name, ["showDomainLink"], ["true"])
    def getDomainMatch(self, domain):
        print "Matching",domain
        for key in self.specialDomains.keys():
            print "Trying",key
            if re.match(key, domain)!=None:
                print "Matched",key
                return key
        print "No match"
        return False
    def action(self, complete):
        showDomain = True if settingsHandler.readSetting("urlFollow", "showDomainLink")=="true" else False
        if "urlFollowQueue" not in globalv.communication.keys():
            return self.urlFollow(complete, showDomain)
        else:
            globalv.communication["urlFollowQueue"].put((complete, self.urlFollow))
            return [""]
    def urlFollow(self, complete, showDomain = True):
        username = complete.user()
        complete=complete.complete()[1:].split(' :',1)
        if len(complete[0].split())>2:
            if complete[0].split()[1]=="PRIVMSG":
                msg=complete[1]
                sender=complete[0].split(' ')
                sender=sender[2]

                if isIgnored(username):
                    return [""]

                if msg.find('http://')!=-1 or msg.find('https://')!=-1:

                    url = re.search(".*(?P<url>https?://[^\s#]+)", msg).group("url")
                    if url[-2:]==")$":
                        url = url[:-2]
                    print url
                    if url[-1]=="\x01":
                        url=url[0:-1]
                    if msg.split()[0]=="\x01ACTION":
                        return [""]
                    domain = re.search("(?P<url>https?://[^/\s]+)", url).group("url")
                    isDomain=re.findall("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", domain)
                    if isDomain!=[]:
                        return [""]
                    headers = self.headers['']
                    for regex in self.headers:
                        if regex == '': continue
                        if re.match(regex, domain):
                            headers = self.headers[regex]
                    try:
                        try:
                            print "using headers", headers
                            Req = urllib2.Request(url,None,headers)
                            response=urllib2.urlopen(Req,None, 15)
                            first_bytes = response.read(64)
                            weird_byte_count = 0
                            for c in first_bytes:
                                if ord(c) < 32:
                                    weird_byte_count += 1

                            if weird_byte_count > 15:
                                return

                            page=first_bytes + response.read(800000)
                            page=page.replace('\n','').replace('\r','')
                            fullURL=response.geturl()
                            #domain = re.search("(?P<url>https?://[^/\s]+)", fullURL).group("url")

                        except Exception as detail:
                            print detail
                            if str(detail)!="<urlopen error [Errno -2] Name or service not known>":
                                return ["PRIVMSG $C$ :URLFollow Error: "+str(detail)]
                        if not self.getDomainMatch(domain):
                            title=re.findall("<\s*title\s*>(.*?)</title\s*>", page, re.I)
                            if len(title)>0:
                                title=title[0]
                                title=re.sub("\s\s+", " ", title).strip()
                                return ['PRIVMSG $C$ :Title: '+title.decode('utf-8')+ (' (at '+domain.decode('utf-8')+')' if showDomain else "")]
                            else:
                                if url!=fullURL:
                                    return ['PRIVMSG $C$ :Target URL: %s'%fullURL]
                        else:
                            return self.specialDomains[self.getDomainMatch(domain)](url, page)
                    except Exception as detail:
                        print "Exception:",detail
        return [""]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the plugin that follows URLs","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :None - I monitor all input, if you have a url in your text, I will find it."]
