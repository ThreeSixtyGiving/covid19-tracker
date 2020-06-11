import json
import datetime
import re
from collections import Counter

import requests
import requests_cache

requests_cache.install_cache(
    'fetch_cache',
    expire_after=60 * 60 * 2 # two hours
)

from .settings import GOOGLE_ANALYTICS, GRANTS_DATA_FILE, FUNDER_IDS_FILE

def get_data():

    def get_recipient(grant):
        for r in grant.get("_recipient", []):
            return (r["id"], r['name'])
        return (g['recipientOrganization'][0]['id'], g['recipientOrganization'][0]['name'])

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

    funders = Counter()
    recipients = dict()
    counties = set()
    has_geo = 0
    for g in grants:
        funders[(g['fundingOrganization'][0]['id'], g['fundingOrganization'][0]['name'])] += 1
        recipient_id, recipient_name = get_recipient(g)
        recipients[g['_recipient_ids'][0]] = recipient_name
        this_has_geo = False
        for geo in g.get('_geo', []):
            if geo.get('utlacd') and geo.get('utlanm'):
                counties.add((
                    geo.get('utlacd'),
                    geo.get('utlanm')
                ))
                this_has_geo = True
        if this_has_geo:
            has_geo += 1

    return dict(
        grants=grants,
        funders=funders,
        recipients=set(recipients.keys()),
        counties=counties,
        all_funders=all_funders,
        all_recipients=recipients,
        now=datetime.datetime.now(),
        last_updated=last_updated,
        google_analytics=GOOGLE_ANALYTICS,
        has_geo=has_geo,
        grant_count=len(grants),
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

            # area filter
            if filters.get("area"):
                utlas = [geo['utlacd'] for geo in g.get('_geo', []) if geo.get(
                    'utlacd') and geo.get('utlacd') in filters['area']]
                include_grant.append(len(utlas) > 0)

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

            # recipients filter
            if filters.get("recipient", []):
                include_grant.append(
                    len(set(g['_recipient_ids']) & set(
                        filters.get("recipient", [])))
                )

            # exclude grants to grantmakers filter
            if 'exclude' in filters.get("doublecount", []):
                include_grant.append(
                    g['recipientOrganization'][0]["id"] not in all_data["all_funders"]
                ) 
            
            if all(include_grant):
                grants.append(g)
    
    funders = Counter()
    recipients = set()

    grantsByRegion = {}
    grantsByLa = {}
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
        funders[(g['fundingOrganization'][0]['id'], g['fundingOrganization'][0]['name'])] += 1
        recipients.add(g['_recipient_ids'][0])

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

        for geo in g.get('_geo', []):
            geocodes_seen = set()
            if geo.get('rgncd') or geo.get('ctrycd'):
                geocode = (
                    geo['rgncd'] if geo.get("rgncd") else geo.get('ctrycd'),
                    geo['rgnnm'] if geo.get("rgnnm") else geo.get('ctrynm'),
                )
                la_geocode = (geo['utlacd'],geo['utlanm'],)
                if geocode in geocodes_seen:
                    continue
                if geocode not in grantsByRegion:
                    grantsByRegion[geocode] = {
                        'count': 0,
                        'amount': 0,
                    }
                if la_geocode not in grantsByLa:
                    grantsByLa[la_geocode] = {
                        'count': 0,
                        'amount': 0,
                    }
                grantsByRegion[geocode]['count'] += 1
                grantsByRegion[geocode]['amount'] += g['amountAwarded']
                grantsByLa[la_geocode]['count'] += 1
                grantsByLa[la_geocode]['amount'] += g['amountAwarded']
                geocodes_seen.add(geocode)
    
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
        'funder_counts': funders,
        'funders': list(funders.keys()),
        'recipients': list(recipients),
        "amountAwarded": amountAwarded,
        "amountByDate": amountByDate,
        "grantsByRegion": grantsByRegion,
        "grantsByLa": grantsByLa,
        "grants": grants,
        "grants_grantmakers": grants_grantmakers,
        "filters": filters,
    }
