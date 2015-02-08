# -*- coding: utf-8 -*-
from plugins import plugin
from datetime import datetime
from securityHandler import isAllowed
import globalv
import pickle
import os
import difflib
import re

def days_till(date):
    now = datetime.now()
    now = now.replace(hour = 10)
    date = date.replace(hour = 11)

    if date.year == 1900:
        if date.month > now.month:
            date = date.replace(year = now.year)
        elif date.month < now.month:
            date = date.replace(year = now.year+1)
        else:
            if date.day > now.day:
                date = date.replace(year = now.year)
            elif date.day < now.day:
                date = date.replace(year = now.year+1)
            else:
                return 0
    return (date - now).days

def parse_date(date):
    today = datetime.now()
    if date.year == today.year and date.month == today.month and date.day == today.day:
        return "today"
    if date.year != 1900:
        parsed = date.strftime("%B {S} %Y")
    else:
        parsed = date.strftime("%B {S}")

    day = date.day
    suffix = 'th' if 11 <= day <= 13 else {1:'st',2:'nd',3:'rd'}.get(day % 10, 'th')

    return parsed.replace("{S}", '%d%s' % (date.day, suffix))

def interpret_date(eventdate, formats):
    eventdate = eventdate.replace("gust","____").replace("st","").replace("nd","").replace("rd","").replace("th","").replace("____","gust")

    for dformat in formats:
        try:
            newdate = datetime.strptime(eventdate, dformat)
            return newdate
        except:
            pass
    return None

def remove_keys_lower(d, key):
    to_remove = []
    for e in d:
        if e.lower() == key:
            to_remove.append(e)
    for e in to_remove:
        del d[e]

class pluginClass(plugin):
    def __init__(self):
        self.formats = [
            "%Y-%m-%d",    #2017-03-31
            "%B %d, %Y",   #March 31, 2017
            "%B %d %Y",    #March 31 2017
            "%d %B %Y",    #31 March 2017
            "%d %B",       #31 March
            "%B %d"       #March 31
            ]

        self.blacklist = {
            'tomorrow': 'Tomorrow is tomorrow, you idiot.',
            'today': 'Are you an idiot?',
            'yesterday': 'WTF is that for question?',
        }

    def gettype(self):
        return "command"

    def action(self, complete):
        # Load the events

        self.file_name = "events-%s" % complete.cmd()[0]
        self.file_path = os.path.join("config", self.file_name)

        self.events = {}

        if os.path.exists(self.file_path):
            with open(self.file_path) as event_file:
                self.events = dict(pickle.load(event_file))

        # Make also a dict with the lower case versions
        self.events_lower = dict(map(lambda (key,val): (key.lower(),val), self.events.items()))

        # Get the message tokens
        s = complete.message().split()

        command = s[0] if len(s) > 0 else "upcoming"

        def processEventName(name):
            return re.sub(r'\bmy\b', "%s's" % complete.user(), name, re.I)

        if command == "upcoming":
	    n = re.search('\d+', complete.message())
	    if n is not None:
		n = int(n.group(0))
	    n = min(max(5,n),15)
            return self.show_upcoming(n)

        print 'hur', complete.message()
        is_set_command = re.search('^set (.+) as (.+?)$', complete.message())
        if is_set_command is not None:
            event = processEventName(is_set_command.group(1))
            date = is_set_command.group(2)
            return self.set_event(event, date)

        is_override_command = re.search('^override (.+) as (.+?)$', complete.message())
        if is_override_command is not None:
            event = processEventName(is_override_command.group(1))
            date = is_override_command.group(2)
            return self.override_event(event, date)

        if command == "remove":
            if isAllowed(complete.userMask()) < 150:
                return ["PRIVMSG $C$ :You don't have the privileges to remove events."]

            event = processEventName(' '.join(s[1:]))

            return self.delete_event(event)

        if command == "till":
            event = processEventName(' '.join(s[1:]))
            return self.show_countdown(event)

        event = processEventName(' '.join(s))
        return self.show_countdown(event)

    ## SHOW UPCOMING #
    def show_upcoming(self, n=5):
        upcoming = [(event, date) for event, date in self.events.items() if days_till(date)>=0]
        upcoming = sorted(upcoming, key = lambda (event, date): days_till(date))

        response = "Upcoming %d: " % n

        for event, date in upcoming[:n]:
            response += event + " on " + parse_date(date) + "; "

        return ["PRIVMSG $C$ :" + response]

    ## SHOW COUNTDOWN #
    def show_countdown(self, eventname):
        eventname_lower = eventname.lower()

        if eventname_lower in self.blacklist:
            return ["PRIVMSG $C$ :%s" % self.blacklist[eventname_lower]]

        # Check if event exists
        event_is_date = False
        eventdate = None
        event_exists = False
        if eventname_lower in self.events_lower:
            event_exists = True

            eventdate = parse_date(self.events_lower[eventname_lower])

            delta_days = days_till(self.events_lower[eventname_lower])

            # Get the event name with original capitalization
            for event in self.events:
                if event.lower() == eventname_lower:
                    eventname = event
                    break
        else:
            # Check if the event is simply a date
            newdate = interpret_date(eventname, self.formats)
            if newdate:
                event_exists = True
                event_is_date = True
                delta_days = days_till(newdate)

        # Event does not exist...
        if not event_exists:
            # Prepare a list of close matches
            response = ["PRIVMSG $C$ :%s has not been set as an event yet." % eventname]
            close_matches = difflib.get_close_matches(eventname, self.events)

            # Check if a match is 90% identical, and use that instead
            estimate_exists = False
            for match in close_matches:
                if difflib.SequenceMatcher(a=eventname, b=match).quick_ratio() > 0.9:
                    eventname = match
                    eventname_lower = eventname.lower()
                    eventdate = parse_date(self.events_lower[eventname_lower])
                    delta_days = days_till(self.events_lower[eventname_lower])
                    estimate_exists = True
                    break

            if not estimate_exists:
                if len(close_matches) > 0:
                    response.append("PRIVMSG $C$ :Did you mean: " + ', '.join(close_matches))
                return response

        if delta_days == 0:
            return ["PRIVMSG $C$ :Today it's %s!" % eventname]
        elif delta_days < 0:
            if not event_is_date:
                return ["PRIVMSG $C$ :%s happened %d day%s ago (%s)" % (eventname, -delta_days, 's' if delta_days != 1 else '', eventdate)]
            else:
                return ["PRIVMSG $C$ :%s happened %d day%s ago" % (eventname, -delta_days, 's' if delta_days != 1 else '')]
        else:
            if not event_is_date:
                return ["PRIVMSG $C$ :%d day%s till %s (%s)" % (delta_days, 's' if delta_days != 1 else '', eventname, eventdate)]
            else:
                return ["PRIVMSG $C$ :%d day%s till %s" % (delta_days, 's' if delta_days != 1 else '', eventname)]

    ## NEW EVENT #
    def set_event(self, eventname, eventdate, override = False):
        eventname_lower = eventname.lower()

        if interpret_date(eventname, self.formats):
            return ["PRIVMSG $C$ :You are not allowed to set dates as event names."]

        # Create an appropiate datetime object
        newdate = interpret_date(eventdate, self.formats)

        if eventname_lower in self.events_lower:
            # Event already exists
            if not override:
                current_date = parse_date(self.events_lower[eventname_lower])

                response = ["PRIVMSG $C$ :That event has already been set at %s." % current_date]
                if interpret_date(current_date, self.formats) != newdate:
                    response += ["Use \"!countdown override %s as %s\" to override" % (eventname, ddate)]
                return response
        elif override:
            response = ["PRIVMSG $C$ :%s has not been set as an event yet." % eventname]
            close_matches = difflib.get_close_matches(eventname, self.events)
            if len(close_matches) > 0:
                response.append("PRIVMSG $C$ :Did you mean: " + ', '.join(close_matches))
            return response

        if not newdate:
            return ["PRIVMSG $C$ :Invalid date format. Valid date formats: YYYY-mm-dd, Month dd(th)(,) (YYYY), dd Month"]

        # Remove any keys of which the lowercase version clashes with the new eventname
        remove_keys_lower(self.events, eventname_lower)
        self.events[eventname] = newdate

        with open(self.file_path,"w") as event_file:
            pickle.dump(self.events, event_file)

        return ["PRIVMSG $C$ :%s successfully %s!" % (eventname, "updated" if override else "added")]

    ## OVERRIDE EVENT #
    def override_event(self, eventname, eventdate):
        return self.set_event(eventname, eventdate, True)

    ## DELETE EVENT #
    def delete_event(self, eventname):
        eventname_lower = eventname.lower()

        if eventname_lower not in self.events_lower:
            response = ["PRIVMSG $C$ :%s has not been set as an event." % eventname]
            close_matches = difflib.get_close_matches(eventname, self.events)
            if len(close_matches) > 0:
                response.append("PRIVMSG $C$ :Did you mean: " + ', '.join(close_matches))
            return response

        remove_keys_lower(self.events, eventname_lower)

        with open(self.file_path,"w") as event_file:
            pickle.dump(self.events, event_file)

        return ["PRIVMSG $C$ :Event successfully removed!"]


    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the !countdown module",
                "PRIVMSG $C$ :Usage:",
                "PRIVMSG $C$ :!countdown set [Event name] as [Date]",
                "PRIVMSG $C$ :!countdown (till) [Event name]"]
