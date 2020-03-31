import json
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('360covid-tracker', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('index.html')

with open('grants_data.json') as a:
    grants = json.load(a)

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

page_content = template.render(
    grants=grants,
    funders=funders,
    recipients=recipients,
    amountAwarded=amountAwarded,
    amountByDate=amountByDate,
).encode('utf-8')

with open('docs/index.html', 'wb') as a:
    a.write(page_content)