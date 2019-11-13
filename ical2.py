from icalendar import Calendar, Event
from datetime import datetime, timedelta #, timezone
from pytz import UTC # timezone

import arrow

g = open('muellkalender.ics','rb')
gcal = Calendar.from_ical(g.read())

components = gcal.walk()
now = datetime.now()
components = filter(lambda c: c.name=='VEVENT', components)
components = filter(lambda c: c.get('dtstart').dt.replace(tzinfo=None) - now > timedelta(0), components)  # filter out past events
components = sorted(components, key=lambda c: c.get('dtstart').dt.replace(tzinfo=None) - now, reverse=False)  # order dates soonist to now to farthest



for component in components:
    if component.name == "VEVENT":
        print(component.get('summary'))
        print(component.get('dtstart').dt)
        print(component.get('dtend').dt)
        dtstart = arrow.get(component.get('dtstart').dt)
        print(dtstart.humanize().title())
g.close()
