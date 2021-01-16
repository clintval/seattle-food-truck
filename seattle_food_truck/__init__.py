import datetime

from functools import partial
from math import radians, cos, sin, asin, sqrt
from operator import itemgetter
from typing import Any, Callable, Iterable, List, Mapping, Optional, Tuple

from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

# Dependency exists because the Python standard library cannot parse a
# timestamp with a colon in the time zone offset.
from dateutil.parser import parse as date_parse
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from lazy_property import LazyProperty
from requests_futures.sessions import FuturesSession

__all__ = [
    'Location',
    'Client',
    'Truck',
    'lat_long_from_address',
    'humanize_list'
]

GEOLOCATOR = Nominatim(user_agent="seattle-food-truck")
HOST = 'https://www.seattlefoodtruck.com/api/{endpoint}'
IMAGE_HOST = 'https://s3-us-west-2.amazonaws.com/seattlefoodtruck-uploads-prod'
MAX_WORKERS = 25


def lat_long_from_address(address: str) -> Tuple[float]:
    """Find the latitude and longitude of an address.

    Parameters
    ----------
    address : str
        An address on Earth.

    Returns
    -------
    lat_long : tuple of float
        The most likely latitude and longitude of `address`.

    """
    location = GEOLOCATOR.geocode(address)
    assert location != None, f"Could not find a location matching address: {address}"
    return (location.latitude, location.longitude)


def humanize_list(iterable: Iterable[str]) -> str:
    """Return a grammatically correct English phrase of a list of items.

    Parameters
    ----------
    iterable : iterable of str
        Any list of items.

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

    Note
    ----
    Any list with length greater than two will, of course, use an Oxford comma.

    """
    iterable = list(map(str, iterable))
    if len(iterable) == 1:
        return ''.join(iterable)
    elif len(iterable) == 2:
        return ' and '.join(iterable)
    else:
        iterable[-1] = f'and {iterable[-1]}'
        return ', '.join(iterable)


def paginate(
    url: str,
    key: str,
    params: Optional[Mapping]=None,
    func: Callable[[Mapping], Any]=lambda _: _['pagination']['total_pages']
):
    """Get all entries from the API at `url` by pagination over `key`.

    Parameters
    ----------
    url : str
        URL of the API.
    key : str
        The key to access the content from each page.
    func : callable
        How to access the total number of pages from one page's response.

    Returns
    -------
    content : list
        All items found in the given key as a result of pagination.

    """
    content = []
    params = params or {}
    with requests.Session() as s:
        first_page = s.get(url, params={**params, 'page': 1}).json()
        content.extend(first_page.get(key))

    with FuturesSession(executor=ThreadPoolExecutor(MAX_WORKERS)) as s:
        async_jobs = []
        for i in range(2, func(first_page)):
            async_jobs.append(s.get(url, params={**params, 'page': i}))

        for job in as_completed(async_jobs):
            content.extend(job.result().json().get(key))
    return content


class Truck(object):
    """A food truck in Seattle."""

    def __init__(self, mapping: Mapping):
        self.__dict__.update(mapping)

    @property
    def food_description(self) -> str:
        """Return a grammatically correct listing of categorical food items."""
        return humanize_list(self.food_categories)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'"{self.name}", style="{self.food_description}")')


class Location(object):
    """Represents a location where a food truck may appear."""

    def __init__(self, mapping: Mapping):
        self.__dict__.update(mapping)

    @property
    def lat_long(self) -> Tuple[float]:
        """Return the latitude and longitude."""
        return self.latitude, self.longitude

    def distance_from(
        self,
        address: Optional[str]=None,
        lat_long: Optional[Iterable[float]]=None
    ) -> float:
        """The distance in miles between this location and another.

        Parameters
        ----------
        address : str, optional
            The address of the query location.
        lat_long : iterable of floats, optional
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
            raise ValueError('`lat_long` must be an iterable of floats.')
        distance = geodesic(self.lat_long, lat_long).miles
        return distance

    def trucks_on_day(self, date: datetime.date) -> List[Truck]:
        """Returns the food trucks at a given date."""
        assert isinstance(date, datetime.date)

        trucks = []
        for event in Client.events_at_location(self):
            scheduled_date = date_parse(event.get('start_time')).date()

            # Instantiate all trucks that have been booked on this event.
            if date == scheduled_date:
                trucks.extend([Truck(booking['truck']) for
                               booking in event.get('bookings')])

        return trucks

    def trucks_n_days_from_now(self, n: int) -> List[Truck]:
        """Return the food trucks at a given date n days from now."""
        today = datetime.datetime.today().date()
        return self.trucks_on_day(today + datetime.timedelta(days=n))

    def trucks_today(self) -> List[Truck]:
        """Return food trucks scheduled for today."""
        today = datetime.datetime.today().date()
        return self.trucks_on_day(today)

    def trucks_tomorrow(self) -> List[Truck]:
        """Return food trucks scheduled for tomorrow."""
        today = datetime.datetime.today().date()
        return self.trucks_on_day(today + datetime.timedelta(days=1))

    def trucks_yesterday(self) -> List[Truck]:
        """Return yesterday's food trucks."""
        today = datetime.datetime.today().date()
        return self.trucks_on_day(today - datetime.timedelta(days=1))

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'name="{self.name.strip()}", '
            f'address="{self.address}", '
            f'uid={self.uid})')


class Client(object):
    """A representation of the API at www.seattlefoodtrucks.com."""

    def nearest_location_to(
        self,
        address: Optional[str]=None,
        lat_long: Optional[Iterable[float]]=None
    ) -> Location:
        """Find the food truck location closest to the query location.

        Parameters
        ----------
        address : str, optional
            The address of the query location.
        lat_long : iterable of floats, optional
            The latitude and longitude of the query location.

        Returns
        -------
        location : Location
            The food truck location closed to the query location.

        """
        (distance, location), *_ = self.locations_closest_to(
            address=address,
            lat_long=lat_long)

        return location

    def locations_closest_to(
        self,
        address: Optional[str]=None,
        lat_long: Optional[Iterable[float]]=None
    ) -> List[Tuple[float, Location]]:
        """Find the food truck locations closest to the query location.

        Parameters
        ----------
        address : str, optional
            The address of the query location.
        lat_long : tuple of floats, optional
            The latitude and longitude of the query location.

        Returns
        -------
        distance_and_locations : list of (float, Location) tuples
            The distance in miles and food truck location as compared the
            query location.

        """
        if address is None and lat_long is None:
            raise ValueError('`address` or `lat_long` must be specified.')
        elif address is not None:
            lat_long = lat_long_from_address(address)
        elif (
            lat_long is not None and
            not all(isinstance(_, float) for _ in lat_long)
        ):
            raise ValueError('`lat_long` must be an iterable of floats.')

        distance_and_locations = [
            (geodesic(lat_long, location.lat_long).miles, location)
            for location in self.locations
        ]

        return sorted(distance_and_locations, key=itemgetter(0))

    @staticmethod
    def events_at_location(location: Location) -> List[Mapping]:
        """Lists the events at a given location.

        Returns
        -------
        location : Location
            The Location to query.

        """
        params = {
            'for_locations': str(location.uid),
            'with_active_trucks': 'true',
            'include_bookings': 'true',
            'with_booking_status': 'approved'}
        events = paginate(
            HOST.format(endpoint='events'),
            key='events',
            params=params)
        return events

    @LazyProperty
    def locations(self) -> List[Location]:
        """A memoized property of all locations at instantiation time."""
        locations = map(
            Location,
            paginate(HOST.format(endpoint='locations'), key='locations'))
        return list(locations)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'
