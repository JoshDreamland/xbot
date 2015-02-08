# -*- coding: utf-8 -*-
from plugins import plugin
import globalv,urllib2
class pluginClass(plugin):
	def gettype(self):
		return "command"
	def action(self, complete):
		msg=complete.message()
		url="http://ws.audioscrobbler.com/2.0/?method=track.search&track="+msg.replace(' ','%20')+"&api_key=2d51d7338fd13b2c1045f68e3a2ccc62"
		feed=urllib2.urlopen(url).read()
		name=feed.split('<name>')[1].split('</name>')[0]
		artist=feed.split('<artist>')[1].split('</artist>')[0]
		link=feed.split('<url>')[1].split('</url>')[0]
		msg="Found \""+name+"\" by "+artist+" (at "+link+")"
		return ["PRIVMSG $C$ :"+msg]
	def describe(self, complete):
		msg=complete.message()
		return ["PRIVMSG $C$ :I am the !last.fm search module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!last.fm [track]"]
