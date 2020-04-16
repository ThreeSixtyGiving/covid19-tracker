import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DB_URL")
GOOGLE_ANALYTICS = os.getenv('GOOGLE_ANALYTICS')
GRANTS_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data/grants_data.json')
FUNDER_IDS_FILE = os.path.join(os.path.dirname(__file__), 'data/funder_ids.json')