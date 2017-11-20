Python Library for finding Seattle Food Trucks
---

> Uses the API at www.seattlefoodtruck.com

**Installation**

```bash
pip install git@github.com:clintval/seattle-food-truck.git
```

**Usage**




```python
>>> from seattle_food_truck import SeattleFoodTruckAPI
>>> api = SeattleFoodTruckAPI()
```
```python
>>> address = '3131 Elliot Ave. Seattle Washington'
>>> location = api.location_closest_to(address=address)
>>> print(location)
Location(name="PI Building", address="101 Elliott Ave W, Seattle, WA, United States", uid=69)
```


One thing to note is that a `Location` must be bound to the main class before food trucks can be queried as there are hundreds of food truck bookings and queries across the entire city are quite time-consuming. At this point we must bind the location to the API for subsequent queries on food trucks.

```python
>>> api.location = location
```

```python
>>> api.trucks_tomorrow()
[Truck("Sam Choy's Poke To The Max", style="Hawaiian"),
 Truck("Bumbu Truck", style="Asian")]
```
