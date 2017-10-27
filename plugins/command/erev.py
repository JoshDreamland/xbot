# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import subprocess
from collections import namedtuple

rootdir = '/repos/enigma-dev/enigma-dev/'

RunResult = namedtuple('RunResult', ['ret', 'out', 'err'])

def readall(buf):
    return [] if not buf else [ x.decode("utf-8") for x in buf.readlines() ]

def exec_enigma(command):
    p = subprocess.Popen(command,
                         cwd=rootdir,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    return RunResult(ret=p.returncode,
                     out=readall(p.stdout), err=readall(p.stderr))

class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        pull=exec_enigma(["git", "pull"])
        if (pull.ret):
            message='Problem updating repository. Maybe try again later.';
        else:
            format='Commit %h by %an on %cD (%cr): %s'
            info=exec_enigma(['git', 'log', '--pretty=format:'+format, '-n', '1'])
            if (info.ret or len(info.out) != 1):
                message = "Up to date. (FYI: I'm having a bad day.)"
            else:
                message = info.out[0];
        return ["PRIVMSG $C$ :"+message]
    def describe(self, complete):
        return ["PRIVMSG $C$ :Call !erev to update the local ENIGMA repository copy"]
