import json

from ac_api import *

def create_indicator_group():
    indicator_group = IndicatorGroup([{"short": "short description", "long":"long description", "language": "en"}]
            ,"IG1" )
    return indicator_group

def test_indicator_group():
    indicator_group = create_indicator_group()
    assert indicator_group.internalId == "IG1"
    assert json.dumps(indicator_group.__dict__) == \
        '{"descriptions": [{"short": "short description", "long": "long description", "language": "en"}], "internalId": "IG1"}'

def test_auth():
    oauth = get_oauth_session()
    assert oauth.authorized == True

def test_indicator_group_exists_before_create():
    indicator_group = create_indicator_group()
    assert indicator_group.in_asset_central() == False

def test_create_indicator_group():
    indicator_group = create_indicator_group()
    assert indicator_group.insert_asset_central()

def test_delete_indicator_group():
    indicator_group = create_indicator_group()
    res_code, res_list = indicator_group.delete_asset_central()
    assert res_code == 200
