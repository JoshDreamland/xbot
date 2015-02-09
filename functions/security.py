# -*- coding: utf-8 -*-
import settingsHandler
import globalv
def users():
	return [] #OMGbot Identified User [2]
def accessRight(user):
	# This is where we'd put owner access rights, IF WE HAD ANY
	accessRights = {globalv.owner:[]}
	if user in accessRights.keys():
		return accessRights[user]
	else:
		return []
