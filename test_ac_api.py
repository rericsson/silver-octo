import json

from ac_api import *

ig_path = "/indicatorgroups"
ig_internal_id = "IG1"
ind_path = "/indicators"
ind_internal_id = "IND1"
tem_internal_id = "TEM1"
tem_path = "/templates"

# make sure the authorization code works
def test_auth():
    oauth = get_oauth_session()
    assert oauth.authorized == True

# create the objects properly
def create_indicator():
    description = Description("indicator description", "indicator description")
    indicator_type = IndicatorType()
    indicator = Indicator([description], ind_internal_id, [indicator_type])
    return indicator


def test_indicator():
    indicator = create_indicator()
    content = json.loads(indicator.to_json())
    assert content["internalId"] == ind_internal_id
    assert content["descriptions"][0]["short"] == "indicator description"
    assert content["descriptions"][0]["long"] == "indicator description"
    assert content["descriptions"][0]["language"] == "en"
    assert content["dataType"] == "numeric"
    assert content["indicatorType"][0]["type"] == "IndicatorType"
    assert content["indicatorType"][0]["code"] == "1"
    assert content["indicatorType"][0]["languageIsoCode"] == "en"
    assert content["indicatorType"][0]["description"] == "measured"
    assert content["aggregationConcept"] == "6"
    assert content["expectedBehaviour"] == "3"
    assert content["indicatorCategory"] == "1"

def create_indicator_group():
    description = Description("short description", "long description")
    indicator_group = IndicatorGroup([description], ig_internal_id, [])
    return indicator_group


def test_indicator_group():
    indicator_group = create_indicator_group()
    content = json.loads(indicator_group.to_json())
    assert content["internalId"] == ig_internal_id
    assert content["descriptions"][0]["short"] == "short description"
    assert content["descriptions"][0]["long"] == "long description"
    assert content["descriptions"][0]["language"] == "en"
    assert content["indicators"] == []

def create_template():
    description = Description("template description", "template long description")
    template = Template([description], tem_internal_id, [], [])
    return template

def test_template():
    template = create_template()
    content = json.loads(template.to_json())
    assert content["internalId"] == tem_internal_id
    assert content["descriptions"][0]["short"] == "template description"
    assert content["descriptions"][0]["long"] == "template long description"
    assert content["descriptions"][0]["language"] == "en"
    assert content["indicatorGroups"] == []
    assert content["industryStandards"] == []



# asset central tests
def test_indicator_exists_before_create():
    res_code, exists, ac_id = in_asset_central(ind_path, ind_internal_id)
    assert res_code == 200
    assert exists == False
    assert ac_id == ""


def test_create_indicator():
    indicator = create_indicator()
    res_code, res = insert_asset_central(ind_path, ind_internal_id, indicator.to_json())
    assert res_code == 200
    assert res



def test_indicator_group_exists_before_create():
    res_code, exists, ac_id = in_asset_central(ig_path, ig_internal_id)
    assert res_code == 200
    assert exists == False
    assert ac_id == ""


def test_create_indicator_group():
    indicator_group = create_indicator_group()
    res_code, res = insert_asset_central(ig_path, ig_internal_id, indicator_group.to_json())
    assert res_code == 200
    assert res


def test_delete_indicator_group():
    res_code, res_list = delete_asset_central(ig_path, ig_internal_id)
    assert res_code == 200


def test_delete_indicator():
    res_code, res_list = delete_asset_central(ind_path, ind_internal_id)
    assert res_code == 200

def test_indicator_in_indicator_group():
    indicator = create_indicator()
    res_code, res = insert_asset_central(ind_path, ind_internal_id, indicator.to_json())
    assert res_code == 200
    ind_ac_id = res
    indicator_group = create_indicator_group()
    indicator_group.indicators = [ ind_ac_id ]
    res_code, res = insert_asset_central(ig_path, ig_internal_id, indicator_group.to_json())
    assert res_code == 200
    res_code, res_list = delete_asset_central(ig_path, ig_internal_id)
    assert res_code == 200
    res_code, res_list = delete_asset_central(ind_path, ind_internal_id)
    assert res_code == 200

def test_template_exists_before_create():
    res_code, exists, ac_id = in_asset_central(tem_path, tem_internal_id)
    assert res_code == 200
    assert exists == False
    assert ac_id == ""


def test_create_template():
    template = create_template()
    res_code, res = insert_asset_central(tem_path, tem_internal_id, template.to_json())
    assert res_code == 200
    assert res

def test_delete_template():
    res_code, res_list = delete_asset_central(tem_path, tem_internal_id)
    assert res_code == 200

