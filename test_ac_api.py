import json
import pytest

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

# create the objects with sample data
def create_indicator():
    description = Description("indicator description", "indicator description")
    indicator = Indicator(ind_internal_id, description)
    return indicator

def create_indicator_group():
    description = Description("short description", "long description")
    indicator_group = IndicatorGroup(ig_internal_id, description)
    return indicator_group

def create_template():
    description = Description("template description", "template long description")
    template = Template(tem_internal_id,description )
    return template

def create_model():
    description = Description("model description", "model long description")
    model = Model(internalId=mod_internal_id, description=description,
            templates=[PrimaryTemplate("5C5A3AC52DFD4FD6A77726E39104F9ED")],
            organizationID=org_id)
    return model

def create_equipment():
    description = Description("equipment description", "equipment long description")
    equip = Equipment(equip_internal_id, [description], org_id, "7D3E155E436044ACA0EC40C902189DAE" )
    return equip

# make sure the authorization code works
def test_auth():
    oauth = get_oauth_session()
    assert oauth.authorized == True


def test_indicator():
    indicator = create_indicator()
    content = json.loads(indicator.to_json())
    assert content["internalId"] == ind_internal_id
    assert content["description"]["short"] == "indicator description"
    assert content["description"]["long"] == "indicator description"
    assert content["dataType"] == "numeric"
    assert content["indicatorType"][0]["type"] == "IndicatorType"
    assert content["indicatorType"][0]["code"] == "1"
    assert content["indicatorType"][0]["languageIsoCode"] == "en"
    assert content["indicatorType"][0]["description"] == "measured"
    assert content["aggregationConcept"] == "6"
    assert content["expectedBehaviour"] == "3"
    assert content["indicatorCategory"] == "1"
    # insert the indicator
    status = indicator.insert()
    assert status == 200
    assert len(indicator.id) == 32
    # update indicator
    indicator.description.short = "Indicator 1"
    status = indicator.update()
    assert status == 200
    assert indicator.description.short == "Indicator 1"
    # load indicator
    indicator_load = Indicator.load(ind_internal_id)
    assert indicator_load.internalId == ind_internal_id
    # delete indicator
    status = indicator.delete()
    assert status == 200

def test_indicator_group():
    indicator_group = create_indicator_group()
    content = json.loads(indicator_group.to_json())
    assert content["internalId"] == ig_internal_id
    assert content["description"]["short"] == "short description"
    assert content["description"]["long"] == "long description"
    assert content["indicators"] == []
    # insert the indicator group
    status = indicator_group.insert()
    assert status == 200
    assert len(indicator_group.id) == 32
    # update indicator group
    indicator_group.description.short = "Indicator 1"
    status = indicator_group.update()
    assert status == 200
    assert indicator_group.description.short == "Indicator 1"
    # load indicator group
    indicator_group_load = IndicatorGroup.load(ig_internal_id)
    assert indicator_group_load.internalId == ig_internal_id
    # delete indicator group
    status = indicator_group.delete()
    assert status == 200


def test_template():
    template = create_template()
    template.indicatorGroups = [ IdString("ED5D78C2A79F4EE6A54714E87496ADB4") ]
    content = json.loads(template.to_json())
    assert content["internalId"] == tem_internal_id
    assert content["description"]["short"] == "template description"
    assert content["description"]["long"] == "template long description"
    assert len(content["indicatorGroups"]) == 1
    assert content["industryStandards"] == []
    assert content["attributeGroups"] == []
    # insert the template
    status = template.insert()
    assert status == 200
    assert len(template.id) == 32
    # update indicator
    template.description.short = "Indicator 1"
    status = template.update()
    assert status == 200
    assert template.description.short == "Indicator 1"
    # load indicator
    template_load = Template.load(tem_internal_id)
    assert template_load.internalId == tem_internal_id
    # delete indicator
    status = template.delete()
    assert status == 200


def test_model():
    model = create_model()
    content = json.loads(model.to_json())
    assert content["internalId"] == mod_internal_id
    assert content["organizationID"] == org_id
    assert content["description"]["short"] == "model description"
    assert content["description"]["long"] == "model long description"
    assert content["templates"][0]["id"] == "5C5A3AC52DFD4FD6A77726E39104F9ED"
    assert content["templates"][0]["primary"] == True
    # insert
    #status = model.insert()
    #assert status == 200
    #assert len(model.id) == 32
    # update
    #with pytest.raises(NotImplementedError):
    #    model.update()
    # publish
    #status = model.publish()
    #assert status == 200
    # load
    load = Model.load(mod_internal_id)
    assert load.internalId == mod_internal_id
    # delete
    status = model.delete()
    assert status == 200


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
    # insert
    status = equip.insert()
    assert status == 200
    assert len(equip.id) == 32
    # update
    equip.description.short = "Indicator 1"
    status = equip.update()
    assert status == 200
    assert equip.description.short == "Indicator 1"
    # load
    load = Equipment.load(ind_internal_id)
    assert load.internalId == equip_internal_id
    # delete
    status = equip.delete()
    assert status == 200

def test_all():
    # insert the indicator
    indicator = create_indicator()
    status = indicator.insert()
    assert status == 200
    assert len(indicator.id) == 32
    ind_ac_id = indicator.id
    # create indicator group with that indicator
    indicator_group = create_indicator_group()
    indicator_group.indicators = [ ind_ac_id ]
    status = indicator_group.insert()
    assert status == 200
    assert len(indicator_group.id) == 32
    ind_group_ac_id = indicator_group.id
    # create template with that indicator group
    template = create_template()
    template.indicator_groups = [ IdString(ind_group_ac_id) ]
    status = template.insert()
    assert status == 200
    assert len(template.id) == 32
    tem_ac_id = template.id
    # create a model
    model = create_model()
    model.templates = [PrimaryTemplate(tem_ac_id)]
    status = model.insert()
    assert status == 200
    assert len(model.id) == 32
    mod_ac_id = model.id
    # need to publish the model before creating the equipment
    res_code = model.publish()
    assert res_code == 200
    # create an equipment
    equip = create_equipment()
    equip.model_id = mod_ac_id
    status = equipment.insert()
    assert status == 200
    assert len(equipment.id) == 32
    # delete the equipment
    status = equipment.delete()
    assert status == 204
    # delete the model
    status = model.delete()
    assert status == 204
    # delete the template
    status = template.delete()
    assert status == 200
    # delete the indicator group
    status == indicator_group.delete()
    assert status == 200
    # delete the indicator
    status == indicator.delete()
    assert status == 200



