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
class Dimension():
    dimensionId: str = ""
    dimensionExternalId: str = ""
    unitId: str = ""
    unitExternalId: str = ""
    dimensionDescription: str = ""
    unitShortDescription: str = ""
    unitLongDescription: str = ""
    unitIsoCode: str = ""

def load_dimensions():
    url = base_url + f"/uom/dimensions?isFlat=true"
    res = get_oauth_session().get(url)
    # if we get a successful result, load the list
    if res.status_code == 200:
        dims = res.json()
        return [Dimension(**d) for d in dims]
    else:
        raise ValueError


@dataclass_json
@dataclass
class Description():
    """ Description used in all of the AC objects
    Attributes:
        short description
        long description
    """
    short: str = ""
    long: str = ""


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
class Indicator():
    """ Indicator as defined in AC

    The fields are best defined in AC and can mirrored here

    """
    id: str = ""
    internalId: str = ""
    description: Description = Description
    indicatorType: List[IndicatorType] = field(default_factory=indicator_type_factory)
    dataType: str = "numeric"
    aggregationConcept: str = "6"
    expectedBehaviour: str = "3"
    indicatorCategory: str = "1"
    indicatorColorCode: str = ""
    dimension1: str = ""
    indicatorUom: str = ""

    def insert(self):
        """ inserts the indicator into AC """
        url = base_url + "/indicators"
        # modify schema to not serialize dimension1 and indicatorUom unless both are populated (fails on insert)
        exclude = ["id", "dimension1", "indicatorUom"]
        if self.dimension1 and self.indicatorUom:
            exclude = ["id"]
        schema = self.schema(exclude=exclude)
        data = schema.dumps(self)
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
            # modify schema to not serialize dimension1 and indicatorUom unless both are populated
            exclude = ["dimension1", "indicatorUom"]
            if self.dimension1 and self.indicatorUom:
                exclude = []
            schema = self.schema(exclude=exclude)
            data = schema.dumps(self)
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
class IndicatorGroup():
    id: str = ""
    internalId: str = ""
    description: Description = Description
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
class Template():
    id: str = ""
    internalId: str = ""
    description: Description = Description
    indicatorGroups: List[IdString] = field(default_factory=list)
    industryStandards: List[str] = field(default_factory=list)
    attributeGroups: List[IdString] = field(default_factory=list)
    type: str = "3"
    parentId: str = ""
    source: str = ""
    isSourceActive: str = ""
    shortDescription: str = ""
    createdOn: str = ""
    changedOn: str = ""
    sourceSearchTerms: str = ""
    noOfChildCategory: str = ""
    noOfModels: str = ""
    standardIDs: str = ""
    typeCode: str = ""

    def insert(self):
        """ inserts the template into AC """
        url = base_url + "/templates"
        # modify schema to not serialize unecessary fields
        schema = self.schema(only=["internalId", "description", "attributeGroups",
            "indicatorGroups", "type"])
        data = schema.dumps(self)
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
        if res.status_code == 200:
            d = res.json()[0]
            return Template(**d)
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
class Model():
    internalId: str = ""
    description: str = ""
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
    #class: str = "" - this is part of the AC model, but breaks serialization because it is a Python keyword
    image: str = ""
    isClientValid: bool = True
    consume: str = ""

    def publish(self):
        """ publish the model so that equipment can be added
            need to have the id from AC
        """
        if self.modelId:
            url = base_url + f"/models({self.modelId})/publish"
            res = get_oauth_session().put(url)
            return res.status_code
        else:
            raise ValueError

    def insert(self):
        """ inserts the model into AC """
        url = base_url + "/models"
        # modify schema to not serialize unecessary fields
        schema = self.schema(only=["internalId", "description", "templates",
            "organizationID", "equipmentTracking"])
        data = schema.dumps(self)
        s = get_oauth_session()
        res = s.request("POST", url, data=data, headers={"Content-Type": "application/json"})
        status_code = res.status_code
        res_val = res.json()
        self.modelId = res_val["modelId"]
        return status_code

    def update(self):
        """ updates the model in AC """
        raise NotImplementedError

    def delete(self):
        """ deletes the model from AC """
        if self.modelId:
            url = base_url + f"/models({self.modelId})"
            res = get_oauth_session().delete(url)
            if res.status_code == 204:
                self.modelId = ""
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
            # might be able to find a workaroud to load
            # could rename to class_ and change the name back on serialization
            d.pop("class")
            return Model(**d)
        else:
            raise ValueError

@dataclass_json
@dataclass
class Equipment():
    equipmentId: str = ""
    description: Description = Description
    internalId: str = ""
    operatorID: str = ""
    modelId: str = ""
    modelKnown: bool = True
    sourceBPRole: str = "1"
    lifeCycle: str = "2"
    name: str = ""
    status: str = ""
    statusDescription: str = ""
    version: float = 0.0
    hasInRevision: str = ""
    modelName: str = ""
    shortDescription: str = ""
    templateId: str = ""
    subclass: str = ""
    modelTemplate: str = ""
    location: str = ""
    criticalityCode: str = ""
    criticalityDescription: str = ""
    manufacturer: str = ""
    completeness: float = 0.0
    createdOn: str = ""
    changedOn: str = ""
    publishedOn: str = ""
    serialNumber: str = ""
    batchNumber: str = ""
    tagNumber: str = ""
    lifeCycleDescription: str = ""
    source: str = ""
    imageURL: str = ""
    operator: str = ""
    coordinates: str = ""
    installationDate: str = ""
    equipmentStatus: str = ""
    buildDate: str = ""
    isOperatorValid: str = ""
    modelVersion: float = 0.0
    soldTo: str = ""
    image: str = ""
    consume: str = ""
    dealer: str = ""
    serviceProvider: str = ""
    primaryExternalId: str = ""
    equipmentSearchTerms: str = ""
    sourceSearchTerms: str = ""
    manufacturerSearchTerms: str = ""
    operatorSearchTerms: str = ""

    def insert(self):
        """ inserts the equipment  into AC """
        url = base_url + "/equipment"
        # modify schema to not serialize unecessary fields
        schema = self.schema(only=["internalId", "modelId", "sourceBPRole", "modelKnown",
            "lifeCycle", "description", "operatorID"])
        data = schema.dumps(self)
        s = get_oauth_session()
        res = s.request("POST", url, data=data, headers={"Content-Type": "application/json"})
        status_code = res.status_code
        res_val = res.json()
        self.equipmentId = res_val["equipmentId"]
        return status_code

    def update(self):
        """ updates the equipment in AC """
        raise NotImplementedError

    def delete(self):
        """ deletes the equipment from AC """
        if self.equipmentId:
            url = base_url + f"/equipment({self.equipmentId})"
            res = get_oauth_session().delete(url)
            if res.status_code == 204:
                self.modelId = ""
            return res.status_code
        else:
            raise ValueError

    @classmethod
    def load(cls, internal_id: str):
        """ load an equiment from AC
            arguments:
                internal_id: the internal id for the model
        """
        url = base_url + f"/equipment?$filter=internalId+eq+'{internal_id}'"
        res = get_oauth_session().get(url)
        if res.status_code == 200:
            d = res.json()[0]
            # remove class as it kills serialization
            # might be able to find a workaroud to load
            # could rename to class_ and change the name back on serialization
            d.pop("class")
            return Equipment(**d)
        else:
            raise ValueError

class ElementAlreadyExists(Exception):
    """ The element specified for insert already exists in asset central """
    pass

class ElementDoesNotExist(Exception):
    """ The element specified does not exist in Asset Central """
    pass

class ElementCouldNotBeCreated(Exception):
    """ The element could not be created (probably an issue with dependency) """
    pass





