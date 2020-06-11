import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DB_URL")
GOOGLE_ANALYTICS = os.getenv('GOOGLE_ANALYTICS')
GRANTS_DATA_FILE = os.getenv(
    'GRANTS_DATA_FILE',
    os.path.join(os.path.dirname(__file__), 'assets/data/grants_data.json')
)
FUNDER_IDS_FILE = os.getenv(
    'FUNDER_IDS_FILE',
    os.path.join(os.path.dirname(__file__), 'assets/data/funder_ids.json')
)
THREESIXTY_COLOURS = [
    # "#153634", # Grey
    "#DE6E26", # Orange
    "#4DACB6", # Teal
    "#EFC329", # Yellow
    "#BC2C26", # Red
    "#0B1B1A", # Darker grey
    "#6F3713", # Darker orange
    "#27565B", # Darker teal
    "#786114", # Darker yellow
    "#5E1613", # Darker red
]