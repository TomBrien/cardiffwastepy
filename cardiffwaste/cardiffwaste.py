"""A module to get waste collection details for addresses in Cardiff, UK."""
from __future__ import annotations

import datetime
import json
import logging

import httpx
from bs4 import BeautifulSoup
from getuseragent import UserAgent

from .const import (
    PAYLOAD_GET_JWT,
    URL_COLLECTIONS,
    URL_GET_JWT,
    headers_get_jwt,
    headers_get_waste_cookies,
    headers_waste_collections,
    payload_waste_collections,
)

_LOGGER = logging.getLogger(__name__)


class WasteCollections:
    """Get and store details of waste collections."""

    def __init__(self, uprn: int | str) -> None:
        """Initiate getter parameters."""

        self.uprn: int = int(uprn) if isinstance(uprn, str) else uprn
        self._user_agent: str = UserAgent("desktop").Random()
        _LOGGER.debug("Setting fake user agent to: %s", self._user_agent)

    def _get_token(self) -> str:
        """Get an access token."""

        _LOGGER.debug("Requesting JWT")
        headers_get_jwt["User-Agent"] = self._user_agent
        response = httpx.request(
            "POST", URL_GET_JWT, headers=headers_get_jwt, data=PAYLOAD_GET_JWT
        )
        _LOGGER.debug(
            "Completed JWT request with status code: %d", response.status_code
        )
        xml = BeautifulSoup(response.text, "xml")
        result = json.loads(xml.find("GetJWTResult").get_text())
        return result["access_token"]

    def _get_cookied_session(self) -> httpx.Client:
        """Start a session and collect required cookies."""

        client = httpx.Client()
        headers_get_waste_cookies["User-Agent"] = self._user_agent
        _LOGGER.debug("Attempting to get collection cookies")
        client.request("OPTIONS", URL_COLLECTIONS, headers=headers_get_waste_cookies)
        _LOGGER.debug("Received %d cookies", len(client.cookies))
        return client

    def get_raw_collections(self) -> dict:
        """Get all known collections from API and do minimal tidying."""

        jwt = self._get_token()
        client = self._get_cookied_session()
        headers_waste_collections["Authorization"] = f"Bearer {jwt}"
        headers_waste_collections["User-Agent"] = self._user_agent
        payload_waste_collections["uprn"] = self.uprn
        _LOGGER.debug("Attempting to get collection data")
        response = client.request(
            "POST",
            URL_COLLECTIONS,
            headers=headers_waste_collections,
            data=json.dumps(payload_waste_collections),
        )
        _LOGGER.debug(
            "Completed collection data request with status code: %d",
            response.status_code,
        )
        raw = {}
        raw["collections"] = json.loads(response.text)["collectionWeeks"]
        raw["response_code"] = response.status_code
        return raw

    def check_valid_uprn(self) -> bool:
        """Helper to check if UPRN returns valid data."""

        jwt = self._get_token()
        client = self._get_cookied_session()
        headers_waste_collections["Authorization"] = f"Bearer {jwt}"
        headers_waste_collections["User-Agent"] = self._user_agent
        payload_waste_collections["uprn"] = self.uprn

        _LOGGER.debug("Attempting validation check")

        response = client.request(
            "POST",
            URL_COLLECTIONS,
            headers=headers_waste_collections,
            data=json.dumps(payload_waste_collections),
        )

        _LOGGER.debug(
            "Completed validation check with status code: %d", response.status_code
        )

        return bool(response.status_code == 200 and "collectionWeeks" in response.text)

    def get_next_collections(self) -> dict:
        """Get collection details and return in."""

        _LOGGER.debug("Starting sorting bins")

        next_collections = {}

        response = self.get_raw_collections()

        if response["response_code"] == 200:
            for week in response["collections"]:
                for collection in week["bins"]:
                    if not next_collections.get(collection["type"].lower()):
                        _LOGGER.debug(
                            "Adding next %s collection to output", collection["type"]
                        )
                        next_collections[collection["type"].lower()] = _tidy_bins(
                            collection, week
                        )
                    else:
                        _LOGGER.debug(
                            "Not adding %s collection to output as "
                            "type is already present",
                            collection["type"],
                        )

        _LOGGER.debug("Completed sorting bins")

        return next_collections


def _tidy_bins(collection: dict, week: dict) -> dict:
    """Generates a useful dictionary of bin collection details from raw response."""

    _LOGGER.debug(
        "Sorting %s bin with "
        "collection date: %s, "
        "collection type: %s and "
        "image %s",
        collection["type"],
        week["date"],
        collection["collectionType"],
        collection["imageUrl"],
    )

    sorted_bin: dict = {}
    sorted_bin["date"] = datetime.datetime.strptime(
        week["date"], "%Y-%m-%dT%H:%M:%S"
    ).date()
    sorted_bin["type"] = collection["collectionType"].lower()
    if sorted_bin["type"] == "standard":
        sorted_bin["type"] = "scheduled"
    elif sorted_bin["type"] == "moved":
        sorted_bin["type"] = "rescheduled"
    sorted_bin["image"] = collection["imageUrl"]
    return sorted_bin
