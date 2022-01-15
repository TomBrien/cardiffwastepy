# cardiffwaste

## About

This is a highly-juvenile package to collect upcoming waste collections for an addresses served by Cardiff Council.

## Installation

'''
pip install cardiffwaste
'''

## Usage

Currently you are required to know your Unique Property Reference Number (UPRN), this can easily be found on <https://www.findmyaddress.co.uk/search>. The example below uses `123456789012`

```python
from cardiffwaste import WasteCollections

address = WasteCollections(123456789012)
collections = address.get_collections()

print(collections.general.collection_date)
# 2022-01-15

```

Four collection types are currently handled, which are `general`, `recycling`, `food`, `garden`. If a collection date was found, each collection type will have the `loaded` attribute set to `True`. `loaded = False` means no collection is scheduled. For scheduled collections, each collection will have the following attributes:

| Attribute | Type | Description | Only present when loaded |
| --- | --- | --- |--- |
| `loaded` | `bool` | Indicates if collection details were found | No |
| `type` | `str` | The collection type (`general`, `recycling`, `food`, or `garden`) | No |
| `collection_date` | `datetime.date` | Date of next collection | Yes |
| `collection_type` | `str` | `scheduled` or `rescheduled` depending on if planned has been missed | Yes |
| `image` | `str` | URL of a representation of the collection type | Yes |