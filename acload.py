import click

from openpyxl import load_workbook
from ac_api import Description, IndicatorType, Indicator, IndicatorGroup, IdString, Template
from mapping import *
from typing import List

@click.command()
@click.argument("datafile", type=click.Path(exists=True))
def cli(datafile):
    """ Command line interface to load AC data

    Inserts all of the given data into AC.
    Provides output of progess.

    Args:
        datafile - xlsx file that contains the data to be loaded


    """
    click.echo("Opening %s..." % datafile)
    wb = load_workbook(filename=datafile)
    # check that we have the proper worksheets
    assert wb.sheetnames == ["Indicator", "Indicator Group", "Model Template", "Model", "Equipment"]

    indicators = load_indicators(wb["Indicator"])
    update_worksheet(indicators, wb["Indicator"])
    indicator_groups = load_indicator_groups(indicators, wb["Indicator Group"])
    update_worksheet(indicator_groups, wb["Indicator Group"])
    templates = load_templates(indicator_groups, wb["Model Template"])
    update_worksheet(templates, wb["Model Template"])

    # save the changes
    wb.save(filename=datafile)

def load_indicators(indicator_sheet):
    """ Loads all of the indicators into AC

    Args:
        indicator_sheet - worksheet containing the required datafields

    Returns:
        List of indicators that were loaded

    """
    indicators = []

    # open the indicator sheet and load the objects
    for row in indicator_sheet.iter_rows(min_row=2, values_only=True):
        indicator = Indicator(internalId=row[IND_INTERNAL_ID],
                                description=Description(row[IND_DESCRIPTION]),
                                dataType=row[IND_DATA_TYPE],
                                dimension1=row[IND_DIMENSION],
                                indicatorUom=row[IND_UOM],
                                expectedBehaviour=str(row[IND_EXPECTED_BEHAVIOR]),
                                indicatorColorCode=row[IND_COLOR],
                                id=4)

        indicators.append(indicator)

    # insert into AC
    for indicator in indicators:
        print(f"inserting indicator {indicator.internalId}...")
        try:
            indicator.insert()
        except Exception as ex:
            print(f"failed...error:{ex}")
        else:
            print(f"sucess...id = {indicator.id}")

    return indicators

def load_indicator_groups(indicators: List[Indicator], ig_sheet):
    """ Loads all of the indicator groups into AC

    Args:
        indicators - list of indicators that were loaded
        ig_sheet - worksheet containing the required datafields


    Returns:
        List of indicator groups that were loaded
    """

    # open the indicator group sheet and load the objects
    # loop through the row and get the distinct indicator group identifiers
    indicator_groups = []
    internal_id = ""
    desc = ""
    ig_indicators = []
    for iteration, row in enumerate(ig_sheet.iter_rows(min_row=2, values_only=True)):
        # first iteration
        if iteration == 0:
            internal_id = row[IG_INTERNAL_ID]
            desc = row[IG_DESCRIPTION]
            ig_indicators.append(row[IG_INDICATOR])
        else:
            # new internal id?
            if internal_id != row[IG_INTERNAL_ID]:
                # create indicator group and add to list
                indicator_groups.append(IndicatorGroup(internalId=internal_id,
                    description=Description(desc), indicators=ig_indicators))
                ig_indicators = []
                internal_id = row[IG_INTERNAL_ID]
                desc = row[IG_DESCRIPTION]
                ig_indicators.append(row[IG_INDICATOR])
            else: # same internal id, append the indicator
                ig_indicators.append(row[IG_INDICATOR])

    # out of the loop, we should have at least one indicator group
    indicator_groups.append(IndicatorGroup(internalId=internal_id,
        description=Description(desc), indicators=ig_indicators))

    # get the ids for each indicator in each indicator group
    for indicator_group in indicator_groups:
        # loop through the temp_ids in the indicator group
        for iteration, temp_id in enumerate(indicator_group.indicators):
            for ind in indicators:
                # get the real id from the indicators list and replace the temp_id
                if ind.internalId == temp_id:
                    indicator_group.indicators[iteration] = ind.id
                    break

    # insert into AC
    for indicator_group in indicator_groups:
        print(f"inserting indicator group {indicator_group.internalId}...")
        try:
            indicator_group.insert()
        except Exception as ex:
            print(f"failed...error: {ex}")
        else:
            print(f"success...id = {indicator_group.id}")

    return indicator_groups

def load_templates(indicator_groups, template_sheet):
    """ Loads all of the templates into AC

    Supports model templates only.

    Args:
        indicator_groups - list of indicator groups that were loaded
        template_sheet - worksheet that contains required datafields

    Returns:
        list of the templates that were loaded

    """
    # open the template sheet and load the objects
    # loop through the row and get the distinct template identifiers
    templates = []
    internal_id = ""
    desc = ""
    template_ig = []
    for iteration, row in enumerate(template_sheet.iter_rows(min_row=2, values_only=True)):
        # first iteration
        if iteration == 0:
            internal_id = row[TEM_INTERNAL_ID]
            desc = row[TEM_DESCRIPTION]
            template_ig.append(row[TEM_INDICATOR_GROUP])
        else:
            # new internal id?
            if internal_id != row[TEM_INTERNAL_ID]:
                # create template and add to list
                templates.append(Template(internalId=internal_id,
                    description=Description(desc), indicatorGroups=template_ig))
                template_ig = []
                internal_id = row[TEM_INTERNAL_ID]
                desc = row[TEM_DESCRIPTION]
                template_ig.append(row[TEM_INDICATOR_GROUP])
            else: # same internal id, append the indicator group
                template_ig.append(row[TEM_INDICATOR_GROUP])

    # out of the loop, we should have at least one indicator group
    templates.append(Template(internalId=internal_id,
        description=Description(desc), indicatorGroups=template_ig))

    # get the ids for each indicator group in each template
    for template in templates:
        # loop through the temp_ids in the template
        for iteration, temp_id in enumerate(template.indicatorGroups):
            for ig in indicator_groups:
                # get the real id from the indicator group list and replace the temp_id
                if ig.internalId == temp_id:
                    template.indicatorGroups[iteration] = IdString(ig.id)
                    break

    # insert into AC
    for template in templates:
        print(f"inserting template {template.internalId}...")
        try:
            template.insert()
        except Exception as ex:
            print(f"failed...error: {ex}")
        else:
            print(f"success...id = {template.id}")

    return templates

pass

def load_models(templates, models):
    pass

def load_equipment(models, equipment):
    pass

def update_worksheet(asset_central_objects: List, worksheet):
    """ Update the worksheet with returned IDs in the first column

    Args:
        asset_central_objects - a list of objects with ids
        worksheet - the worksheet to be updated
    """
    # get the internal ids from the spreadsheet
    for iteration, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True)):
        internal_id = row[INTERNAL_ID]
        for obj in asset_central_objects:
            if obj.internalId == internal_id:
                # adjust cells to account for header row and 1-based counting
                worksheet.cell(column=ID+1, row=iteration+2, value=obj.id)
                break


