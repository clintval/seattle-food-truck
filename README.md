Python Library for finding Seattle Food Trucks
---

> Uses the API at www.seattlefoodtruck.com

**Installation**

```bash
pip install seattle-food-truck
```

**Usage**

```python
from seattle_food_truck import Client

location = Client().nearest_location_to('3131 Elliot Ave. Seattle WA')

for truck in location.trucks_today():
    print(truck)
```

```
Truck("NOSH", style="Seafood")
Truck("Raney Brothers BBQ", style="BBQ")
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
