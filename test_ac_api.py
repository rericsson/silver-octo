import json

from ac_api import *


org_id = "BC0D934611A24E28A7B56888E55BB9F5"
ig_path = "/indicatorgroups"
ig_internal_id = "IG1"
ind_path = "/indicators"
ind_internal_id = "IND1"
tem_path = "/templates"
tem_internal_id = "TEM1"
mod_path = "/models"
mod_internal_id = "MOD1"
equip_path = "/equipment"
equip_internal_id = "EQU1"

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
    template = Template([description], tem_internal_id, [], [], [])
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
    assert content["attributeGroups"] == []

def create_model():
    description = Description("model description", "model long description")
    model = Model([description], mod_internal_id, [PrimaryTemplate("5C5A3AC52DFD4FD6A77726E39104F9ED")], org_id)
    return model

def test_model():
    model = create_model()
    content = json.loads(model.to_json())
    assert content["internalId"] == mod_internal_id
    assert content["organizationID"] == org_id
    assert content["descriptions"][0]["short"] == "model description"
    assert content["descriptions"][0]["long"] == "model long description"
    assert content["descriptions"][0]["language"] == "en"
    assert content["templates"][0]["id"] == "5C5A3AC52DFD4FD6A77726E39104F9ED"
    assert content["templates"][0]["primary"] == True

def create_equipment():
    description = Description("equipment description", "equipment long description")
    equip = Equipment([description], equip_internal_id, org_id, "7D3E155E436044ACA0EC40C902189DAE" )
    return equip

def test_equipment():
    equip = create_equipment()
    content = json.loads(equip.to_json())
    assert content["internalId"] == equip_internal_id
    assert content["operatorID"] == org_id
    assert content["descriptions"][0]["short"] == "equipment description"
    assert content["descriptions"][0]["long"] == "equipment long description"
    assert content["descriptions"][0]["language"] == "en"
    assert content["modelId"] == "7D3E155E436044ACA0EC40C902189DAE"
    assert content["sourceBPRole"] == "1"
    assert content["modelKnown"] == True
    assert content["lifeCycle"] == "2"


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
    template.indicator_groups = [ IdString("ED5D78C2A79F4EE6A54714E87496ADB4") ]
    res_code, res = insert_asset_central(tem_path, tem_internal_id, template.to_json())
    assert res_code == 200
    assert res
    res_code, res_list = delete_asset_central(tem_path, tem_internal_id)
    assert res_code == 200

def test_create_model():
    model = create_model()
    res_code, res = insert_asset_central(mod_path, mod_internal_id, model.to_json())
    assert res_code == 200
    res_code = delete_asset_central_model(mod_internal_id)
    assert res_code == 204

def test_create_and_publish_model():
    model = create_model()
    res_code, res = insert_asset_central(mod_path, mod_internal_id, model.to_json())
    assert res_code == 200
    res_code = model.publish()
    assert res_code == 200
    res_code = delete_asset_central_model(mod_internal_id)
    assert res_code == 204



def test_create_equipment():
    equip = create_equipment()
    equip.model_id = "7D3E155E436044ACA0EC40C902189DAE"
    equip_id = equipment_insert_asset_central(equip_internal_id, equip.to_json())
    assert len(equip_id) == 32
    res_code = delete_asset_central_equipment(equip_internal_id)
    assert res_code == 204


def test_all():
    # create an indicator
    indicator = create_indicator()
    res_code, res = insert_asset_central(ind_path, ind_internal_id, indicator.to_json())
    assert res_code == 200
    ind_ac_id = res
    # create indicator group with that indicator
    indicator_group = create_indicator_group()
    indicator_group.indicators = [ ind_ac_id ]
    res_code, res = insert_asset_central(ig_path, ig_internal_id, indicator_group.to_json())
    assert res_code == 200
    ind_group_ac_id = res
    # create template with that indicator group
    template = create_template()
    template.indicator_groups = [ IdString(ind_group_ac_id) ]
    res_code, res = insert_asset_central(tem_path, tem_internal_id, template.to_json())
    assert res_code == 200
    tem_ac_id = res
    # create a model
    model = create_model()
    model.templates = [PrimaryTemplate(tem_ac_id)]
    res_code, res = insert_asset_central(mod_path, mod_internal_id, model.to_json())
    assert res_code == 200
    mod_ac_id = res
    # need to publish the model before creating the equipment
    res_code = model.publish()
    assert res_code == 200
    # create an equipment
    equip = create_equipment()
    equip.model_id = mod_ac_id
    res = equipment_insert_asset_central(equip_internal_id, equip.to_json())
    assert len(res) == 32
    # delete the equipment
    res_code = delete_asset_central_equipment(equip_internal_id)
    assert res_code == 204
    # delete the model
    res_code = delete_asset_central_model(mod_internal_id)
    assert res_code == 204
    # delete the template
    res_code, res_list = delete_asset_central(tem_path, tem_internal_id)
    assert res_code == 200
    # delete the indicator group
    res_code, res_list = delete_asset_central(ig_path, ig_internal_id)
    assert res_code == 200
    # delete the indicator
    res_code, res_list = delete_asset_central(ind_path, ind_internal_id)
    assert res_code == 200



