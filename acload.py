import click

from openpyxl import load_workbook
from ac_api import Description, IndicatorType, Indicator
from mapping import *

@click.command()
@click.argument("datafile", type=click.Path(exists=True))
def cli(datafile):
    click.echo("Opening %s" % datafile)
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
                                indicatorColorCode=row[IND_COLOR])

        indicators.append(indicator)

    # insert into AC
    for indicator in indicators:
        print(indicator)
        status = indicator.insert()
        print(f"{indicator.internalID} status {status}")
