import json

from sqlalchemy import create_engine

from settings import DB_URL

engine = create_engine(DB_URL)
conn = engine.connect()

grant_sql = '''
select g.data
from view_latest_grant g
where (
        g.data->>'title' ~* 'covid|coronavirus|pandemic' or
        g.data->>'description' ~* 'covid|coronavirus|pandemic'
    )
    and to_date(g.data->>'awardDate', 'YYYY-MM-DD') > '2020-01-01'
order by to_date(g.data->>'awardDate', 'YYYY-MM-DD')
'''
outputfile = "docs/data/grants_data.json"

print('Fetching grants')
result = conn.execute(grant_sql)

grants = []
for row in result:
    grants.append(row['data'])
print('Found {:,.0f} grants'.format(len(grants)))

print('Saving to file')
with open(outputfile, 'w') as a:
    json.dump({
        "grants": grants,
    }, a, indent=4)
print('Saved to `{}`'.format(outputfile))

print('Fetching funders')
result = conn.execute('''
select distinct g.data->'fundingOrganization'->0->>'id' as "fundingOrganization.0.id"
from view_latest_grant g 
''')
funders = []
for row in result:
    funders.append(row['fundingOrganization.0.id'])
print('Found {:,.0f} funder IDs'.format(len(funders)))

print('Saving to file')
with open('docs/data/funder_ids.json', 'w') as a:
    json.dump({
        "funders": funders,
    }, a, indent=4)
print('Saved to `{}`'.format('docs/data/funder_ids.json'))
