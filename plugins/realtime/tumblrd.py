# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import re
import urllib
import urllib2
import settingsHandler
import xml.sax.saxutils
import threading
import time
import mimetypes
def fixXMLEntities(match):
    value=int(match.group()[2:-1])
    return chr(value)
class pluginClass(plugin):
    def gettype(self):
        return "realtime"
    def __init__(self):
        self.lastURLs=[]
    def __init_db_tables__(self, name):
        settingsHandler.newTable("tumblrdIgnores","ignore")
        settingsHandler.newTable("tumblrd","username", "password")

    def action(self, completeargs):
        def makeRequest(reqData, async=True):
            success=False
            failed=0 if async else 14
            while not success:
                try:
                    con=urllib2.urlopen(req,None,10)
                    success=True
                except:
                    failed+=1
                    print "Tumblrd failed",failed,"times."
                    if failed>15:
                        success=True
                    time.sleep(30)

        if not settingsHandler.tableExists("tumblrdIgnores"):
            settingsHandler.newTable("tumblrdIgnores","ignore")
        complete=completeargs.complete()[1:].split(' :',1)
        imageFileTypes=[".jpg",".png",".bmp"]
        username = settingsHandler.readSetting("tumblrd", "username")
        password = settingsHandler.readSetting("tumblrd", "password")
        ignores=[x[0].lower() for x in settingsHandler.readSettingRaw("tumblrdIgnores","ignore")]
        if completeargs.channel().lower() in ignores or completeargs.user().lower() in ignores:
            return [""]
        if len(complete[0].split())>2:
            if complete[0].split()[1]=="PRIVMSG":
                msg=complete[1]
                sender=complete[0].split(' ')
                sender=sender[2]
                if msg.find('http://')!=-1 or msg.find('https://')!=-1:
                    url = re.search(".*(?P<url>https?://.+?)[\".,?!]?\s", msg+" ").group("url")
                    if url in self.lastURLs:
                        return [""]
                    else:
                        self.lastURLs.append(url)
                        if len(self.lastURLs)>10:
                            self.lastURLs.pop(0)
                    logindata={'email':username, "password":password,"tags":','.join((completeargs.channel(),completeargs.user()))}
                    if url[-4:].lower() in imageFileTypes:
                        uploaddata={"type":"photo", "source":url}
                    elif url.lower().find("youtube.com/watch")!=-1:
                        request = urllib2.urlopen(url)
                        page = request.read(10000).replace('\n','')
                        print page
                        title=re.findall("<\s*title\s*>(.*?)</title\s*>", page, re.I)
                        print title
                        title=title[0]
                        uploaddata={"type":"video", "embed":url, "caption":title}
                    else:
                        uploaddata={"type":"link", "url":url}
                    logindata.update(uploaddata)
                    print logindata
                    uploadData=urllib.urlencode(logindata)
                    req=urllib2.Request("http://www.tumblr.com/api/write",uploadData)
                    print "Constructing thread..."
                    thread=threading.Thread(target=makeRequest, args=(req,))
                    print "Launching thread..."
                    try:
                        thread.start()
                        print "Thread launched..."
                    except:
                        print "Thread failed to launch - using synchronous fallback"
                        makeRequest(req, False)
                        print "Sucessfully submitted data"
        return [""]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the plugin that follows URLs","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :None - I monitor all input, if you have a url in your text, I will find it."]
