# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import re
import urllib, urllib2

class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        query = {'where':complete.message()}
        url = 'http://www.thefuckingweather.com/?%s' % (urllib.urlencode(query))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
        }
        req = urllib2.Request(url, headers = headers)
        first = urllib2.urlopen(req)
        source = first.read()

        content = re.search('class="content">(.*?)<table', source, re.DOTALL).group(1)
        content = re.sub('<[^<>]+>','', content)

        content = unicode(content).replace('&#39;',"'").replace('&#176;',u'\uc2b0')

        return [u"PRIVMSG $C$ :%s" % content]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !weather module. I give you the motherfucking weather."]
