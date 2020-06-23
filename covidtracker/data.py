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

from .settings import GOOGLE_ANALYTICS, GRANTS_DATA_FILE, GRANTS_DATA_PICKLE, FUNDER_IDS_FILE

def get_data():

    grants = pd.read_pickle(GRANTS_DATA_PICKLE)

    return dict(
        grants=grants,
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
            grants = grants[
                grants['fundingOrganization.0.id'].isin(filters['funder']) |
                grants['recipientOrganization.0.id'].isin(filters['funder'])
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
                ~grants['_recipient_is_funder']
            ]

    return {
        **all_data,
        "all_grants": all_data['grants'],
        "grants": grants,
        "filters": filters,
    }
