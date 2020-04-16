import json
import datetime
import re

from settings import GOOGLE_ANALYTICS, GRANTS_DATA_FILE, FUNDER_IDS_FILE

def get_data():

    with open(GRANTS_DATA_FILE) as a:
        grantsdata = json.load(a)
        grants = grantsdata['grants']
        last_updated = datetime.datetime.fromisoformat(grantsdata["last_updated"])

    with open(FUNDER_IDS_FILE) as a:
        all_funders = json.load(a)['funders']

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
                    g['fundingOrganization'][0]['id'] in filters['funder']
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
    
    funders = list(set([
        (g['fundingOrganization'][0]['id'], g['fundingOrganization'][0]['name'])
        for g in grants]))
    recipients = list(set([
        g['recipientOrganization'][0]['id']
        for g in grants
    ]))

    amountAwarded = {}
    amountByDate = {
        '2020-03-14': {'grants':0, 'amount': 0},
    }
    for g in grants:
        awardDate = g['awardDate'][0:10]
        if g['currency'] not in amountAwarded:
            amountAwarded[g['currency']] = 0
        if awardDate not in amountByDate:
            amountByDate[awardDate] = {
                'grants': 0,
                "amount": 0,
            }
        amountAwarded[g['currency']] += g['amountAwarded']
        if g['currency'] == 'GBP':
            amountByDate[awardDate]['grants'] += 1
            amountByDate[awardDate]['amount'] += g['amountAwarded']

    return {
        **all_data,
        'funders': funders,
        'recipients': recipients,
        "amountAwarded": amountAwarded,
        "amountByDate": amountByDate,
        "grants": grants,
    }