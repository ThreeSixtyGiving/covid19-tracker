import json
import datetime
import re
from collections import Counter

import requests
import requests_cache
import pandas as pd

requests_cache.install_cache(
    'fetch_cache',
    expire_after=60 * 60 * 2 # two hours
)

from .settings import GOOGLE_ANALYTICS, GRANTS_DATA_FILE, GRANTS_DATA_PICKLE, FUNDER_IDS_FILE, WORDS_PICKLE, FUNDER_GROUPS

def get_data():

    grants = pd.read_pickle(GRANTS_DATA_PICKLE)
    words = pd.read_pickle(WORDS_PICKLE)

    return dict(
        grants=grants,
        words=words,
        now=datetime.datetime.now(),
        last_updated=grants['_last_updated'].max().to_pydatetime(),
        google_analytics=GOOGLE_ANALYTICS,
    )

def normalise_string(s):
    s = s.lower()
    s = re.sub(r'[^0-9a-zA-Z]+', '', s)
    return s


def filter_data(all_data, **filters):

    grants = all_data["grants"]

    use_filter = False
    for f in filters.values():
        if f:
            use_filter = True

    if use_filter:
        # funder filter
        if filters.get("funder"):

            funder_ids = []

            for f in filters['funder']:
                if f in FUNDER_GROUPS.keys():
                    funder_ids.extend(FUNDER_GROUPS[f]['funder_ids'].keys())
                else:
                    funder_ids.append(f)

            grants = grants[
                grants['fundingOrganization.0.id'].isin(funder_ids)
            ]

        # area filter
        if filters.get("area"):
            grants = grants[
                grants['location.utlacd'].isin(filters['area'])
            ]

        # search filter
        if filters.get("search"):
            search_in = grants[[
                "title",
                "description",
                'fundingOrganization.0.name',
                'recipientOrganization.0.name',
                '_recipient_name'
            ]].fillna('').apply(" ".join, axis=1).apply(normalise_string)
            search_term = normalise_string(filters.get("search"))
            grants = grants[
                search_in.str.contains(search_term)
            ]

        # recipients filter
        if filters.get("recipient", []):
            grants = grants[
                grants['_recipient_id'].isin(filters['recipient']) |
                grants['recipientOrganization.0.id'].isin(filters['recipient'])
            ]

        # exclude grants to grantmakers filter
        if 'exclude' in filters.get("doublecount", []):
            grants = grants[
                ~grants['_recipient_is_grantmaker']
            ]

    return {
        **all_data,
        "words": all_data['words'][all_data['words']['id'].isin(grants['id'])],
        "all_grants": all_data['grants'],
        "grants": grants,
        "filters": filters,
    }
