import json

from ac_api import *

path = "/indicatorgroups"
internal_id = "IG1"

def create_indicator_group():
    indicator_group = IndicatorGroup([{"short": "short description", "long":"long description", "language": "en"}]
            , internal_id)
    return indicator_group

def test_indicator_group():
    indicator_group = create_indicator_group()
    assert indicator_group.internalId == internal_id
    assert json.dumps(indicator_group.__dict__) == \
        '{"descriptions": [{"short": "short description", "long": "long description", "language": "en"}], "internalId": "IG1"}'

def test_auth():
    oauth = get_oauth_session()
    assert oauth.authorized == True

def test_indicator_group_exists_before_create():
    res_code, exists = in_asset_central(path, internal_id)
    assert res_code == 200
    assert exists == False

def test_create_indicator_group():
    indicator_group = create_indicator_group()
    res_code, res = insert_asset_central(path, internal_id, indicator_group.__dict__)
    assert res_code == 200
    assert res

def test_delete_indicator_group():
    res_code, res_list = delete_asset_central(path, internal_id)
    assert res_code == 200
