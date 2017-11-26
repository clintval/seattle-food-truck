Python Library for finding Seattle Food Trucks
---

> Uses the API at www.seattlefoodtruck.com

**Installation**

```bash
pip install seattle-food-truck
```

**Usage**

```python
>>> from seattle_food_truck import SeattleFoodTruckClient
>>> client = SeattleFoodTruckAPI()
```
```python
>>> address = '3131 Elliot Ave. Seattle Washington'
>>> location = client.location_closest_to(address=address)
>>> print(location)
Location(name="PI Building", address="101 Elliott Ave W, Seattle, WA, United States", uid=69)
```


One thing to note is that a `Location` must be bound to the main class before food trucks can be queried as there are hundreds of food truck bookings and queries across the entire city are quite time-consuming. At this point we must bind the location to the API for subsequent queries on food trucks.

```python
>>> client.location = location
```

```python
>>> client.trucks_tomorrow()
[Truck("Sam Choy's Poke To The Max", style="Hawaiian"),
 Truck("Bumbu Truck", style="Asian")]
```


**CLI Utility**

A primitive CLI tool is installed with this library. It works similary to the Python client.

```bash
$ sft
Usage: sft [OPTIONS] COMMAND [ARGS]...

  Tool to get you the food trucks scheduled near you in Seattle.

Options:
  --help  Show this message and exit.

Commands:
  locations        Print the locations with food truck bookings.
  trucks_today     Print the truck bookings today.
  trucks_tomorrow  Print the truck bookings tomorrow
```

```bash
$ sft trucks_tomorrow --location-uid 69
Truck("Sam Choy's Poke To The Max", style="Hawaiian")
Truck("Bumbu Truck", style="Asian")
```
