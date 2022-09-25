"""Initiate directory"""
from json import JSONDecodeError

from cardiffwaste.cardiffwaste import (
    ConnectionError,
    DecodeFailed,
    EmptyMatches,
    Timeout,
    WasteCollections,
    address_search,
)

__version__ = "0.2.5"
