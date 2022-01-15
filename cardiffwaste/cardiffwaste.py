"""A module to get waste collection details for addresses in Cardiff, UK."""
from __future__ import annotations

import datetime
import json

import httpx
from bs4 import BeautifulSoup
from getuseragent import UserAgent

from .const import (
    headers_get_jwt,
    headers_get_waste_cookies,
    headers_waste_collections,
    payload_get_jwt,
    payload_waste_collections,
    url_collections,
    url_get_jwt,
)


class WasteCollections:
    """Get and store details of waste collections."""

    def __init__(self, uprn: int | str) -> None:
        """Initiate getter parameters."""

        self._uprn: int = int(uprn) if isinstance(uprn, str) else uprn
        self._user_agent: str = UserAgent("desktop").Random()

    def _get_token(self) -> str:
        """Get an access token."""

        headers_get_jwt["User-Agent"] = self._user_agent
        response = httpx.request(
            "POST", url_get_jwt, headers=headers_get_jwt, data=payload_get_jwt
        )
        xml = BeautifulSoup(response.text, "xml")
        result = json.loads(xml.find("GetJWTResult").get_text())
        return result["access_token"]

    def _get_cookied_session(self) -> httpx.Client:
        """Start a session and collect required cookies."""

        client = httpx.Client()
        headers_get_waste_cookies["User-Agent"] = self._user_agent
        client.request("OPTIONS", url_collections, headers=headers_get_waste_cookies)
        return client

    def get_collections(self) -> NextCollections:
        """Get collection details."""

        client = self._get_cookied_session()
        jwt = self._get_token()
        headers_waste_collections["Authorization"] = f"Bearer {jwt}"
        headers_waste_collections["User-Agent"] = self._user_agent
        payload_waste_collections["uprn"] = self._uprn
        response = client.request(
            "POST",
            url_collections,
            headers=headers_waste_collections,
            data=json.dumps(payload_waste_collections),
        )

        next_collections = NextCollections()

        if response.status_code == 200:
            result = json.loads(response.text)["collectionWeeks"]
            for week in result:
                for collection in week["bins"]:
                    if (
                        collection["type"] == "Recycling"
                        and not next_collections.recycling.loaded
                    ):
                        next_collections.recycling.update(collection, week)
                    if (
                        collection["type"] == "General"
                        and not next_collections.general.loaded
                    ):
                        next_collections.general.update(collection, week)
                    if (
                        collection["type"] == "Food"
                        and not next_collections.food.loaded
                    ):
                        next_collections.food.update(collection, week)
                    if (
                        collection["type"] == "Garden"
                        and not next_collections.garden.loaded
                    ):
                        next_collections.garden.update(collection, week)
            return next_collections
        else:
            raise Exception()


class Bin:
    """Representation of a bin for collection."""

    def __init__(self, bin_type: str) -> None:
        """Initiate an empty bin."""

        self.loaded: bool = False
        self.type: str = bin_type.lower()

    def update(self, collection, week) -> bool:
        """Updates the bin properties from data."""

        self.collection_date = datetime.datetime.strptime(
            week["date"], "%Y-%m-%dT%H:%M:%S"
        ).date()
        collection_type = collection["collectionType"].lower()
        if collection_type == "standard":
            collection_type = "scheduled"
        elif collection_type == "moved":
            collection_type = "rescheduled"
        self.collection_type = collection_type
        self.image = collection["imageUrl"]
        self.loaded = True
        return True


class NextCollections:
    """Representation of a household of bins."""

    def __init__(self) -> None:
        """Initiate household of empty bins."""

        self.general = Bin("general")
        self.recycling = Bin("recycling")
        self.food = Bin("food")
        self.garden = Bin("garden")
