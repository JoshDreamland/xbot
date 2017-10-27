# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import re
import sys
import os

rootdir = '/repos/enigma-dev/enigma-dev/'
def populateSearch(regexp):
    results = []
    for subdir, dirs, files in os.walk(rootdir):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        abbrdir = subdir.replace(rootdir, '//', 1)
        for file in files:
            try:
                fullpath = os.path.join(subdir, file)
                abbrpath = os.path.join(abbrdir, file)
                lineno = 1
                for line in open(fullpath, 'r'):
                    if re.search(regexp, line):
                        results.append(
                            '%s:%s: %s' % (abbrpath, lineno, line.strip()))
                    lineno += 1
            except:
                continue
    global search_results
    global current_result
    search_results = results
    current_result = 0

def nextResult():
    global search_results
    global current_result
    if (len(search_results) < 1):
        return "Try doing a search first with !egrep"
    if (len(search_results) <= current_result):
        return "No more results."
    res = '[%s/%s] %s' % (
        current_result+1, len(search_results), search_results[current_result])
    current_result += 1
    return res

class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        try:
            regexp = complete.message().decode('utf-8','replace')
        except:
            regexp = complete.message()
        regexp = regexp.strip()

        if (len(regexp) < 1):
            message = nextResult()
        else:
            populateSearch(regexp)
            message = nextResult()

        return ["PRIVMSG $C$ :"+message]
    def describe(self, complete):
        return ["PRIVMSG $C$ :!egrep [regexp] - Grep over the ENIGMA repository"]
