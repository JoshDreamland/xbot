# -*- coding: utf-8 -*-
import globalv
from pluginHandler import load_plugin, unload_plugin
from pluginFormatter import formatInput
from pluginArguments import pluginArguments
import settingsHandler
def load_alias(name, plugin): #Loads an alias
    try:
        if plugin.split()[0] in globalv.loadedPlugins:
            if plugin.split()[0] in globalv.aliasExtensions:
                argumentsObject = pluginArguments(":nothing!nobody@nowhere PRIVMSG #NARChannel :%s%s"%(globalv.commandCharacter, plugin))
                argumentsObject = formatInput(argumentsObject, globalv.aliasExtensions, False)
                plugin = argumentsObject.fullMessage()[len(globalv.commandCharacter):]
                print plugin

            globalv.loadedPlugins.update({name:globalv.loadedPlugins[plugin.split()[0]]})
            if settingsHandler.tableExists(name)==0:
                globalv.loadedPlugins[plugin.split()[0]].__init_db_tables__(name)
            if name not in [x[0] for x in settingsHandler.readSetting("'core-userlevels'", "plugin")]:
                settingsHandler.writeSetting("'core-userlevels'", ["plugin", "level"],[name, str(globalv.loadedPlugins[plugin.split()[0]].__level__())])
        else: #If the aliases dependancy isn't loaded, load it, then get rid of it afterwards.
            load_plugin(plugin.split()[0])
            globalv.loadedPlugins.update({name:globalv.loadedPlugins[plugin.split()[0]]})
            if settingsHandler.tableExists(name)==0:
                globalv.loadedPlugins[plugin.split()[0]].__init_db_tables__(name)
            if name not in [x[0] for x in settingsHandler.readSetting("'core-userlevels'", "plugin")]:
                settingsHandler.writeSetting("'core-userlevels'", ["plugin", "level"],[name, str(globalv.loadedPlugins[plugin.split()[0]].__level__())])
            unload_plugin(plugin.split()[0])
        globalv.loadedAliases.update({name:plugin})
        globalv.basePlugin[name] = plugin.split()[0]
    except Exception as detail:
        print detail
        try:
            message("Function syntax: "+globalv.commandCharacter+"alias [word] [command] [arguments]",info[2])
        except:
            print "Plugin",name,"failed to load"
    try:
        print "Adding Extensions"
        print plugin
        globalv.aliasExtensions.update({name:" "+' '.join(plugin.split()[1:])})
    except:
        globalv.aliasExtensions.update({name:''})
    if globalv.aliasExtensions[plugin.split()[0]]!="":
        try:
            #globalv.aliasExtensions.update({name:globalv.aliasExtensions[plugin.split()[0]]})
            print "Would have broken here"
        except:
            globalv.aliasExtensions.update({name:''})
#Renames an alias, returns true on success and false on failure
def rename_alias(name, newName):
    if (name not in globalv.loadedAliases.keys()):
        return False
    if (newName in globalv.loadedAliases.keys()):
        return False
    globalv.loadedPlugins[newName] = globalv.loadedPlugins[name]
    globalv.loadedAliases[newName] = globalv.loadedAliases[name]
    globalv.aliasExtensions[newName] = globalv.aliasExtensions[name]
    del globalv.loadedPlugins[name]
    del globalv.loadedAliases[name]
    del globalv.aliasExtensions[name]
    settingsHandler.executeQuery("UPDATE alias SET aliasName=\"%s\" WHERE aliasName=\"%s\""%(newName, name))
    return True

def save_alias(name): #Saves alias to a file, to stick around between sessions. Returns 1 for complete, 0 for the plugin not existing in the current instnace, and 2 if it fails for some reason.
    if name in globalv.loadedAliases.keys(): #To check if the alias is in the current instance (IE, it actually works)
        isIn=0
        for plugin in [plugin[0] for plugin in settingsHandler.readSetting("alias","aliasName")]:
            if name==plugin:
                isIn=1
        plugin=globalv.loadedAliases[name].split()[0]
        arguments=' '.join(globalv.loadedAliases[name].split()[1:])
        if not isIn:
            settingsHandler.writeSetting("alias",['aliasName', 'aliasPlugin', 'aliasArguments'],[name, plugin, arguments])
        else:
            settingsHandler.updateSetting("alias","aliasPlugin", plugin, "aliasName='"+name+"'")
            settingsHandler.updateSetting("alias","aliasArguments", arguments, "aliasName='"+name+"'")
        return 1
    else:
        return 0
