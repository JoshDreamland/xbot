# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import urllib2
currencies={"QUID":"GBP","DOLLAR":"USD","DOLLARS":"USD","POUNDS":"GBP","POUND":"GBP","RUPEE":"INR","RUPEES":"INR"}
class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        msg=complete.message()
        tokens = msg.split()
        if len(tokens)==4 and tokens[2] == 'to':
            tokens = tokens[:2] + tokens[3:]
        if len(tokens)==3:
            first=tokens[1].upper()
            second=tokens[2].upper()
            if first in currencies.keys():
                first=currencies[first]
            if second in currencies.keys():
                second=currencies[second]
            if first==second:
                return ["PRIVMSG $C$ :Silly $U$ thinks that things can be converted to themselves. Look at silly $U$. Point and laugh."]
            toConv=first+second
            amount=tokens[0]
            try:
                test = float(amount)
            except:
                return ["PRIVMSG $C$ :Silly $U$ thinks that %s can be converted to a number. Look at silly $U$. Point and laugh."]
        elif len(tokens)==2:
            first=tokens[0].upper()
            second=tokens[1].upper()
            toConv=first+second
            amount='1'
        else:
            return ["PRIVMSG $C$ :Jesus christ what is wrong with you. Get out."]
        convert=float(urllib2.urlopen("http://download.finance.yahoo.com/d/quotes.csv?s="+toConv+"=X&f=sl1d1t1ba&e=.csv").read().split(',')[1])
        return ["PRIVMSG $C$ :%s %s = %.2f %s " % (amount, first, float(amount)*convert, second)]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !convert module","PRIVMSG $C$ :Usage:","PRIVMSG $C$ :!convert [number] [from currency] [to currency]"]
