import json
import os

from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from dotenv import load_dotenv
from typing import Dict, List
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests import Request, Session

# get the Asset Central config
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
base_url = os.getenv("BASE_URL")
token_url = os.getenv("TOKEN_URL")

def get_oauth_session():
    """call the service to get an OAuth2 token and authenticate"""
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
    return oauth


# should probably refactor this to template (or something like that since it is the template part of the API)
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
        ac_object = json.loads(res.content)[0]
        # model returns modelId instead of id
        if "id" in ac_object:
            ac_id = ac_object["id"]
        else:
            ac_id = ac_object["modelId"]
        exists = True
    except IndexError:
        exists = False
    return res.status_code, exists, ac_id

def model_in_asset_central(internalId: str):
    """ check if model exists in Asset Central
        arguments:
            internalId: string id defined for object
        returns:
            status_code: status code of the request
            exists: True if it is in AC, False if not
            ac_id: asset central id
    """
    query = f"/models?$filter=internalId+eq+'{internalId}'"
    res = get_oauth_session().get(base_url + query)
    ac_id = ""
    try:
        ac_object = json.loads(res.content)[0]
        ac_id = ac_object["modelId"]
        exists = True
    except IndexError:
        exists = False
    return res.status_code, exists, ac_id

def equipment_in_asset_central(internalId: str):
    """ check if equipment exists in Asset Central
        arguments:
            internalId: string id defined for object
        returns:
            status_code: status code of the request
            exists: True if it is in AC, False if not
            ac_id: asset central id
    """
    query = f"/equipment?$filter=internalId+eq+'{internalId}'"
    res = get_oauth_session().get(base_url + query)
    ac_id = ""
    try:
        ac_object = json.loads(res.content)[0]
        ac_id = ac_object["equipmentId"]
        exists = True
    except IndexError:
        exists = False
    return res.status_code, exists, ac_id


# refactor to template as above
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
        # model returns modelId instead of id
        if "id" in res_val:
            return status_code, res_val["id"]
        else:
            return status_code, res_val["modelId"]


# add a similar one for model
def equipment_insert_asset_central(internalId: str, data: str):
    """ insert equipment into Asset Central
        arguments:
            internalId: string id defined for object
            data: string JSON representing the object to be created
    """
    status_code, exists, ac_id = equipment_in_asset_central(internalId)

    if exists:
        raise ElementAlreadyExists
    else:
        s = get_oauth_session()
        res = s.request("POST", base_url+"/equipment", data=data, headers={"Content-Type": "application/json"})
        if res.status_code != 200:
            raise ElementCouldNotBeCreated
        res_val = json.loads(res.content)
        return res_val["equipmentId"]


# refactor to template
def delete_asset_central(path: str, internalId: str):
    """ delete item from Asset Central
        arguments:
            path: string path for AC object (e.g. /indicators)
            internalId: string id for the object
        returns:
            status_code: HTTP code (200 if delete is successful)
            res.content: results from the delete
    """
    status_code, exists, ac_id = in_asset_central(path, internalId)
    if exists:
        res = get_oauth_session().delete(base_url + f"{path}/{ac_id}")
        return res.status_code, json.loads(res.content)
    else:
        raise ElementDoesNotExist


def delete_asset_central_model(internalId: str):
    """ delete model from Asset Central
        arguments:
            internalId: string id for the object
        returns:
            status_code: HTTP code (204 if delete is successful)
    """
    status_code, exists, ac_id = model_in_asset_central(internalId)
    if exists:
        url = base_url + f"/models({ac_id})"
        res = get_oauth_session().delete(url)
        return res.status_code
    else:
        raise ElementDoesNotExist

def delete_asset_central_equipment(internalId: str):
    """ delete equipment from Asset Central
        arguments:
            internalId: string id for the object
        returns:
            status_code: HTTP code (204 if delete is successful)
    """
    status_code, exists, ac_id = equipment_in_asset_central(internalId)
    if exists:
        url = base_url + f"/equipment({ac_id})"
        res = get_oauth_session().delete(url)
        return res.status_code
    else:
        raise ElementDoesNotExist

class ElementAlreadyExists(Exception):
    """ The element specified for insert already exists in asset central """
    pass

class ElementDoesNotExist(Exception):
    """ The element specified does not exist in Asset Central """
    pass

class ElementCouldNotBeCreated(Exception):
    """ The element could not be created (probably an issue with dependency) """
    pass

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

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PrimaryTemplate():
    id: str
    primary: bool = True


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Model():
    descriptions: List[Description]
    internal_id: str
    templates: List[PrimaryTemplate]
    organizationID: str # this is an inconsistent name in the API
    equipment_tracking: str = "1"

    def publish(self):
        _, exists, object_id = model_in_asset_central(self.internal_id)
        if exists:
            url = base_url + f"/models({object_id})/publish"
            res = get_oauth_session().put(url)
            return res.status_code


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Equipment():
    descriptions: List[Description]
    internal_id: str
    operatorID: str
    model_id: str
    model_known: bool = True
    sourceBPRole: str = "1"
    life_cycle: str = "2"



