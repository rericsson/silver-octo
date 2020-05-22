import click

from openpyxl import load_workbook
from ac_api import Description, IndicatorType, Indicator, IndicatorGroup
from mapping import *

@click.command()
@click.argument("datafile", type=click.Path(exists=True))
def cli(datafile):
    click.echo("Opening %s..." % datafile)
    wb = load_workbook(filename=datafile, read_only=True)
    # check that we have the proper worksheets
    assert wb.sheetnames == ["Indicator", "Indicator Group", "Model Template", "Model", "Equipment"]

    indicators = []

    # open the indicator sheet and load the objects
    indicator_sheet = wb["Indicator"]
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

    # open the indicator group sheet and load the objects
    ig_sheet = wb["Indicator Group"]
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


