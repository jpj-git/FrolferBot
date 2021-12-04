
import urllib.parse
import os
from datetime import timedelta
from pprint import pprint

import pendulum
from dotenv import load_dotenv
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from gcsa.reminders import PopupReminder

load_dotenv()
EMAIL = os.getenv('CAL_EMAIL')
CAL = os.getenv('CAL_ID')
CREDS = os.getenv('CREDS')


def create_calendar_event(course_pick, sunday):
    text = urllib.parse.quote_plus(f'Disc Golf League at {course_pick}')
    dates = f'{sunday}T090000/{sunday}T120000'
    location = urllib.parse.quote(course_pick)
    details = f'https://udisc.com/courses?courseTerm={location}'

    base_url = 'https://calendar.google.com/calendar/r/eventedit'
    cal_url = f'{base_url}?text={text}&dates={dates}&ctz=America/New_York&location={location}&details={details}&colorId=8'

    pprint([text, dates, details, cal_url])

    return cal_url


def create_cal_event(course_pick, sunday):
    calendar = GoogleCalendar(credentials_path=CREDS)

    for event in calendar:
        pprint(event)

    start = sunday + timedelta(hours=9)
    end = (start + timedelta(hours=3))
    location = urllib.parse.quote(course_pick)
    event_id = course_pick.replace(' ', '').lower() + sunday.strftime('%m%d%Y')

    event = Event(
        f'Disc Golf League at {course_pick}',
        start=start,
        end=end,
        location=course_pick,
        event_id=event_id,
        details=f'https://udisc.com/courses?courseTerm={location}',
        reminders=[PopupReminder(75), PopupReminder()],
        color_id=8,
    )
    # calendar.add_event(event)
    print(f'Event created: {event}')
    print('Vars: ')
    pprint(vars(event))

    return event


if __name__ == '__main__':
    event_day = pendulum.now().next(pendulum.WEDNESDAY)
    create_cal_event('Ecker Hill', event_day)
