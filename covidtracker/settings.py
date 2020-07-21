import os

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
GOOGLE_ANALYTICS = os.getenv("GOOGLE_ANALYTICS")
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "assets/data"))
GRANTS_DATA_FILE = os.getenv(
    "GRANTS_DATA_FILE", os.path.join(DATA_DIR, "grants_data.json")
)
GRANTS_DATA_PICKLE = os.getenv(
    "GRANTS_DATA_PICKLE", os.path.join(DATA_DIR, "grants_data.pkl")
)
WORDS_PICKLE = os.getenv("WORDS_PICKLE", os.path.join(DATA_DIR, "ngrams.pkl"))
FUNDER_IDS_FILE = os.getenv(
    "FUNDER_IDS_FILE", os.path.join(DATA_DIR, "funder_ids.json")
)
SOURCES = {
    "recipientOrganizationPostcode": "Postcode of recipient organisation",
    "recipientOrganizationLocation": "Location of recipient organisation",
    "beneficiaryLocation": "Location of grant beneficiaries",
}
THREESIXTY_COLOURS = [
    # "#153634", # Grey
    "#DE6E26",  # Orange
    "#4DACB6",  # Teal
    "#EFC329",  # Yellow
    "#BC2C26",  # Red
    "#0B1B1A",  # Darker grey
    "#6F3713",  # Darker orange
    "#27565B",  # Darker teal
    "#786114",  # Darker yellow
    "#5E1613",  # Darker red
]

FUNDER_GROUPS = {
    "lottery": {
        "name": "National Lottery distributors",
        "funder_ids": {
            "GB-GOR-PB188": "National Lottery Community Fund",
            "GB-COH-RC000766": "Sport England",
            "GB-GOR-PC390": "National Lottery Heritage Fund",
            "GB-CHC-1036733": "Arts Council",
        },
    }
}

PRIORITIES = [
    "GB-CHC",
    "GB-SC",
    "GB-NIC",
    "GB-EDU",
    "GB-LAE",
    "GB-PLA",
    "GB-LAS",
    "GB-LANI",
    "GB-GOR",
    "GB-COH",
]

AMOUNT_BINS = [0, 500, 1000, 2000, 5000, 10000, 100000, 1000000, float("inf")]
AMOUNT_BIN_LABELS = [
    "Under £500",
    "£500 - £1k",
    "£1k - £2k",
    "£2k - £5k",
    "£5k - £10k",
    "£10k - £100k",
    "£100k - £1m",
    "Over £1m",
]
INCOME_BINS = [-1, 10000, 100000, 250000, 500000, 1000000, 10000000, float("inf")]
INCOME_BIN_LABELS = [
    "Under £10k",
    "£10k - £100k",
    "£100k - £250k",
    "£250k - £500k",
    "£500k - £1m",
    "£1m - £10m",
    "Over £10m",
]
AGE_BINS = pd.to_timedelta([x * 365 for x in [-1, 1, 2, 5, 10, 25, 200]], unit="D")
AGE_BIN_LABELS = [
    "Under 1 year",
    "1-2 years",
    "2-5 years",
    "5-10 years",
    "10-25 years",
    "Over 25 years",
]

STOPWORDS = [
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "you're",
    "you've",
    "you'll",
    "you'd",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "she's",
    "her",
    "hers",
    "herself",
    "it",
    "it's",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
    "what",
    "which",
    "who",
    "whom",
    "this",
    "that",
    "that'll",
    "these",
    "those",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "a",
    "an",
    "the",
    "and",
    "but",
    "if",
    "or",
    "because",
    "as",
    "until",
    "while",
    "of",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "s",
    "t",
    "can",
    "will",
    "just",
    "don",
    "don't",
    "should",
    "should've",
    "now",
    "d",
    "ll",
    "m",
    "o",
    "re",
    "ve",
    "y",
    "ain",
    "aren",
    "aren't",
    "couldn",
    "couldn't",
    "didn",
    "didn't",
    "doesn",
    "doesn't",
    "hadn",
    "hadn't",
    "hasn",
    "hasn't",
    "haven",
    "haven't",
    "isn",
    "isn't",
    "ma",
    "mightn",
    "mightn't",
    "mustn",
    "mustn't",
    "needn",
    "needn't",
    "shan",
    "shan't",
    "shouldn",
    "shouldn't",
    "wasn",
    "wasn't",
    "weren",
    "weren't",
    "won",
    "won't",
    "wouldn",
    "wouldn't" "toward",
    "towards",
    "work",
    "works",
    "help",
    "continue",
    "works",
    "provide",
    # covid-specific words
    "covid19",
    "19",
    "covid",
    "people",
    "grant",
    "during",
    "pandemic",
    "coronavirus",
]
