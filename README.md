<h1 align="center">seattle-food-truck</h2>

<p align="center">A Python 3.6+ library for discovering Seattle Food Truck schedules</p>

<p align="center">
  <a href="#installation"><strong>Installation</strong></a>
  ·
  <a href="#tutorial"><strong>Tutorial</strong></a>
  ·
  <a href="#command-line-utility"><strong>Command Line Utility</strong></a>
  ·
  <a href="#contributing"><strong>Contributing</strong></a>
</p>

<p align="center">
  <a href="https://badge.fury.io/py/seattle-food-truck"><img src="https://badge.fury.io/py/seattle-food-truck.svg" alt="PyPI version"></img></a>
  <a href="https://codeclimate.com/github/clintval/seattle-food-truck/maintainability"><img src="https://api.codeclimate.com/v1/badges/7f6bfb6d1a887a1ba811/maintainability"></img></a>
  <a href="https://github.com/clintval/seattle-food-truck/blob/master/LICENSE"><img src="https://img.shields.io/pypi/l/seattle-food-truck.svg"></img></a>
</p>

<br>

<h3 align="center">Installation</h3>

```bash
❯ pip install seattle-food-truck
```

<br>

<h3 align="center">Tutorial</h3>

The `Client` allows you to discover convenient or nearby locations where food trucks are scheduled to visit! After finding a suitable `Location` we can query it for a schedule of trucks.

```python
from seattle_food_truck import Client

sft = Client()
```

You can discover locations through listing them all. All locations are memoized once they are discovered to speedup all future queries.

```python
print(f'There are {len(sft.locations)} locations.\n')
print(sft.locations)
```

```
There are 675 locations.

[
  Location(name="Metropolitan Park", address="1100 Olive Way, Seattle, WA, United States", uid=283),
  Location(name="10020 Southeast 256th Street, Kent, WA, USA", address="10020 Southeast 256th Street, Kent, WA, USA", uid=633),
  Location(name="1020 Central Avenue North, Kent, WA, USA", address="1020 Central Avenue North, Kent, WA, USA", uid=866),
  Location(name="10256 16th Avenue Southwest, Seattle, WA, USA", address="10256 16th Avenue Southwest, Seattle, WA, USA", uid=864),
  Location(name="103 110th Ave NE, Bellevue, WA, USA", address="103 110th Ave NE, Bellevue, WA, USA", uid=553),
  Location(name="104 Washington Avenue South, Orting, WA, USA", address="104 Washington Avenue South, Orting, WA, USA", uid=806),
  Location(name="10416 193rd Street Court East, Graham, WA, USA", address="10416 193rd Street Court East, Graham, WA, USA", uid=807),
  ...
]
```

It would be easier if we could sort the list of locations by their proximity to my home or job site!
The `Client` provides two functions for this purpose.

The first discovers all locations ranked by their direct distance away.

```python
address = '3131 Elliott Ave Seattle WA 98121'

for distance, location in sft.locations_closest_to(address):
    print(f'{distance:0.2f} miles away: {location.name}')
    print('\t' + location.address)
```

```
0.11 miles away: PI Building
    101 Elliott Ave W, Seattle, WA, United States
0.27 miles away: Olympic Sculpture Park
    2901 Western Avenue, Seattle, WA, United States
0.43 miles away: F5 Networks
    401 Elliott Ave W, Seattle, WA 98119, United States
0.66 miles away: Memorial Stadium
    401 5th Avenue North, Seattle, WA, United States
...
```

The second simply returns the location nearest to me.

```python
location = sft.nearest_location_to(address)

for truck in location.trucks_today():
    print(truck)
```

```
Truck("NOSH", style="Seafood")
Truck("Raney Brothers BBQ", style="BBQ")
```

<br>

<h3 align="center">Command Line Utility</h3>

A primitive CLI tool is installed with this library.

```bash
$ sft
Usage: sft [OPTIONS] COMMAND [ARGS]...

  Tool to get you the food trucks scheduled near you in Seattle.

Options:
  --help  Show this message and exit.

Commands:
  locations        Print the locations with food truck bookings.
  trucks-today     Print the truck bookings today.
  trucks-tomorrow  Print the truck bookings tomorrow
```

```bash
❯ sft trucks-tomorrow --location-uid 69
Truck("Sam Choy's Poke To The Max", style="Hawaiian")
Truck("Bumbu Truck", style="Asian")
```

<br>

<h3 align="center">Contributing</h3>

Pull requests, feature requests, and issues welcome!

> This library uses the undocumented API at www.seattlefoodtruck.com
