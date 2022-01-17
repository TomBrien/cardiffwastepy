# cardiffwaste

## About

This is a highly-juvenile package to collect upcoming waste collections for an addresses served by Cardiff Council.

## Installation

```
pip install cardiffwaste
```

## Usage

Currently you are required to know your Unique Property Reference Number (UPRN), this can easily be found on <https://www.findmyaddress.co.uk/search>. The example below uses `123456789012`

```python
from cardiffwaste import WasteCollections

address = WasteCollections(123456789012)
collections = address.get_next_collections()

print(collections["general"]["collection_date"])
# 2022-01-15

```

Four collection types are currently handled, which are `general`, `recycling`, `food`, `garden`. These keys will only be present if a collection is scheduled in the next 4 weeks. For scheduled collections, each collection will have the following keys:

| Attribute | Value Type | Description |
| --- | --- | --- |
| `type` | `str` | The collection type (`general`, `recycling`, `food`, or `garden`) |
| `collection_date` | `datetime.date` | Date of next collection |
| `collection_type` | `str` | `scheduled` or `rescheduled` depending on if planned has been missed |
| `image` | `str` | URL of a representation of the collection type |

## Contributing

My current plans are to get this to what might actually be called a stable state and sort out CI/CD. I also will implement hygiene collection details and perhaps a uprn lookup.
