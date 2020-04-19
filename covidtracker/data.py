import json
import datetime
import re

import requests
import requests_cache

requests_cache.install_cache(
    'fetch_cache',
    expire_after=60 * 60 * 2 # two hours
)

from .settings import GOOGLE_ANALYTICS, GRANTS_DATA_FILE, FUNDER_IDS_FILE

def get_data():

    with open(GRANTS_DATA_FILE) as a:
        grantsdata = json.load(a)

    with open(FUNDER_IDS_FILE) as a:
        fundersdata = json.load(a)

    grants = grantsdata['grants']
    if grantsdata.get("last_updated"):
        last_updated = datetime.datetime.fromisoformat(grantsdata["last_updated"])
    else:
        last_updated = datetime.datetime.now()
    all_funders = fundersdata['funders']

    funders = list(set([
        (g['fundingOrganization'][0]['id'], g['fundingOrganization'][0]['name'])
        for g in grants]))
    recipients = list(set([
        g['recipientOrganization'][0]['id']
        for g in grants
    ]))

    return dict(
        grants=grants,
        funders=funders,
        recipients=recipients,
        all_funders=all_funders,
        now=datetime.datetime.now(),
        last_updated=last_updated,
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
        grants = []
        for g in all_data["grants"]:
            include_grant = []

            # funder filter
            if filters.get("funder"):
                include_grant.append(
                    g['fundingOrganization'][0]['id'] in filters['funder'] or \
                    g['recipientOrganization'][0]['id'] in filters['funder']
                )

            # search filter
            if filters.get("search"):
                search_in = normalise_string(
                    " ".join([
                        g['fundingOrganization'][0]['name'],
                        g['recipientOrganization'][0]['name'],
                        g['title'],
                        g['description'],
                    ])
                )
                search_term = normalise_string(filters.get("search"))
                include_grant.append(search_term in search_in)

            # exclude grants to grantmakers filter
            if 'exclude' in filters.get("doublecount", []):
                include_grant.append(
                    g['recipientOrganization'][0]["id"] not in all_data["all_funders"]
                ) 
            
            if all(include_grant):
                grants.append(g)
    
    funders = set()
    recipients = set()

    amountAwarded = {}
    amountByDate = {
        '2020-03-14': {
            'grants': 0,
            "amount": 0,
            'grants_grantmakers': 0,
            'amount_grantmakers': 0,
            'grants_other': 0,
            'amount_other': 0,
        },
    }
    grants_grantmakers = 0
    for g in grants:
        funders.add((g['fundingOrganization'][0]['id'], g['fundingOrganization'][0]['name']))
        recipients.add(g['recipientOrganization'][0]['id'])

        awardDate = g['awardDate'][0:10]
        if g['currency'] not in amountAwarded:
            amountAwarded[g['currency']] = 0
        if awardDate not in amountByDate:
            amountByDate[awardDate] = {
                'grants': 0,
                "amount": 0,
                'grants_grantmakers': 0,
                'amount_grantmakers': 0,
                'grants_other': 0,
                'amount_other': 0,
            }
        amountAwarded[g['currency']] += g['amountAwarded']
        if g['currency'] == 'GBP':
            amountByDate[awardDate]['grants'] += 1
            amountByDate[awardDate]['amount'] += g['amountAwarded']
            if g['recipientOrganization'][0]['id'] in all_data['all_funders']:
                amountByDate[awardDate]['grants_grantmakers'] += 1
                amountByDate[awardDate]['amount_grantmakers'] += g['amountAwarded']
                grants_grantmakers += 1
            else:
                amountByDate[awardDate]['grants_other'] += 1
                amountByDate[awardDate]['amount_other'] += g['amountAwarded']
    
    todays_date = datetime.datetime.now().date().isoformat()
    if todays_date not in amountByDate:
        amountByDate[todays_date] = {
                'grants': 0,
                "amount": 0,
                'grants_grantmakers': 0,
                'amount_grantmakers': 0,
                'grants_other': 0,
                'amount_other': 0,
            }

    return {
        **all_data,
        'funders': list(funders),
        'recipients': list(recipients),
        "amountAwarded": amountAwarded,
        "amountByDate": amountByDate,
        "grants": grants,
        "grants_grantmakers": grants_grantmakers,
    }