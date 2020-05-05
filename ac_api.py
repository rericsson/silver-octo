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


class ElementAlreadyExists(Exception):
    """ The element specified for insert already exists in asset central """
    pass


@dataclass
class IndicatorGroup:
    descriptions: List[Dict]
    internalId: str

    def in_asset_central(self):
        query = f"/indicatorgroups?$filter=internalId+eq+'{self.internalId}'"
        res = get_oauth_session().get(base_url + query)
        res_list = json.loads(res.content)
        if len(res_list) == 0:
            # not there
            return False
        else:
            # get the id and assign it
            res_val = json.loads(res.content)
            self.id = res_val[0]["id"]
            return True

    def insert_asset_central(self):
        if self.in_asset_central():
            # can't insert
            raise ElementAlreadyExists
        else:
            res = get_oauth_session().post(base_url + "/indicatorgroups", json=self.__dict__)
            res_val = json.loads(res.content)
            self.id = res_val["id"]
            return self.id

    def delete_asset_central(self):
        if self.in_asset_central():
            # delete it
            res = get_oauth_session().delete(base_url + f"/indicatorgroups/{self.id}")
            return res.status_code, json.loads(res.content)
        else:
            raise ElementDoesNotExist

