# -*- coding: utf-8 -*-
from plugins import plugin
import globalv
import subprocess
from collections import namedtuple

ENIGMA_REPO = '/repos/enigma-dev/enigma-dev/'
LATERALGM_REPO = '/repos/IsmAvatar/LateralGM/'
PRETTY_FORMAT = 'format:Commit %h by %an on %cD (%cr): %s'
HELP_TEXT=('I am the git tracking plugin. Call !erev to update the local '  +
           'ENIGMA repository copy, !lrev for LateralGM. Specify a revision ' +
           'for details about an arbitrary commit.')
RunResult = namedtuple('RunResult', ['ret', 'out', 'err'])

def readall(buf):
    return [] if not buf else [ x.decode("utf-8") for x in buf.readlines() ]

def exec_in_dir(command, path):
    p = subprocess.Popen(command,
                         cwd = path, 
                         stdout = subprocess.PIPE, 
                         stderr = subprocess.PIPE)
    p.wait()
    return RunResult(ret = p.returncode,
                     out = readall(p.stdout), err = readall(p.stderr))

def behind_origin(repo):
    if exec_in_dir(["git", "fetch"], repo).ret:
        return -1
    revs = exec_in_dir(["git", "rev-list", "HEAD..origin"], repo)
    if revs.ret:
        return -1
    if len(revs.out) and len(revs.out[0]):
        return len(revs.out)
    return 0

def command_handler(repo, args):
    if args:
        info = exec_in_dir(
                ['git', 'log', args, '--pretty=' + PRETTY_FORMAT, '-n', '1'],
                repo)
        if info.ret:
            pull = exec_in_dir(["git", "pull"], repo)
            if pull.ret:
                return [("Couldn't find your revision, then failed to update " +
                         "the repository (%s)") % pull.err[0].strip()]
            elif len(info.err) and 'unknown revision' in info.err[0]:
                return ["Couldn't find your revision (\"%s\")" % args]
            else:
                return [
                    "Git is screaming at me and I don't know why! It says %s"
                    % (info.err[0].strip() if len(info.err)
                       else "it doesn't like me!")]
            return [msg]
        else:
            msgs = [info.out[0].strip()]
            lag = behind_origin(repo)
            if lag > 0:
                msgs.append(
                    "Note: my local copy is behind origin by %s commits." % lag)
            return msgs
    else:
        pull = exec_in_dir(["git", "pull"], repo)
        if pull.ret:
            return ['Problem updating repository. Maybe try again later. (%s)' %
                          pull.err[0].strip()];
        else:
            info = exec_in_dir(
                    ['git', 'log', '--pretty=' + PRETTY_FORMAT, '-n', '1'],
                    repo)
            if (info.ret or len(info.out) != 1):
                return ["Up to date. (FYI: I'm having a bad day.)"]
            else:
                return [info.out[0].strip()]

class pluginClass(plugin):
    def gettype(self):
        return "command"
    def action(self, complete):
        cmd = complete.cmd()[0];
        if cmd == 'erev':
            repo = ENIGMA_REPO
        elif cmd == 'lrev':
            repo = LATERALGM_REPO
       	elif cmd == 'gitter':
       	    return  ["PRIVMSG $C$ :Hello! " + HELP_TEXT]
        else:
            return ["PRIVMSG $C$ :This is not a zero-configuration plugin."];
        return ["PRIVMSG $C$ :" + msg for msg in command_handler(repo, complete.message())]
    def describe(self, complete):
        return ["PRIVMSG $C$ :" + HELP_TEXT]
