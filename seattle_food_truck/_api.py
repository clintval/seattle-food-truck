import json
import datetime

import requests

from pandas import to_datetime  # Hope to get rid of this dependency soon!


__all__ = [
    'Location',
    'SeattleFoodTruckAPI']


class Location(object):
    """A listing of all buildings and their location codes."""
    PI_building = '69'


def humanize_list(array):
    """Return a grammatically correct English phrase of a list of items. Any
    list with items greater than 2 will, of course, use an Oxford comma.

    Parameters
    ----------
    array : iterable
        Any list of items with a __str__ method.

    Returns
    -------
    phrase : str
        A grammatically correct way of saying the iterable.

    Examples
    --------
    >>> humanize_list(['tomato'])
    'tomato'
    >>> humanize_list(['tomato', 'cabbage'])
    'tomato and cabbage'
    >>> humanize_list(['tomato', 'cabbage', 'lettuce'])
    'tomato, cabbage, and lettuce'

    """
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
        """Return a grammatically correct listing of categorical food items"""
        return humanize_list(self.food_categories)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'"{self.name}", style="{self.food_description}")')


class SeattleFoodTruckAPI():
    def __init__(self, location):
        # Hosting for the main domain and image hosting platform.
        self.host = 'https://www.seattlefoodtruck.com'
        self.img_host = ('https://s3-us-west-2.amazonaws.com/'
                         'seattlefoodtruck-uploads-prod')

        # API keys and values needed to get truck bookings.
        self.options = {
            'for_locations': location,
            'with_active_trucks': 'true',
            'include_bookings': 'true',
            'with_booking_status': 'approved'}

    def events_by_page(self, page):
        """Consider using the field `total_pages` to grab all pages in the
        pagination so a user is guaranteed to find a food truck when using the
        ``trucks_on_day()`` method if one such glorious food truck exists.

        Parameters
        ----------
        page : int
            The page to query from the paginator.

        Returns
        -------
        events : dict
            A JSON dictionary of all events on the requested page.

        """
        # Join all key values and concatenate them with ampersands
        query = '&'.join('='.join((k, v)) for k, v in self.options.items())

        # Make a GET request and parse the resulting call to JSON.
        response = requests.get(f'{self.host}/api/events?page={page}&{query}')
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

            # Instantiate all trucks that have been booked on this event.
            if date == scheduled_date:
                trucks.extend([Truck(booking['truck']) for
                               booking in event.get('bookings')])

        return trucks

    def trucks_today(self):
        """Returns food trucks scheduled for today"""
        today = datetime.datetime.today().date()
        return self.trucks_on_day(today)

    def trucks_tomorrow(self):
        """Returns food trucks scheduled for tomorrow"""
        today = datetime.datetime.today().date()
        return self.trucks_on_day(today + datetime.timedelta(days=1))

    def trucks_yesterday(self):
        """Returns yesterdays food trucks so you can be sad you missed them"""
        today = datetime.datetime.today().date()
        return self.trucks_on_day(today - datetime.timedelta(days=1))

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'location="{self.parameters["for_locations"]}")')


if __name__ == '__main__':  # Usage... will remove in favor of scripts/xxx.py
    api = SeattleFoodTruckAPI(Location.PI_building)
    print(api.trucks_today())
