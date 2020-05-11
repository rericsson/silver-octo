import json

from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import Dict, List

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests import Request, Session

client_id = 'sb-85c59c29-88eb-40d8-bbbf-ad2d007c92e8!b16149|ac_broker_poc!b1537'
client_secret = 'dvXu5EuQ+M21MOtOF83B550jGZA='
base_url = 'https://ac-poc.cfapps.eu10.hana.ondemand.com/ain/services/api/v1'
token_url = 'https://vestatest.authentication.eu10.hana.ondemand.com/oauth/token'

def get_oauth_session():
    """call the service to get an OAuth2 token and authenticate"""
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
    return oauth

def in_asset_central(path: str, internalId: str):
    """ check if item exists in Asset Central
        arguments:
            path: string path for AC object (e.g. /indicators)
            internalId: string id defined for object
        returns:
            status_code: status code of the request
            exists: True if it is in AC, False if not
            ac_id: asset central id
    """
    query = f"{path}?$filter=internalId+eq+'{internalId}'"
    res = get_oauth_session().get(base_url + query)
    ac_id = ""
    try:
        ac_id = json.loads(res.content)[0]["id"]
        exists = True
    except IndexError:
        exists = False
    return res.status_code, exists, ac_id

def insert_asset_central(path: str, internalId: str, data: str):
    """ insert item into Asset Central
        arguments:
            path: string path for AC object (e.g. /indicators)
            internalId: string id defined for object
            data: string JSON representing the object to be created
    """
    status_code, exists, ac_id = in_asset_central(path, internalId)

    if exists:
        raise ElementAlreadyExists
    else:
        s = get_oauth_session()
        res = s.request("POST", base_url+path, data=data, headers={"Content-Type": "application/json"})
        res_val = json.loads(res.content)
        # template (at least) returns a list from post so need to check if we have a list
        if isinstance(res_val, List):
            return status_code, res_val[0]["id"]
        return status_code, res_val["id"]

def delete_asset_central(path: str, internalId: str):
    status_code, exists, ac_id = in_asset_central(path, internalId)
    if exists:
        res = get_oauth_session().delete(base_url + f"{path}/{ac_id}")
        return res.status_code, json.loads(res.content)
    else:
        raise ElementDoesNotExist


class ElementAlreadyExists(Exception):
    """ The element specified for insert already exists in asset central """
    pass

class ElementDoesNotExist(Exception):
    """ The element specified does not exist in Asset Central """


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Description():
    short: str
    long: str
    language: str = "en"


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IndicatorGroup():
    descriptions: List[Description]
    internal_id: str
    indicators: List[str]

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IndicatorType():
    type: str = "IndicatorType"
    code: str = "1"
    language_iso_code: str = "en"
    description: str = "measured"


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Indicator():
    descriptions: List[Description]
    internal_id: str
    indicator_type: List[IndicatorType]
    data_type: str = "numeric"
    aggregation_concept: str = "6"
    expected_behaviour: str = "3"
    indicator_category: str = "1"

""" used to create required format for indicator and attribute groups """
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IdString():
    id: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Template():
    descriptions: List[Description]
    internal_id: str
    indicator_groups: List[IdString]
    industry_standards: List[str] # will need an object here - this won't be the right json
    attribute_groups: List[IdString]
    type: str = "3"


