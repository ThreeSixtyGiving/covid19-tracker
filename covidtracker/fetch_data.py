import datetime
import json
import re

import click
import pandas as pd
from nltk.util import ngrams
from settings import (
    DB_URL,
    FUNDER_IDS_FILE,
    GRANTS_DATA_FILE,
    GRANTS_DATA_PICKLE,
    PRIORITIES,
    STOPWORDS,
    WORDS_PICKLE,
)


def canon_recipient(records):
    if not records:
        return {}

    for r in records:
        r["org_schema"] = "-".join(r["id"].split("-")[0:2])
        r["priority"] = (
            PRIORITIES.index(r["org_schema"])
            if r["org_schema"] in PRIORITIES
            else len(PRIORITIES)
        )
        r["latestIncome"] = int(r["latestIncome"]) if r["latestIncome"] else None
        r["active"] = r["active"] != "False"

    records = sorted(
        records,
        key=lambda r: (
            r["active"],
            r["priority"],
            r["dateRegistered"],
            r["latestIncome"],
        ),
    )
    return records[0]


def canon_recipient_id(records):
    return canon_recipient(records).get("id")


def canon_recipient_name(records):
    return canon_recipient(records).get("name")


def canon_recipient_income(records):
    return canon_recipient(records).get("latestIncome")


def canon_recipient_types(records):
    types = canon_recipient(records).get("organisationType")
    if types:
        for t in types:
            if t != "Registered Company":
                return t
    return None


def get_ngrams(grants):
    def clean_string(s):
        s = s.lower()
        s = re.sub("[']+", "", s).strip()
        s = re.sub("[^0-9a-zA-Z]+", " ", s).strip()
        return s.split()

    def bigrams(text):
        text = [w for w in text if w not in STOPWORDS]
        return [" ".join(n) for n in ngrams(text, 2)]

    def unigrams(text):
        return [w for w in text if w not in STOPWORDS]

    def to_ngram(s, f):
        s = (
            s.apply(f)
            .apply(pd.Series)
            .stack()
            .rename("ngram")
            .reset_index()[["id", "ngram"]]
        )
        s.loc[:, "func"] = f.__name__
        return s

    words = []
    for i in ["title", "description"]:
        for f in (bigrams, unigrams):
            words.append(to_ngram(grants.set_index("id")[i].apply(clean_string), f))
    words = pd.concat(words, ignore_index=True)
    words = words.drop_duplicates(subset=["id", "ngram"])
    return words


@click.command()
@click.option("--db-url", default=DB_URL, help="Database connection string")
@click.option(
    "--grants-data-file",
    default=GRANTS_DATA_FILE,
    help="Location to save the grants data",
)
@click.option(
    "--grants-data-pickle",
    default=GRANTS_DATA_PICKLE,
    help="Location to save the grants data as a pickle",
)
@click.option(
    "--funder-ids-file",
    default=FUNDER_IDS_FILE,
    help="Location to save the list of funders",
)
@click.option(
    "--words-pickle", default=WORDS_PICKLE, help="Location to save ngrams as a pickle"
)
def fetch_data(
    db_url=DB_URL,
    grants_data_file=GRANTS_DATA_FILE,
    grants_data_pickle=GRANTS_DATA_PICKLE,
    funder_ids_file=FUNDER_IDS_FILE,
    words_pickle=WORDS_PICKLE,
):
    """Import data from the database to a JSON file"""

    print("Fetching funders")
    funder_sql = """
    select distinct g.data->'fundingOrganization'->0->>'id' as "fundingOrganization.0.id"
    from view_latest_grant g
    """
    funders = (
        pd.read_sql(funder_sql, con=db_url)["fundingOrganization.0.id"]
        .unique()
        .tolist()
    )
    with open(funder_ids_file, "r") as a:
        funders.extend(json.load(a).get("funders", []))
    funders = sorted(set(funders))
    print("Found {:,.0f} funder IDs".format(len(funders)))

    print("Fetching grants")
    grant_sql = """
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
            g.additional_data->'locationLookup'->0->>'ladcd' as "location.ladcd",
            g.additional_data->'locationLookup'->0->>'ladnm' as "location.ladnm",
            g.additional_data->'locationLookup'->0->>'utlacd' as "location.utlacd",
            g.additional_data->'locationLookup'->0->>'utlanm' as "location.utlanm",
            g.additional_data->'locationLookup'->0->>'rgncd' as "location.rgncd",
            g.additional_data->'locationLookup'->0->>'rgnnm' as "location.rgnnm",
            g.additional_data->'locationLookup'->0->>'ctrycd' as "location.ctrycd",
            g.additional_data->'locationLookup'->0->>'ctrynm' as "location.ctrynm",
            g.additional_data->'locationLookup'->0->>'latitude' as "location.latitude",
            g.additional_data->'locationLookup'->0->>'longitude' as "location.longitude",
            g.additional_data->'locationLookup'->0->>'source' as "location.source",
            g."source_data"->'publisher'->>'prefix' as "publisher.prefix",
            g."source_data"->'publisher'->>'name' as "publisher.name",
            g."source_data"->>'license' as "license",
            g."source_data"->>'license_name' as "license_name",
            g.additional_data->'recipientOrgInfos' as "recipientOrgInfos",
            g.data as "grant"
        from view_latest_grant g
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
    """
    grants = pd.read_sql(grant_sql, con=db_url)

    # add canonical recipient details
    grants.loc[:, "_recipient_id"] = grants["recipientOrgInfos"].apply(
        canon_recipient_id
    )
    grants.loc[:, "_recipient_name"] = grants["recipientOrgInfos"].apply(
        canon_recipient_name
    )
    grants.loc[:, "_recipient_type"] = grants["recipientOrgInfos"].apply(
        canon_recipient_types
    )
    grants.loc[:, "_recipient_income"] = grants["recipientOrgInfos"].apply(
        canon_recipient_income
    )
    grants.loc[:, "_recipient_is_grantmaker"] = grants[
        "recipientOrganization.0.id"
    ].isin(funders)
    grants.loc[:, "_last_updated"] = datetime.datetime.now()
    print("Found {:,.0f} grants".format(len(grants)))

    # extract the full grant record and save to JSON
    print("Saving grants to json file")

    def get_grant(g):

        recipient_ids = set()
        recipient_ids.add(g["recipientOrganization.0.id"])
        if g["recipientOrgInfos"]:
            for o in g["recipientOrgInfos"]:
                for i in o["orgIDs"]:
                    recipient_ids.add(i)
                recipient_ids.add(o["id"])

        r = {
            "_recipient": g["recipientOrgInfos"] if g["recipientOrgInfos"] else [],
            "_recipient_ids": sorted(list(recipient_ids)),
            "_recipient_is_grantmaker": g["_recipient_is_grantmaker"],
            **g.grant,
        }
        if g["location.source"]:
            r["_geo"] = [
                {
                    "ladcd": g["location.ladcd"],
                    "ladnm": g["location.ladnm"],
                    "utlacd": g["location.utlacd"],
                    "utlanm": g["location.utlanm"],
                    "rgncd": g["location.rgncd"],
                    "rgnnm": g["location.rgnnm"],
                    "ctrycd": g["location.ctrycd"],
                    "ctrynm": g["location.ctrynm"],
                    "latitude": g["location.latitude"],
                    "longitude": g["location.longitude"],
                    "source": g["location.source"],
                }
            ]
        return r

    with open(grants_data_file, "w") as a:
        json.dump(
            {
                "grants": [get_grant(g) for i, g in grants.iterrows()],
                "last_updated": datetime.datetime.now().isoformat(),
            },
            a,
            indent=4,
        )
    print("Saved to `{}`".format(grants_data_file))

    # remove big fields
    grants = grants.drop(columns=["grant", "recipientOrgInfos"])

    print("Saving grants to pickle")
    grants.to_pickle(grants_data_pickle)
    print("Saved to `{}`".format(grants_data_pickle))

    print("Saving ngrams to file")
    words = get_ngrams(grants)
    words.to_pickle(words_pickle)
    print("Saved to `{}`".format(words_pickle))

    print("Saving funders to file")
    with open(funder_ids_file, "w") as a:
        json.dump({"funders": funders}, a, indent=4)
    print("Saved to `{}`".format(funder_ids_file))


if __name__ == "__main__":
    fetch_data()
