import json
import datetime

import requests

from pandas import to_datetime


__all__ = [
    'Location',
    'SeattleFoodTruckAPI']


class Location(object):
    PI_BUILDING = '69'


def humanize_list(array):
    new = list(map(str, array))
    if len(array) == 1:
        return ''.join(new)
    elif len(array) == 2:
        return ' and '.join(new)
    else:
        new[-1] = f'and {new[-1]}'
        return ', '.join(new)


class Truck():
    def __init__(self, mapping):
        self.featured_photo = mapping.get('featured_photo')
        self.food_categories = mapping.get('food_categories')
        self.id = mapping.get('id')
        self.name = mapping.get('name')
        self.trailer = mapping.get('trailer')
        self.uid = mapping.get('uid')

    @property
    def food_description(self):
        return humanize_list(self.food_categories)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'"{self.name}", style="{self.food_description}")')


class SeattleFoodTruckAPI():
    def __init__(self, location):
        self.host = 'https://www.seattlefoodtruck.com'
        self.img_host = ('https://s3-us-west-2.amazonaws.com/'
                         'seattlefoodtruck-uploads-prod')
        self.options = {
            'for_locations': location,
            'with_active_trucks': 'true',
            'include_bookings': 'true',
            'with_booking_status': 'approved'}

    # Consider using the field `total_pages` to grab all pages in the
    # pagination so a user is guaranteed to find a food truck when using the
    # ``trucks_on_day()`` method if one such glorious food truck exists.`
    def events_by_page(self, page):
        options = '&'.join('='.join((k, v)) for k, v in self.options.items())
        URL = f'{self.host}/api/events?page={page}&{options}'
        response = requests.get(URL)
        events = json.loads(response.text).get('events')
        return events

    def trucks_on_day(self, date):
        assert isinstance(date, datetime.date)
        trucks = []
        for event in self.events_by_page(1):
            # Would love to remove pandas dependency but there is a stupid
            # colon in the timezone field and datetime.strptime is not
            # compatible with that format.
            scheduled_date = to_datetime(event.get('start_time')).date()

            if date == scheduled_date:
                trucks.extend([Truck(booking['truck']) for
                               booking in event.get('bookings')])

        return trucks

    def trucks_today(self):
        today = datetime.datetime.today().date()
        return self.trucks_on_day(today)

    def trucks_tomorrow(self):
        today = datetime.datetime.today().date()
        return self.trucks_on_day(today + datetime.timedelta(days=1))

    def trucks_yesterday(self):
        today = datetime.datetime.today().date()
        return self.trucks_on_day(today - datetime.timedelta(days=1))

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'location="{self.parameters["for_locations"]}")')


if __name__ == '__main__':
    # Usage!
    api = SeattleFoodTruckAPI(Location.PI_BUILDING)
    print(api.trucks_today())
