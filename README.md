# cardiffwaste

## About

This is a simple package to collect upcoming waste collections for an addresses served by Cardiff Council.

## Installation

```
pip install cardiffwaste
```

## Usage

### Getting Collections

Getting collections requires your Unique Property Reference Number (UPRN), the example below uses `123456789012`. If you don't know this (highly likely), you can use the `address_search` helper to look up the UPRN as decribed [below](#address-search)

```python
from cardiffwaste import WasteCollections

address = WasteCollections(123456789012)
collections = address.get_next_collections()

print(collections["general"]["collection_date"])
# 2022-01-15

```

Five collection types are currently handled, which are `general`, `recycling`, `food`, `garden` and `hygiene`. These keys will only be present if a collection is scheduled in the next 4 weeks. For scheduled collections, each collection will have the following keys:

| Attribute | Value Type | Description |
| --- | --- | --- |
| `type` | `str` | The collection type (`general`, `recycling`, `food`, or `garden`) |
| `collection_date` | `datetime.date` | Date of next collection |
| `collection_type` | `str` | `scheduled` or `rescheduled` depending on if planned has been missed |
| `image` | `str` | URL of a representation of the collection type |


### Address Search

You can find your UPRN using the `address_search` helper. This takes any reasonable string describing the address, such as a post code, and returns a dictionary of possible matches. The returned dictionary is of the form `{int(UPRN): str(address_description)}`

The helper can be called as follows:

```python
from cardiffwaste import address_search

address_search("CF10 1AA")

# returns: 
# {10090717081: 'Flat 1, 22 St Mary Street, Cathays, Cardiff, CF10 1AA',
#  10090717082: 'Flat 2, 22 St Mary Street, Cathays, Cardiff, CF10 1AA',
#  10090717083: 'Flat 3, 22 St Mary Street, Cathays, Cardiff, CF10 1AA',
#  10090717084: 'Flat 4, 22 St Mary Street, Cathays, Cardiff, CF10 1AA',
#  10095459274: 'Managers Flat, Cardiff Cottage, 25 St Mary Street, Cathays,  Cardiff, CF10 1AA'}

address_search("mansion house")
# returns:
# {10003566863: 'First Floor Flat, Mansion House, Richmond Road, Roath, Cardiff, CF24 3UN',
#  10003566864: 'First Floor Rear, Mansion House, Richmond Road, Roath, Cardiff, CF24 3UN',
#  10003566865: 'Second Floor, Mansion House, Richmond Road, Roath, Cardiff, CF24 3UN',
#  200002933742: 'Mansion Shand House, 20 Newport Road, Adamsdown, Cardiff, CF24 0DB'}
```



## Contributing

My current plans are to get this to what might actually be called a stable state and sort out CI.
