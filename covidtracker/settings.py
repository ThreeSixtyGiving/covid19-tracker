import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DB_URL")
GOOGLE_ANALYTICS = os.getenv('GOOGLE_ANALYTICS')
