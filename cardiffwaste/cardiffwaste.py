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
    URL_SEARCH,
    headers_get_jwt,
    headers_get_search_cookies,
    headers_get_waste_cookies,
    headers_search,
    headers_waste_collections,
    payload_search,
    payload_waste_collections,
)

_LOGGER = logging.getLogger(__name__)


def _get_cookied_search_session(user_agent) -> httpx.Client:
    """Start a session and collect required cookies for searches."""

    client = httpx.Client(timeout=120)
    headers_get_waste_cookies["User-Agent"] = user_agent
    _LOGGER.debug("Attempting to get collection cookies")
    client.request("OPTIONS", URL_SEARCH, headers=headers_get_search_cookies)
    _LOGGER.debug("Received %d cookies", len(client.cookies))
    return client


def _get_token(user_agent) -> str:
    """Get an access token."""

    _LOGGER.debug("Requesting JWT")
    headers_get_jwt["User-Agent"] = user_agent
    try:
        response = httpx.request(
            "POST", URL_GET_JWT, headers=headers_get_jwt, data=PAYLOAD_GET_JWT
        )
    except httpx.ConnectError as connection_error:
        _LOGGER.error("Unable to connect to %s", URL_GET_JWT)
        raise ConnectionError(
            f"Unable to connect to {URL_GET_JWT} with user agent {user_agent}"
        ) from connection_error
    _LOGGER.debug("Completed JWT request with status code: %d", response.status_code)
    xml = BeautifulSoup(response.text, "xml")
    try:
        result = json.loads(xml.find("GetJWTResult").get_text())
    except json.JSONDecodeError as json_error:
        _LOGGER.error("Unable to decode JWT response")
        raise DecodeFailed(
            f"Unable to decode JWT response, user agent was {user_agent}"
        ) from json_error
    return result["access_token"]


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
    sorted_bin["last_update_utc"] = datetime.datetime.utcnow()
    return sorted_bin


def address_search(search_term: str) -> dict[int, str]:
    """Helper to return UPRN matches from a partial address."""

    user_agent = UserAgent("desktop").Random()

    _LOGGER.debug("Setting fake user agent to %s for address search", user_agent)

    jwt = _get_token(user_agent)
    client = _get_cookied_search_session(user_agent)
    headers_search["Authorization"] = f"Bearer {jwt}"
    headers_search["User-Agent"] = user_agent
    payload_search["searchTerm"] = search_term

    _LOGGER.debug("Searching for address %s", search_term)
    try:
        response = client.request(
            "POST",
            URL_SEARCH,
            headers=headers_search,
            data=json.dumps(payload_search),
        )
        _LOGGER.debug("Completed search with status code: %d", response.status_code)
    except httpx.ReadTimeout as search_timed_out:
        _LOGGER.warning("Timed out searching for address %s", search_term)
        raise Timeout(
            f"Timed out searching for address {search_term}"
        ) from search_timed_out

    if response.status_code == 204:
        raise EmptyMatches(message=f"No matches for {search_term}")

    matches = {
        address["uprn"]: address["fullAddress"] for address in json.loads(response.text)
    }

    _LOGGER.debug("Found %d matches", len(matches))

    return matches


class WasteCollections:
    """Get and store details of waste collections."""

    def __init__(self, uprn: int | str) -> None:
        """Initiate getter parameters."""

        self.uprn: int = int(uprn) if isinstance(uprn, str) else uprn
        self._user_agent: str = UserAgent("desktop").Random()
        _LOGGER.debug("Setting fake user agent to: %s", self._user_agent)
        self._bin_store: dict[str, dict] = {}

    def _get_cookied_collection_session(self) -> httpx.Client:
        """Start a session and collect required cookies for collection."""

        client = httpx.Client(timeout=120)
        headers_get_waste_cookies["User-Agent"] = self._user_agent
        _LOGGER.debug("Attempting to get collection cookies")
        client.request("OPTIONS", URL_COLLECTIONS, headers=headers_get_waste_cookies)
        _LOGGER.debug("Received %d cookies", len(client.cookies))
        return client

    def get_raw_collections(self) -> dict:
        """Get all known collections from API and do minimal tidying."""

        jwt = _get_token(self._user_agent)
        client = self._get_cookied_collection_session()
        headers_waste_collections["Authorization"] = f"Bearer {jwt}"
        headers_waste_collections["User-Agent"] = self._user_agent
        payload_waste_collections["uprn"] = self.uprn
        _LOGGER.debug("Attempting to get collection data")
        try:
            response = client.request(
                "POST",
                URL_COLLECTIONS,
                headers=headers_waste_collections,
                data=json.dumps(payload_waste_collections),
            )
        except httpx.ReadTimeout as err:
            raise Timeout(message="Timed out reading response") from err

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

        jwt = _get_token(self._user_agent)
        client = self._get_cookied_collection_session()
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
        try:
            response = self.get_raw_collections()
        except Timeout as err:
            _LOGGER.warning(
                "Timed out getting collection data with error: %s, "
                "using stored data,",
                err,
            )
            return self._bin_store

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

        self._bin_store = next_collections

        return next_collections


class EmptyMatches(Warning):
    """A warning to raise in case of no search matches."""

    def __init__(self, message="No matches found"):
        super().__init__(message)


class Timeout(Exception):
    """A class to report a timeout issue."""

    def __init__(self, message="Timed out searching address"):
        super().__init__(message)


class DecodeFailed(Exception):
    """A class to report a timeout issue."""

    def __init__(self, message="Failed to decode JSON"):
        super().__init__(message)


class ConnectionError(Exception):
    """A class to report a connection issue."""

    def __init__(self, message="Failed to connect to API"):
        super().__init__(message)
