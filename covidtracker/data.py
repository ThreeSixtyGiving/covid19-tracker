import json
import datetime

from settings import GOOGLE_ANALYTICS, GRANTS_DATA_FILE, FUNDER_IDS_FILE

def get_data():

    with open(GRANTS_DATA_FILE) as a:
        grantsdata = json.load(a)
        grants = grantsdata['grants']
        last_updated = datetime.datetime.fromisoformat(grantsdata["last_updated"])

    with open(FUNDER_IDS_FILE) as a:
        all_funders = json.load(a)['funders']

    funders = list(set([g['fundingOrganization'][0]['id'] for g in grants]))
    recipients = list(set([g['recipientOrganization'][0]['id'] for g in grants]))
    amountAwarded = {}
    amountByDate = {
        '2020-03-14': {'grants':0, 'amount': 0}
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

    return dict(
        grants=grants,
        funders=funders,
        recipients=recipients,
        amountAwarded=amountAwarded,
        amountByDate=amountByDate,
        all_funders=all_funders,
        now=datetime.datetime.now(),
        last_updated=last_updated,
        google_analytics=GOOGLE_ANALYTICS,
    )