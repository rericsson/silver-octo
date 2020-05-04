import json

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

client_id = 'sb-85c59c29-88eb-40d8-bbbf-ad2d007c92e8!b16149|ac_broker_poc!b1537'
client_secret = 'dvXu5EuQ+M21MOtOF83B550jGZA='
base_url = 'https://ac-poc.cfapps.eu10.hana.ondemand.com/ain/services/api/v1'
token_url = 'https://vestatest.authentication.eu10.hana.ondemand.com/oauth/token'

indicator_group =  {
        "descriptions": [
            {
                "short": "Indicator Group from API",
                "long": "Indicator Group from API long description",
                "language": "en"
            }
        ],
        "internalId": "IndicatorGroupAPI",
    }



group = {
        "id": "353E907744CF4DCFB791E53CEC2BE8ED",
        "groupType": ["GEN"],
        "shortDescription": "new short description",
        "longDescription": "new long description",
        "businessObjectTypes": ["EQU", "FL"],
        "descriptions": [
                {
                "languageISOCode": "en",
                "shortDescription": "new en-short",
                "longDescription": "new en-long"
                }
            ]
        }


def json_print(json_str: str):
    json_object = json.loads(json_str)
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)

client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
assert(oauth.authorized)

# this group code worked
#group_create = oauth.post(base_url + '/groups', json=group)
#print(group_create.content)

#group_put = oauth.put(base_url + '/groups', json=group)
#assert(group_put.status_code == 200)
#json_print(group_put.content)
#
#group_list = oauth.get(base_url + '/groups')
#assert(group_list.status_code == 200)
#json_print(group_list.content)

# get the initial indicator group count
indicator_group_res = oauth.get(base_url + '/indicatorgroups/$count')
assert(indicator_group_res.status_code == 200)
print(f"there are {indicator_group_res.text} indicator groups")

# create a new indicator group
indicator_group_res = oauth.post(base_url + '/indicatorgroups', json=indicator_group)
assert(indicator_group_res.status_code == 200)
json_print(indicator_group_res.content)


# get the indicator group named IndicatorGroupAPI
#indicator_group_res = oauth.get(base_url + "/indicatorgroups?$filter=(substringof('IndicatorGroupAPI', internalId) eq true)")
indicator_group_res = oauth.get(base_url + "/indicatorgroups?$filter=internalId+eq+'IndicatorGroupAPI'")
assert(indicator_group_res.status_code == 200)
ig = json.loads(indicator_group_res.content)
for i in ig:
    print(f"deleting {i['id']}")
    indicator_group_id = i["id"]

#delete that id if it exists
try:
    indicator_group_res = oauth.delete(base_url + f"/indicatorgroups/{indicator_group_id}")
    assert(indicator_group_res.status_code == 200)
except NameError:
    print("indicator group not defined")

# get the final count
indicator_group_res = oauth.get(base_url + '/indicatorgroups/$count')
assert(indicator_group_res.status_code == 200)
print(f"there are {indicator_group_res.text} indicator groups")

#indicator_group_res = oauth.post(base_url + '/indicatorgroups', json=indicator_group)
#assert(indicator_group.status_code == 200)
#print(indicator_group_res.content)
#
#
#
#indicator = oauth.post(base_url + '/indicators', json=indicator_json)
#print(indicator.status_code)
#json_print(indicator.content)
# appears that indicators must be created first
#created_indicator_group = oauth.post(base_url + '/indicatorgroups', json=indicator_group_json)
#assert(created_indicator_group.status_code == 200)
#json_print(created_indicator_group.content)


