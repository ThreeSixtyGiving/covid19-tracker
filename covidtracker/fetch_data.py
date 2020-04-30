import json
import os
import datetime

from sqlalchemy import create_engine
import click
import requests
import tqdm

from settings import DB_URL, GRANTS_DATA_FILE, FUNDER_IDS_FILE, AREAS_FILE

def find_areas(areas_to_find, areas):
    new_areas = 0
    new_areas_to_find = set()
    for a in tqdm.tqdm(areas_to_find):
        if areas.get(a):
            if a.startswith('E07'):
                new_areas_to_find.add(areas[a]["parent"])
            continue
        try:
            areas[a] = requests.get(f'https://findthatpostcode.uk/areas/{a}.json').json().get('data', {}).get('attributes')
            if a.startswith('E07'):
                new_areas_to_find.add(areas[a]["parent"])
            new_areas += 1
        except Exception as e:
            print("Could not find area {}".format(a))
            print(e)
            continue
        if a == 'E10000011':
            print(areas[a])
    print('Found {:,.0f} new areas'.format(new_areas))
    return areas, new_areas_to_find

@click.command()
@click.option('--db-url', default=DB_URL, help='Database connection string')
@click.option('--grants-data-file', default=GRANTS_DATA_FILE, help='Location to save the grants data')
@click.option('--funder-ids-file', default=FUNDER_IDS_FILE, help='Location to save the list of funders')
@click.option('--areas-file', default=AREAS_FILE, help='Location to save the list of funders')
def fetch_data(db_url=DB_URL, grants_data_file=GRANTS_DATA_FILE, funder_ids_file=FUNDER_IDS_FILE, areas_file=AREAS_FILE):
    """Import data from the database to a JSON file"""
    engine = create_engine(db_url)
    conn = engine.connect()

    grant_sql = '''
    select g.data,
    	db_grant.additional_data->>'recipientDistrictGeoCode' as "recipientDistrictGeoCode",
    	db_grant.additional_data->>'recipientWardNameGeoCode' as "recipientWardNameGeoCode"
    from view_latest_grant g
    	inner join db_grant 
    		on g.id = db_grant.id
    where (
            g.data->>'title' ~* 'covid|coronavirus|pandemic|cv-?19' or
            g.data->>'description' ~* 'covid|coronavirus|pandemic|cv-?19' or
            g.data->'grantProgramme'->0->>'title' ~* 'covid|coronavirus|pandemic|cv-?19' or
            g.data->>'classifications' ~* 'covid|coronavirus|pandemic|cv-?19'
        )
        and to_date(g.data->>'awardDate', 'YYYY-MM-DD') > '2020-03-16'
    order by to_date(g.data->>'awardDate', 'YYYY-MM-DD'), g.data->>'id'
    '''

    print('Fetching grants')
    result = conn.execute(grant_sql)

    grants = []
    areas_to_find = set()
    for row in result:
        geo = dict(
            lsoa=None,
            ward=row['recipientWardNameGeoCode'],
            district=row["recipientDistrictGeoCode"],
            county=row["recipientDistrictGeoCode"],
        )
        for l in row['data'].get('beneficiaryLocation', []):
            if l.get("geoCodeType") == 'LSOA':
                geo["lsoa"] = l.get("geoCode")
            elif l.get("geoCodeType") in ['NMD', 'LONB', 'UA']:
                geo["district"] = l.get("geoCode")
                geo["county"] = l.get("geoCode")
            elif l.get("geoCodeType") in ['WD']:
                geo["ward"] = l.get("geoCode")

        if geo["district"]:
            areas_to_find.add(geo["district"])

        grants.append({
            **row['data'],
            "geo": geo,
        })
    print('Found {:,.0f} grants'.format(len(grants)))

    print("Fetching areas")
    with open(areas_file, 'r') as a:
        areas = json.load(a).get('areas', {})
    while areas_to_find:
        areas, areas_to_find = find_areas(areas_to_find, areas)

    print('Saving areas to file')
    with open(areas_file, 'w') as a:
        json.dump({
            "areas": areas,
        }, a, indent=4)
    print('Saved to `{}`'.format(areas_file))

    print("Adding upper-tier authorities to grants")
    for g in grants:
        if g['geo']['district'] and g['geo']['district'].startswith('E07'):
            g['geo']['county'] = areas[g['geo']['district']]['parent']

    print('Saving grants to file')
    with open(grants_data_file, 'w') as a:
        json.dump({
            "grants": grants,
            "last_updated": datetime.datetime.now().isoformat()
        }, a, indent=4)
    print('Saved to `{}`'.format(grants_data_file))

    print('Fetching funders')
    result = conn.execute('''
    select distinct g.data->'fundingOrganization'->0->>'id' as "fundingOrganization.0.id"
    from view_latest_grant g 
    ''')
    funders = []
    with open(funder_ids_file, 'r') as a:
        funders.extend(json.load(a).get('funders', []))
    for row in result:
        funders.append(row['fundingOrganization.0.id'])
    funders = sorted(set(funders))
    print('Found {:,.0f} funder IDs'.format(len(funders)))

    print('Saving funders to file')
    with open(funder_ids_file, 'w') as a:
        json.dump({
            "funders": funders,
        }, a, indent=4)
    print('Saved to `{}`'.format(funder_ids_file))

if __name__ == '__main__':
    fetch_data()