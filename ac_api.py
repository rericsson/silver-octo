import json

from dataclasses import dataclass
from typing import Dict, List

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

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
    """ check if item exists in Asset Central """
    query = f"{path}?$filter=internalId+eq+'{internalId}'"
    res = get_oauth_session().get(base_url + query)
    try:
        ac_id = json.loads(res.content)[0]["id"]
    except IndexError:
        ac_id = False
    return res.status_code, ac_id

def insert_asset_central(path: str, internalId: str, item: Dict):
    """ insert item into Asset Central """
    status_code, exists = in_asset_central(path, internalId)

    if exists:
        raise ElementAlreadyExists
    else:
        res = get_oauth_session().post(base_url + path, json=item)
        res_val = json.loads(res.content)
        return status_code, res_val["id"]

def delete_asset_central(path: str, internalId: str):
    status_code, ac_id = in_asset_central(path, internalId)
    if ac_id:
        res = get_oauth_session().delete(base_url + f"{path}/{ac_id}")
        return res.status_code, json.loads(res.content)
    else:
        raise ElementDoesNotExist


class ElementAlreadyExists(Exception):
    """ The element specified for insert already exists in asset central """
    pass

class ElementDoesNotExist(Exception):
    """ The element specified does not exist in Asset Central """


@dataclass
class IndicatorGroup:
    descriptions: List[Dict]
    internalId: str


