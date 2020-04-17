import json
import os
import datetime

from sqlalchemy import create_engine

from .settings import DB_URL, GRANTS_DATA_FILE, FUNDER_IDS_FILE

engine = create_engine(DB_URL)
conn = engine.connect()

grant_sql = '''
select g.data
from view_latest_grant g
where (
        g.data->>'title' ~* 'covid|coronavirus|pandemic' or
        g.data->>'description' ~* 'covid|coronavirus|pandemic' or
        g.data->'grantProgramme'->0->>'title' ~* 'covid|coronavirus|pandemic'
    )
    and to_date(g.data->>'awardDate', 'YYYY-MM-DD') > '2020-03-16'
order by to_date(g.data->>'awardDate', 'YYYY-MM-DD'), g.data->>'id'
'''

print('Fetching grants')
result = conn.execute(grant_sql)

grants = []
for row in result:
    grants.append(row['data'])
print('Found {:,.0f} grants'.format(len(grants)))

print('Saving to file')
with open(GRANTS_DATA_FILE, 'w') as a:
    json.dump({
        "grants": grants,
        "last_updated": datetime.datetime.now().isoformat()
    }, a, indent=4)
print('Saved to `{}`'.format(GRANTS_DATA_FILE))

print('Fetching funders')
result = conn.execute('''
select distinct g.data->'fundingOrganization'->0->>'id' as "fundingOrganization.0.id"
from view_latest_grant g 
''')
funders = []
with open(FUNDER_IDS_FILE, 'r') as a:
    funders.extend(json.load(a).get('funders', []))
for row in result:
    funders.append(row['fundingOrganization.0.id'])
funders = sorted(set(funders))
print('Found {:,.0f} funder IDs'.format(len(funders)))

print('Saving to file')
with open(FUNDER_IDS_FILE, 'w') as a:
    json.dump({
        "funders": funders,
    }, a, indent=4)
print('Saved to `{}`'.format(FUNDER_IDS_FILE))
