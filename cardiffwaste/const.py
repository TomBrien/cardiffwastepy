# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 12:04:21 2022

@author: tom
"""

from typing import Final

PAYLOAD_GET_JWT: Final[str] = (
    "<?xml version='1.0' encoding='utf-8'?>"
    "<soap:Envelope xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'"
    " xmlns:xsd='http://www.w3.org/2001/XMLSchema'"
    " xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'>"
    "<soap:Body>"
    "<GetJWT xmlns='http://tempuri.org/' />"
    "</soap:Body>"
    "</soap:Envelope>"
)
headers_get_jwt = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "Accept": "*/*",
    "Content-Type": 'text/xml; charset="UTF-8"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://www.cardiff.gov.uk",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.cardiff.gov.uk/",
    "Accept-Language": "en-GB,en;q=0.9",
}

URL_GET_JWT: Final[
    str
] = "https://authwebservice.cardiff.gov.uk/AuthenticationWebService.asmx?op=GetJWT"

URL_COLLECTIONS: Final[
    str
] = "https://api.cardiff.gov.uk/WasteManagement/api/WasteCollection"

headers_get_waste_cookies = {
    "Connection": "keep-alive",
    "Accept": "*/*",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "authorization,content-type",
    "Origin": "https://www.cardiff.gov.uk",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.cardiff.gov.uk/",
    "Accept-Language": "en-GB,en;q=0.9",
    "Host": "api.cardiff.gov.uk",
}

payload_waste_collections = {"systemReference": "web", "language": "eng", "uprn": "000"}

headers_waste_collections = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/json; charset=UTF-8",
    "sec-ch-ua-mobile": "?0",
    "Origin": "https://www.cardiff.gov.uk",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.cardiff.gov.uk/",
    "Accept-Language": "en-GB,en;q=0.9",
}
