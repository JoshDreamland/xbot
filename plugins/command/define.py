# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import re
import json as JSON
import urllib, urllib2

class pluginClass(plugin):
    jsond = JSON.JSONDecoder()
    abbr = [ "n","vt","vi","v","adj","adv" ]
    full = [ "noun","verb-transitive","verb-intransitive",
             "verb","adjective","adverb" ]
    
    def _dic_define_(self, args):
        arg = args.split('|')
        phrase = arg[0]
        phrase = urllib.quote(phrase)
        key = "20136bcc66cf6016b300a01f4b402a36245b857cb95c5737c";
        url = ("http://api.wordnik.com/v4/word.json/" + phrase
                + "/definitions?api_key=" + key)
        
        ind = 0
        if len(arg) > 1:
            if re.match("[0-9]+", arg[1]) is None:
                url += "&partOfSpeech=" + urllib.quote(arg[1])
                #print "Using1 part of speech " + arg[1]
                if len(arg) > 2 and re.match("[0-9]+", arg[2]) is not None:
                    ind = int(arg[2]);
                    #print "Using1 index " + str(ind)
            else:
                if len(arg) > 2:
                    url += "&partOfSpeech=" + urllib.quote(arg[2])
                    #print "Using2 part of speech " + arg[2]
                ind = int(arg[1]);
                #print "Using2 index " + str(ind)

            try:
                i = self.abbr.index(pos)
                pos = self.full[i]
            except:
                pass

        try:
            jsondef = urllib2.urlopen(url).read()
        except:
            return "I've encountered an internet error."
        
        try:
            definitions = self.jsond.decode(jsondef)
        except:
            return jsondef
            return "My dictionary is scrambled!";
        
        defcount = len(definitions)
        if defcount == 0:
            return "No definitions found. Try !spell <word>"
        if ind >= defcount:
            return "I don't have that many definitions for that word.";
        
        speech = {}
        for defn in definitions:
            if 'partOfSpeech' in defn:
                pos = defn['partOfSpeech']
                if pos in speech:
                    speech[pos] += 1
                else:
                    speech[pos] = 1

        defn = definitions[ind];
        if "word" not in defn or "partOfSpeech" not in defn or "text" not in defn:
            return "Someone spilled something over that definition..."
        
        word = defn["word"]
        pos = defn["partOfSpeech"]
        deftext = defn["text"]
        
        speechHist = [];
        for pos in speech:
            speechHist += [(str(pos) + "=" + str(speech[pos]))]
        speechHist = "{" + ", ".join(speechHist) + "}"
        
        return word + " (" + pos + "): " + deftext.strip() + " " + speechHist
    
    def gettype(self):
        return "command"
    
    def action(self, complete):
        msg = complete.message().decode('utf-8');
        return ["PRIVMSG $C$ :" + self._dic_define_(msg)]
    def describe(self, complete):
        msg=complete.message()
        return ["PRIVMSG $C$ :I am the !define module. I use google to define words!","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!define [word]"]
