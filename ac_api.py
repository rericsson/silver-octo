import json
import os

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from dotenv import load_dotenv
from typing import Dict, List
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests import Request, Session
from marshmallow import Schema, fields

# get the Asset Central config
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
base_url = os.getenv("BASE_URL")
token_url = os.getenv("TOKEN_URL")


def get_oauth_session():
    """call the service using the config to get an OAuth2 token and authenticate"""
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
    return oauth


@dataclass_json
@dataclass
class Description():
    """ Description used in all of the AC objects
    Attributes:
        short description
        long description
        language
    """
    short: str
    long: str

@dataclass_json
@dataclass
class Definition:
    """ Root class for all of the AC objects

    Uses camelCase for easier serialization

    Attributes:
        internalId - user defined id on AC
        description - description object
        id - AC defined id. Used to understand if object has been created in AC or not
    """
    internalId: str
    description: Description
    id: str = ""


@dataclass_json
@dataclass
class IndicatorType():
    """ Indicator class used in the indicator definition """
    type: str = "IndicatorType"
    code: str = "1"
    languageIsoCode: str = "en"
    description: str = "measured"

def indicator_type_factory():
    """ generates default list for indicator """
    return [IndicatorType()]

@dataclass_json
@dataclass
class Indicator(Definition):
    """ Indicator as defined in AC

    The fields are best defined in AC and can mirrored here

    """
    indicatorType: List[IndicatorType] = field(default_factory=indicator_type_factory)
    dataType: str = "numeric"
    aggregationConcept: str = "6"
    expectedBehaviour: str = "3"
    indicatorCategory: str = "1"

    def insert(self):
        """ inserts the indicator into AC """
        url = base_url + "/indicators"
        data = self.to_json()
        s = get_oauth_session()
        res = s.request("POST", url, data=data, headers={"Content-Type": "application/json"})
        status_code = res.status_code
        res_val = json.loads(res.content)
        self.id = res_val["id"]
        return status_code

    def update(self):
        """ updates the indicator in AC """
        if self.id:
            url = base_url + f"/indicators/{self.id}"
            data = self.to_json()
            s = get_oauth_session()
            res = s.request("PUT", url, data=data, headers={"Content-Type": "application/json"})
            status_code = res.status_code
            return status_code
        else:
            raise ValueError

    def delete(self):
        """ deletes the indicator from AC """
        if self.id:
            url = base_url + f"/indicators/{self.id}"
            res = get_oauth_session().delete(url)
            if res.status_code == 200:
                self.id = ""
            return res.status_code
        else:
            raise ValueError

    @classmethod
    def load(cls, internal_id: str):
        """ load an indicator from AC
            arguments:
                internal_id: the internal id for the indicator
        """
        url = base_url + f"/indicators?$filter=internalId+eq+'{internal_id}'"
        res = get_oauth_session().get(url)
        # if we get a successful result and the internalId matches then we load the indicator
        if res.status_code == 200:
            d = res.json()[0]
            return Indicator(**d)
        else:
            raise ValueError

@dataclass_json
@dataclass
class IdString():
    """ hack used to create required format for indicator and attribute groups """
    id: str

@dataclass_json
@dataclass
class IndicatorGroup(Definition):
    indicators: List[str] = field(default_factory=list)

    def insert(self):
        """ inserts the indicator group into AC """
        url = base_url + "/indicatorgroups"
        data = self.to_json()
        s = get_oauth_session()
        res = s.request("POST", url, data=data, headers={"Content-Type": "application/json"})
        status_code = res.status_code
        res_val = json.loads(res.content)
        self.id = res_val["id"]
        return status_code

    def update(self):
        """ updates the indicator group in AC """
        if self.id:
            url = base_url + f"/indicatorgroups/{self.id}"
            data = self.to_json()
            s = get_oauth_session()
            res = s.request("PUT", url, data=data, headers={"Content-Type": "application/json"})
            status_code = res.status_code
            return status_code
        else:
            raise ValueError

    def delete(self):
        """ deletes the indicator group from AC """
        if self.id:
            url = base_url + f"/indicatorgroups/{self.id}"
            res = get_oauth_session().delete(url)
            if res.status_code == 200:
                self.id = ""
            return res.status_code
        else:
            raise ValueError

    @classmethod
    def load(cls, internal_id: str):
        """ load an indicator group from AC
            arguments:
                internal_id: the internal id for the indicator group
        """
        url = base_url + f"/indicatorgroups?$filter=internalId+eq+'{internal_id}'"
        res = get_oauth_session().get(url)
        if res.status_code == 200:
            d = res.json()[0]
            return IndicatorGroup(**d)
        else:
            raise ValueError

@dataclass_json
@dataclass
class Template(Definition):
    indicatorGroups: List[IdString] = field(default_factory=list)
    industryStandards: List[str] = field(default_factory=list)
    attributeGroups: List[IdString] = field(default_factory=list)
    type: str = "3"


    def insert(self):
        """ inserts the template into AC """
        url = base_url + "/templates"
        data = self.to_json()
        s = get_oauth_session()
        res = s.request("POST", url, data=data, headers={"Content-Type": "application/json"})
        status_code = res.status_code
        res_val = json.loads(res.content)
        self.id = res_val[0]["id"]
        return status_code

    def update(self):
        """ updates the template in AC """
        if self.id:
            url = base_url + f"/templates/{self.id}"
            data = self.to_json()
            s = get_oauth_session()
            res = s.request("PUT", url, data=data, headers={"Content-Type": "application/json"})
            status_code = res.status_code
            return status_code
        else:
            raise ValueError

    def delete(self):
        """ deletes the templates from AC """
        if self.id:
            url = base_url + f"/templates/{self.id}"
            res = get_oauth_session().delete(url)
            if res.status_code == 200:
                self.id = ""
            return res.status_code
        else:
            raise ValueError

    @classmethod
    def load(cls, internal_id: str):
        """ load an template from AC
            arguments:
                internal_id: the internal id for the template
        """
        url = base_url + f"/templates?$filter=internalId+eq+'{internal_id}'"
        res = get_oauth_session().get(url)
        # if we get a successful result and the internalId matches then we load the template
        if res.status_code == 200:
            # AC is not consistent in format: the descriptions are just properties not an object
            # The returned dictionary has to be hacked up to manually create the template. Ugh.
            d = res.json()[0]
            description = Description(d["shortDescription"], d["description"])
            template = Template(internalId=d["internalId"], description=description, id=d["id"] )
            return template
        else:
            raise ValueError

@dataclass_json
@dataclass
class PrimaryTemplate():
    id: str
    primary: bool = True

def primary_template_factory():
    return [PrimaryTemplate("")]


@dataclass_json
@dataclass
class Model(Definition):
    templates: List[PrimaryTemplate] = field(default_factory=primary_template_factory)
    organizationID: str = ""
    equipmentTracking: str = "1"
    modelId: str = ""
    name: str = ""
    status: str = ""
    version: int = 0
    hasInRevision: str = ""
    templateId: str = ""
    modelTemplate: str = ""
    subclass: str = ""
    generation: int = 0
    manufacturer: str = ""
    shortDescription: str = ""
    longDescription: str = ""
    completeness: int = 0
    createdOn: str = ""
    changedOn: str = ""
    imageURL: str = ""
    publishedOn: str = ""
    source: str = ""
    serviceExpirationDate: str = ""
    modelExpirationDate: str = ""
    releaseDate: str = ""
    isManufacturerValid: bool = True
    primaryExternalId: str = ""
    modelSearchTerms: str = ""
    sourceSearchTerms: str = ""
    manufacturerSearchTerms: str = ""
    #class: str = ""
    image: str = ""
    isClientValid: bool = True
    consume: str = ""

    def publish(self):
        """ publish the model so that equipment can be added
            need to have the id from AC
        """
        if self.id:
            url = base_url + f"/models({self.id})/publish"
            res = get_oauth_session().put(url)
            return res.status_code
        else:
            raise ValueError

    def insert(self):
        """ inserts the model into AC """
        url = base_url + "/models"
        # modify schema to get not serialize unecessary fields
        schema = self.schema(exclude=["internalId", "description", "templates",
            "organizationID", "equipmentTracking"])
        data = schema.dumps(self)
        s = get_oauth_session()
        res = s.request("POST", url, data=data, headers={"Content-Type": "application/json"})
        status_code = res.status_code
        res_val = res.json()
        print(res_val)
        self.id = res_val["modelId"]
        return status_code

    def update(self):
        """ updates the model in AC """
        raise NotImplementedError

    def delete(self):
        """ deletes the model from AC """
        if self.id:
            url = base_url + f"/models({self.id})"
            res = get_oauth_session().delete(url)
            if res.status_code == 204:
                self.id = ""
            return res.status_code
        else:
            raise ValueError

    @classmethod
    def load(cls, internal_id: str):
        """ load an model from AC
            arguments:
                internal_id: the internal id for the model
        """
        url = base_url + f"/models?$filter=internalId+eq+'{internal_id}'"
        res = get_oauth_session().get(url)
        if res.status_code == 200:
            d = res.json()[0]
            # remove class as it kills serialization
            # the design is inconsistent
            # might be able to find a workaroud to load
            d.pop("class")
            print(d)
            return Model(**d)
        else:
            raise ValueError




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


@dataclass_json
@dataclass
class Equipment():
    descriptions: List[Description]
    internal_id: str
    operatorID: str
    model_id: str
    model_known: bool = True
    sourceBPRole: str = "1"
    life_cycle: str = "2"



