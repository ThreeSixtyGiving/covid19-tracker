import json
import os
import datetime

import click
import requests
import tqdm
import pandas as pd

from settings import DB_URL, GRANTS_DATA_FILE, GRANTS_DATA_PICKLE, FUNDER_IDS_FILE, PRIORITIES

def canon_recipient(records):
    if not records:
        return {}

    for r in records:
        r['org_schema'] = "-".join(r['id'].split("-")[0:2])
        r['priority'] = PRIORITIES.index(
            r['org_schema']) if r['org_schema'] in PRIORITIES else len(PRIORITIES)
        r['latestIncome'] = int(
            r['latestIncome']) if r['latestIncome'] else None
        r['active'] = r['active'] != 'False'

    records = sorted(records, key=lambda r: (
        r['active'], r['priority'], r['dateRegistered'], r['latestIncome']))
    return records[0]


def canon_recipient_id(records):
    return canon_recipient(records).get('id')


def canon_recipient_name(records):
    return canon_recipient(records).get('name')

def canon_recipient_income(records):
    return canon_recipient(records).get('latestIncome')

def canon_recipient_types(records):
    t = canon_recipient(records).get('organisationType')
    if t:
        return t[0]
    return None

@click.command()
@click.option('--db-url', default=DB_URL, help='Database connection string')
@click.option('--grants-data-file', default=GRANTS_DATA_FILE, help='Location to save the grants data')
@click.option('--grants-data-pickle', default=GRANTS_DATA_PICKLE, help='Location to save the grants data as a pickle')
@click.option('--funder-ids-file', default=FUNDER_IDS_FILE, help='Location to save the list of funders')
def fetch_data(db_url=DB_URL, grants_data_file=GRANTS_DATA_FILE, grants_data_pickle=GRANTS_DATA_PICKLE, funder_ids_file=FUNDER_IDS_FILE):
    """Import data from the database to a JSON file"""

    print('Fetching funders')
    funder_sql = '''
    select distinct g.data->'fundingOrganization'->0->>'id' as "fundingOrganization.0.id"
    from view_latest_grant g 
    '''
    funders = pd.read_sql(funder_sql, con=db_url)[
        "fundingOrganization.0.id"].unique().tolist()
    with open(funder_ids_file, 'r') as a:
        funders.extend(json.load(a).get('funders', []))
    funders = sorted(set(funders))
    print('Found {:,.0f} funder IDs'.format(len(funders)))

    print('Fetching grants')
    grant_sql = '''
        select g.data->>'id' as "id",
            g.data->>'title' as "title",
            g.data->>'description' as "description",
            g.data->>'currency' as "currency",
            (g.data->>'amountAwarded')::float as "amountAwarded",
            to_date(g.data->>'awardDate', 'YYYY-MM-DD') as "awardDate",
            g.data->'recipientOrganization'->0->>'id' as "recipientOrganization.0.id",
            g.data->'recipientOrganization'->0->>'name' as "recipientOrganization.0.name",
            g.data->'fundingOrganization'->0->>'id' as "fundingOrganization.0.id",
            g.data->'fundingOrganization'->0->>'name' as "fundingOrganization.0.name",
            g.data->'grantProgramme'->0->>'title' as "grantProgramme.0.title",
            db_grant.additional_data->'locationLookup'->0->>'ladcd' as "location.ladcd",
            db_grant.additional_data->'locationLookup'->0->>'ladnm' as "location.ladnm",
            db_grant.additional_data->'locationLookup'->0->>'utlacd' as "location.utlacd",
            db_grant.additional_data->'locationLookup'->0->>'utlanm' as "location.utlanm",
            db_grant.additional_data->'locationLookup'->0->>'rgncd' as "location.rgncd",
            db_grant.additional_data->'locationLookup'->0->>'rgnnm' as "location.rgnnm",
            db_grant.additional_data->'locationLookup'->0->>'ctrycd' as "location.ctrycd",
            db_grant.additional_data->'locationLookup'->0->>'ctrynm' as "location.ctrynm",
            db_grant.additional_data->'locationLookup'->0->>'latitude' as "location.latitude",
            db_grant.additional_data->'locationLookup'->0->>'longitude' as "location.longitude",
            db_grant.additional_data->'locationLookup'->0->>'source' as "location.source",
            db_sourcefile."data"->'publisher'->>'prefix' as "publisher.prefix",
            db_sourcefile."data"->'publisher'->>'name' as "publisher.name",
            db_sourcefile."data"->>'license' as "license",
            db_grant.additional_data->'recipientOrgInfos' as "recipientOrgInfos"
        from view_latest_grant g
            inner join db_grant 
                on g.id = db_grant.id
            inner join db_sourcefile
                on db_grant.source_file_id = db_sourcefile.id
        where (
                g.data->>'title' ~* 'covid|coronavirus|pandemic|cv-?19' or
                g.data->>'description' ~* 'covid|coronavirus|pandemic|cv-?19' or
                g.data->'grantProgramme'->0->>'title' ~* 'covid|coronavirus|pandemic|cv-?19' or
                g.data->>'classifications' ~* 'covid|coronavirus|pandemic|cv-?19'
            )
            and to_date(g.data->>'awardDate', 'YYYY-MM-DD') > '2020-03-16'
            and to_date(g.data->>'awardDate', 'YYYY-MM-DD') < NOW() + interval '1 day'
            and g.data->>'currency' = 'GBP'
        order by to_date(g.data->>'awardDate', 'YYYY-MM-DD'), g.data->>'id'
    '''
    grants = pd.read_sql(grant_sql, con=db_url)

    # add canonical recipient details
    grants.loc[:, "_recipient_id"] = grants['recipientOrgInfos'].apply(
        canon_recipient_id)
    grants.loc[:, "_recipient_name"] = grants['recipientOrgInfos'].apply(
        canon_recipient_name)
    grants.loc[:, "_recipient_type"] = grants['recipientOrgInfos'].apply(
        canon_recipient_types)
    grants.loc[:, "_recipient_income"] = grants['recipientOrgInfos'].apply(
        canon_recipient_income)
    grants.loc[:, "_recipient_is_funder"] = grants['recipientOrganization.0.id'].isin(
        funders)
    grants.loc[:, "_last_updated"] = datetime.datetime.now()
    print('Found {:,.0f} grants'.format(len(grants)))

    print('Saving grants to file')
    with open(grants_data_file, 'w') as a:
        json.dump({
            "grants": json.loads(grants.drop('recipientOrgInfos', axis=1).to_json(orient='records')),
            "last_updated": datetime.datetime.now().isoformat()
        }, a, indent=4)
    print('Saved to `{}`'.format(grants_data_file))
    grants.to_pickle(grants_data_pickle)
    print('Saved to `{}`'.format(grants_data_pickle))

    print('Saving funders to file')
    with open(funder_ids_file, 'w') as a:
        json.dump({
            "funders": funders,
        }, a, indent=4)
    print('Saved to `{}`'.format(funder_ids_file))

if __name__ == '__main__':
    fetch_data()
