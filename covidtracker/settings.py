import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DB_URL")
GOOGLE_ANALYTICS = os.getenv('GOOGLE_ANALYTICS')
GRANTS_DATA_FILE = os.path.join(os.path.dirname(__file__), 'assets/data/grants_data.json')
FUNDER_IDS_FILE = os.path.join(os.path.dirname(__file__), 'assets/data/funder_ids.json')
# GRANTS_DATA_URL = 'https://raw.githubusercontent.com/ThreeSixtyGiving/covid19-tracker/master/covidtracker/assets/data/grants_data.json'
# FUNDER_IDS_URL = 'https://raw.githubusercontent.com/ThreeSixtyGiving/covid19-tracker/master/covidtracker/assets/data/funder_ids.json'
