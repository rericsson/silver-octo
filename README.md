# ACLoad - loads data from a xlsx file into SAP Asset Central

ACLoad uploads data from a specific spreadsheet format into indicators, indicator groups, model templates, models and equipment. It is intended to accelerate prototyping and enabled faster creation of data. It uses the SAP Asset Central API (ACAPI).

## Installation

Ensure that you have Python installed on your computer.
Datagen was created with Python 3.8 so that version is best. YMMV with other versions.

First, download the code from GitHub:

```
git clone  https://github.com/rericsson/silver_octo.git
```

After you have the code, switch to the directory where it was downloaded and run:

```
pip install .
```

That will install the datagen project in your local system. If you would rather do it in a virtual environment, you can do that by doing the following before running `pip install`:

```
virtualenv venv
. venv/bin/activate
pip install .
```
## Configuration

To connect to the SAP Asset Central API, you need to have an API key and the API urls. To get this information, go to https://help.sap.com/viewer/product/SAP_ASSET_INTELLIGENCE_NETWORK/2002/en-US and then navigate to the API Tutorial. Collect the client ID, client secret, base URL and token URL per the instructions. 

With that information, create a .env file in the same directory where the code is. The format should be like this:
```
CLIENT_ID = 'my client id'
CLIENT_SECRET = 'my client secret'
BASE_URL = 'my base URL'
TOKEN_URL = 'my token URL'
```

After you have created this file, you are ready to run the application.

## Running

ACLoad is a command line application. You can see the options by running acload with the --help option:
```
acload --help
Usage: acload [OPTIONS] COMMAND [ARGS]...

  Root for the CLI

Options:
  --help  Show this message and exit.

Commands:
  delete  Delete AC data defined in spreadsheet Requires ids in the first...
  load    Load AC data from a spreadsheet Inserts all of the given data
          into...

```

There is a example xlsx file with the source called ac_sample.xlsx. To make sure the configuration is working, load that data with the command:
```
acload load ac_sample.xlsx
```

You should get a list of responses and when you open the spreadsheet, it is now populated with the Asset Central GUID for each of the elements you created. 

To remove the data that was created run:
```
acload delete ac_sample.xlsx
```

## Known Limitations

The ACAPI requires GUID values for some of the properties (e.g. operatorId in equipment). For now, you have to look these up in the Asset Central GUI.

The ACAPI requires values for indicator dimension and UOM. These values have to be pulled from the ACAPI as they do not show up in the Asset Central GUI. The test_ac_api.py has an example of how these values can be retrieved. 

Error handling is not very robust. If something fails, the error messages aren't very helpful for figuring out the problem. The workaround is to use the debugger to get more information about the message coming back from the ACAPI. 
