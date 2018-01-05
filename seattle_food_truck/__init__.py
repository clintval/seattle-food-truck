import datetime

from functools import partial
from urllib.parse import quote_plus
from math import radians, cos, sin, asin, sqrt

import requests

# Dependency exists because the Python standard library cannot parse a
# timestamp with a colon in the time zone offset.
from dateutil.parser import parse as date_parse

__all__ = [
    'Location',
    'Client',
    'Truck',
    'haversine_distance',
    'lat_long_from_address',
    'humanize_list']

HOST = 'https://www.seattlefoodtruck.com/api/{table}?'
IMAGE_HOST = 'https://s3-us-west-2.amazonaws.com/seattlefoodtruck-uploads-prod'


def haversine_distance(lat_long1, lat_long2):
    """Distance between two points on Earth in miles"""
    lon1, lat1, lon2, lat2 = map(radians, [*lat_long1, *lat_long2])

    long_dist = lon2 - lon1
    lat_dist = lat2 - lat1
    a = sin(lat_dist / 2)**2 + cos(lat1) * cos(lat2) * sin(long_dist / 2)**2
    c = 2 * asin(sqrt(a))

    miles = 3959 * c  # Radius of Earth in miles
    return miles


def lat_long_from_address(address):
    """Returns the latitude and longitude from an address using the Google maps
    API for geocoding.

    Parameters
    ----------
    address : str
        An address on Earth. Preferrably in Seattle.

    Returns
    -------
    lat_long : tuple of float
        The first latitude and longitude of the address found using the Google
            maps API for geocoding.

    """
    URL = 'https://maps.googleapis.com/maps/api/geocode/json?'
    try:
        response = requests.get(URL, {'address': quote_plus(address)})
        results, *_ = response.json().get('results')
        location = results.get('geometry').get('location')
        lat_long = location['lat'], location['lng']
    except ValueError:
        raise ValueError('Lat/Long not found for address: {address}')
    return lat_long


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


class lazyproperty(object):
    """Decorator function to memoize an expensive property"""

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

    def __repr__(self):
        return f'<self.__class__.__name__ func=self.func>'


class Location(object):
    """Represents a location where a food truck may appear"""

    def __init__(self, mapping):
        self.__dict__.update(mapping)

    @property
    def lat_long(self):
        """Return the latitude and longitude as a tuple"""
        return self.latitude, self.longitude

    def distance_from(self, address=None, lat_long=None):
        """The distance in miles between this food truck locationa and a
        specified location. Either `address` or `lat_long` must be specified.

        Parameters
        ----------
        address : str
            The address of the query location.
        lat_long : tuple of floats
            The latitude and longitude of the query location.

        Returns
        -------
        distance : float
            The distance in miles between the two locations.

        """
        if address is None and lat_long is None:
            raise ValueError('`address` or `lat_long` must be specified.')
        elif address is not None:
            lat_long = lat_long_from_address(address)
        elif (
            lat_long is not None and
            not all(isinstance(_, float) for _ in lat_long)
        ):
            raise ValueError('`lat_long` must be a list of floats.')

        distance = haversine_distance(self.lat_long, lat_long)
        return distance

    def trucks_on_day(self, date):
        """Returns the food trucks at a given date"""
        assert isinstance(date, datetime.date)

        trucks = []
        for event in Client.events_at_location(self):
            scheduled_date = date_parse(event.get('start_time')).date()

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
        """Returns yesterday's food trucks so you can be sad you missed them"""
        today = datetime.datetime.today().date()
        return self.trucks_on_day(today - datetime.timedelta(days=1))

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'name="{self.name.strip()}", '
            f'address="{self.address}", '
            f'uid={self.uid})')


class Truck(object):
    """Represents a food truck in Seattle"""

    def __init__(self, mapping):
        self.__dict__.update(mapping)

    @property
    def food_description(self):
        """Return a grammatically correct listing of categorical food items"""
        return humanize_list(self.food_categories)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'"{self.name}", style="{self.food_description}")')


class Client(object):
    """A class that represents the API at www.seattlefoodtrucks.com."""

    def location_closest_to(self, address=None, lat_long=None):
        """Find the food truck location closest to the query location

        Parameters
        ----------
        address : str
            The address of the query location.
        lat_long : tuple of floats
            The latitude and longitude of the query location.

        Returns
        -------
        location : Location
            The food truck location closed to the query location.

        """
        if address is None and lat_long is None:
            raise ValueError('`address` or `lat_long` must be specified.')
        elif address is not None:
            lat_long = lat_long_from_address(address)
        elif (
            lat_long is not None and
            not all(isinstance(_, float) for _ in lat_long)
        ):
            raise ValueError('`lat_long` must be a list of floats.')

        distance_from_reference = partial(
            haversine_distance,
            lat_long2=lat_long)

        distances = list(map(
            distance_from_reference,
            [l.lat_long for l in self.locations]))
        location = self.locations[distances.index(min(distances))]
        return location

    @staticmethod
    def events_at_location(location):
        """Lists the events at a given location

        Returns
        -------
        location : Location
            The Location to query

        """
        params = {
            'for_locations': str(location.uid),
            'with_active_trucks': 'true',
            'include_bookings': 'true',
            'with_booking_status': 'approved'}

        # Paginate through results with these parameters on the `events` table.
        events = Client._paginate(HOST, 'events', params)
        return events

    @lazyproperty
    def locations(self):
        """A memoized property of all locations at instantiation time."""
        locations = list(map(Location, self._paginate(HOST, 'locations')))
        return locations

    @staticmethod
    def _paginate(host, table, params=None):
        """Helper function to paginate through the pages of a call to the web
        API. An initial call is made to set the `total_pages` variable and then
        all further pages are requested.

        Parameters
        ----------
        host : str
            URL destination of the web host API.
        table : str
            The table name from the web host API.
        params : None or dict
            A list of API parameters.

        Returns
        -------
        content : list
            All items found in the given table as a result of pagination.

        """
        params = params or {}
        content = []

        page = total_pages = 1
        while page <= total_pages:
            json = requests.get(
                host.format(table=table),
                params={**params, 'page': str(page)}).json()

            page += 1
            total_pages = json.get('pagination').get('total_pages')
            content.extend(json.get(table))
        return content

    def __repr__(self):
        return f'{self.__class__.__name__}()'
