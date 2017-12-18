# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import re
import sys
import os

search_results = None
results_by_relevance = None
current_result = None
displayed_result = None

class SearchResult:
    def __init__(self, repo, path, filename, lineno, line):
        self.repo = repo
        self.path = path
        self.filename = filename
        self.lineno = lineno
        self.line = line
    def str(self):
        if not self.lineno or not self.line:
            return '//%s' % self.path
        return '//%s:%s: %s' % (self.path, self.lineno, self.line.strip())

class ResultFile:
    def __init__(self, path, filename, count):
        self.path = path
        self.filename = filename
        self.count = count

class SearchManager:
    def __init__(self, repo):
        self.repo = repo
        self.rootdir = '/repos/%s/' % repo

    def performSearch(self, line):
        for pred in self.search_predicates:
            if not pred(line):
                return False
        return True

    def searchFile(self, fullpath, abbrpath, filename):
        for pred in self.file_predicates:
            if not pred(fullpath):
                return []
        
        if not len(self.search_predicates):
            return [SearchResult(self.repo, abbrpath, filename, None, None)]
        
        lineno = 1
        results = []
        for line in open(fullpath, 'r'):
            if self.performSearch(line):
                results.append(SearchResult(
                        self.repo, abbrpath, filename, lineno, line))
            lineno += 1
        return results

    def populateSearch(self):
        results = []
        for subdir, dirs, files in os.walk(self.rootdir):
            files = [f for f in files if f[0] != '.']
            dirs[:] = [d for d in dirs if d[0] != '.']
            abbrdir = subdir.replace(self.rootdir, '', 1)
            for file in files:
                try:
                    fullpath = os.path.join(subdir, file)
                    abbrpath = os.path.join(abbrdir, file)
                    lineno = 1
                    results += self.searchFile(fullpath, abbrpath, file)
                except:
                    continue

        results_by_file = {}
        for result in results:
            if not result.path in results_by_file:
                results_by_file[result.path] = []
            results_by_file[result.path].append(result)
        sorted_by_relevance = []
        for filepath, fileresults in results_by_file.iteritems():
            sorted_by_relevance.append(ResultFile(
                    filepath, fileresults[0].filename, len(fileresults)))
        sorted_by_relevance.sort(key = lambda res: -res.count)

        global search_results
        global current_result
        global results_by_relevance
        search_results = results
        results_by_relevance = sorted_by_relevance
        current_result = 0

# Try this out for a test of this system:
# r"""this is a test of 'multi w\ord' blocks\ in \0 my " \"data\" " yes"bu*tts"asd a* 'a*'"""
# should produce
# this            # is                # a
# test            # of                # multi\ w\\ord
# blocks\ in      # \0                # my
# \ \"data\"\     # yesbu\*ttsasd     # a*                # a\*
def lexingRegexSplit(command):
    res = []
    i = 0
    fr = 0
    pstr = ""
    while i < len(command):
        if command[i] == ' ':
            if len(pstr) or fr != i:
                res.append(pstr + command[fr:i])
            i += 1
            fr = i
            pstr = ""
        elif command[i] == '"':
            pstr += command[fr:i]
            i += 1
            fr = i
            while i < len(command) and command[i] != '"':
                if command[i] == '\\':
                    i += 1
                i += 1
            pstr += re.escape(command[fr:i].decode('string_escape'))
            i += 1
            fr = i
        elif command[i] == '\'':
            pstr += command[fr:i]
            i += 1
            fr = i
            while i < len(command) and command[i] != '\'':
                i += 1
            pstr += re.escape(command[fr:i])
            i += 1
            fr = i
        elif command[i] == '\\':
            i += 2  # Whatever the next character is, ignore it
            # Multi-char escape sequences can't contain anything we care about
        else:
            i += 1
    leftovers = pstr + command[fr:]
    if leftovers:
        res.append(leftovers)
    return res

def CaseSensitive(args):
    if 'case:yes' in args:
        args.remove('case:yes')
        return (args, True)
    if 'case:no' in args:
        args.remove('case:no')
    return (args, False)

def nextResult():
    global search_results
    global current_result
    global displayed_result
    if search_results == None:
        return "Try doing a search first with, eg, !egrep"
    if (len(search_results) < 1):
        return "Search had no results...."
    if (len(search_results) <= current_result):
        return "No more results."
    res = '[%s/%s] %s' % (
        current_result+1, len(search_results),
        search_results[current_result].str())
    displayed_result = search_results[current_result]
    current_result += 1
    return res

def searcher(regexp, match_case):
    if match_case:
        return lambda arg: re.search(regexp, arg)
    return lambda arg: re.search(regexp, arg, re.IGNORECASE)

def fun_grep(args, mgr):
    (args, case) = CaseSensitive(args)
    file_predicates = []
    search_predicates = []
    for arg in args:
        if arg[0] == 'f' and arg[1] == ':':
            file_predicates.append(searcher(arg[2:], case))
        else:
            search_predicates.append(searcher(arg, case))
    mgr.file_predicates = file_predicates
    mgr.search_predicates = search_predicates
    mgr.populateSearch()
    return nextResult()

def fun_url(args, mgr):
    (args, case) = CaseSensitive(args)
    if len(args) > 0:
        file_predicates = []
        for arg in args:
            file_predicates.append(searcher(arg, case))
        mgr.file_predicates = file_predicates
        mgr.search_predicates = []
        mgr.populateSearch()
        nextResult()
    if displayed_result and mgr.repo == displayed_result.repo:
        res = 'https://github.com/%s/blob/master/%s' % (
                displayed_result.repo, displayed_result.path)
        if len(args) > 1 and len(search_results) > 1:
            res += " (and %s other results; try a grep with f:filename)" % (
                    len(search_results) - 1)
        return res
    if len(args):
        return "No matching files..."
    return 'https://github.com/%s/' % mgr.repo

def fun_grepfiles(args):
    if results_by_relevance == None:
        return "Try doing a search first with, eg, !egrep"
    if not results_by_relevance:
        return "No matching files. Try a different search."
    if len(args):
        return "I don't know what to do with the arguments you specified.  " + args[0]
    i = 0
    res = ""
    while i < 10 and i < len(results_by_relevance):
        pattern = ", %s (%s)" if len(res) else "%s (%s)"
        res += pattern % (results_by_relevance[i].filename,
                          results_by_relevance[i].count)
        i += 1
    return res

enigma_manager = SearchManager('enigma-dev/enigma-dev')
lgm_manager = SearchManager('IsmAvatar/LateralGM')

commandTable = {
  'egrep': (lambda args: fun_grep(args, enigma_manager)),
  'lgrep': (lambda args: fun_grep(args, lgm_manager)),
  'eurl':  (lambda args: fun_url(args, enigma_manager)),
  'lurl':  (lambda args: fun_url(args, lgm_manager)),
  'grepfiles': fun_grepfiles,
  'grepnext': (lambda ignore: nextResult())
}

def errorOut(cmd):
    return lambda dc: "This is not a zero-configuration plugin. Unknown alias '%s'." % cmd

def basicHelp():
    res = "Commands are " +  ", ".join(commandTable.iterkeys()) + "."
    res += " Basic workflows include, eg, !egrep sprite; !grepnext; !grepnext;"
    res += " !eurl; !eurl specific_file"
    return res
        

class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        try:
            params = complete.message().decode('utf-8','replace')
        except:
            params = complete.message()
        lexed_args = lexingRegexSplit(params)

        cmd = complete.cmd()[0];
        message = commandTable.get(cmd, errorOut(cmd))(lexed_args)

        return ["PRIVMSG $C$ :"+message]
    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the Code Search plugin. " + basicHelp()]


