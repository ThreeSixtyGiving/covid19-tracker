import datetime
import json
import re

import click
import pandas as pd
from nltk.util import ngrams

from covidtracker.settings import (
    DB_URL,
    FUNDER_IDS_FILE,
    GRANTS_DATA_FILE,
    GRANTS_DATA_PICKLE,
    PRIORITIES,
    STOPWORDS,
    WORDS_PICKLE,
    DISABLE_UPDATE,
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


def get_location(value):
    if not value:
        return {}
    location = [loc for loc in value if loc["areatype"] == "lsoa"]
    return location[0] if location else value[0]


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

    if DISABLE_UPDATE:
        print("Updates are disabled, do nothing")
        return

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
        data = json.load(a)
        funders.extend(data.get("funders", []))
        regrants = data.get("regrants", [])
        manual_adjustments = data.get("manual_adjustments", {})
    funders = sorted(set(funders))
    print("Found {:,.0f} funder IDs".format(len(funders)))
    print("Found {:,.0f} regrant IDs".format(len(regrants)))

    # process the manual adjustments
    # Manual adjustments are included in the `funder_ids.json` file, in the following format:
    # ...
    # "manual_adjustments": {
    #     "grantProgramme.0.code": {  # Or another field
    #         "exclude": [
    #             "G2-SCH-2021-08-8532",
    #             ...list of values to exclude...
    #             "G2-SCH-2021-03-7422"
    #         ],
    #         "include": [
    #             "G2-SCH-2021-03-7435",
    #             ...list of values to include...
    #             "G2-SCH-2021-03-7427"
    #         ]
    #     }
    # }
    # ...
    manual_adjustments_include = []
    manual_adjustments_exclude = []
    manual_adjustments_params = {}
    for field, v in manual_adjustments.items():
        field_components = field.split(".")
        sql_field = "g.data{}->>'{}'".format(
            "".join(
                [
                    "->{}".format(f if f.isdigit() else f"'{f}'")
                    for f in field_components[:-1]
                ]
            ),
            field_components[-1],
        )
        if v.get("include"):
            manual_adjustments_include.append(f"or {sql_field} in %({field}_include)s")
            manual_adjustments_params[field + "_include"] = tuple(v["include"])
        if v.get("exclude"):
            manual_adjustments_exclude.append(
                f"and ({sql_field} not in %({field}_exclude)s or {sql_field} is null)"
            )
            manual_adjustments_params[field + "_exclude"] = tuple(v["exclude"])
    manual_adjustments_include = "\n".join(manual_adjustments_include)
    manual_adjustments_exclude = "\n".join(manual_adjustments_exclude)

    # fetch grants from the database
    print("Fetching grants")
    grant_sql = f"""
        with g as MATERIALIZED (select * from view_latest_grant)
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
            g.additional_data->'locationLookup' as "location",
            g."source_data"->'publisher'->>'prefix' as "publisher.prefix",
            g."source_data"->'publisher'->>'name' as "publisher.name",
            g."source_data"->>'license' as "license",
            g."source_data"->>'license_name' as "license_name",
            g.additional_data->'recipientOrgInfos' as "recipientOrgInfos",
            g.data as "grant"
        from g
        where (
                g.data->>'title' ~* 'covid|coronavirus|pandemic|cv-?19'
                or g.data->>'description' ~* 'covid|coronavirus|pandemic|cv-?19'
                or g.data->'grantProgramme'->0->>'title' ~* 'covid|coronavirus|pandemic|cv-?19'
                or g.data->>'classifications' ~* 'covid|coronavirus|pandemic|cv-?19'
                {manual_adjustments_include}
            )
            and to_date(g.data->>'awardDate', 'YYYY-MM-DD') > '2020-03-16'
            and to_date(g.data->>'awardDate', 'YYYY-MM-DD') < NOW() + interval '1 day'
            and g.data->>'currency' = 'GBP'
            -- covidtracker requires at least one recipientOrganization to display,
            -- i.e. it can't display grants to individuals.
            and jsonb_array_length(g.data->'recipientOrganization') >= 1
            {manual_adjustments_exclude}
        order by to_date(g.data->>'awardDate', 'YYYY-MM-DD'), g.data->>'id'
    """
    grants = pd.read_sql(
        grant_sql,
        con=db_url,
        params=manual_adjustments_params,
    )
    print("Fetched {:,.0f} grants from database".format(len(grants)))

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

    # add regranting details
    # Regrants are included in the `funder_ids.json` file, in the following format:
    # ...
    # "regrants": [
    #     "360G-CR-4915820",
    #     ...list of grants IDs to mark as regrants...
    #     "360G-CR-4854442"
    # ]
    # ...
    grants.loc[:, "_recipient_is_grantmaker"] = grants[
        "recipientOrganization.0.id"
    ].isin(funders)
    grants.loc[:, "_may_be_regranted"] = grants["_recipient_is_grantmaker"]
    grants.loc[grants["id"].isin(regrants), "_may_be_regranted"] = True

    locations = grants["location"].apply(get_location)
    grants.loc[:, "location.ladcd"] = locations.apply(lambda x: x.get("ladcd"))
    grants.loc[:, "location.ladnm"] = locations.apply(lambda x: x.get("ladnm"))
    grants.loc[:, "location.utlacd"] = locations.apply(lambda x: x.get("utlacd"))
    grants.loc[:, "location.utlanm"] = locations.apply(lambda x: x.get("utlanm"))
    grants.loc[:, "location.rgncd"] = locations.apply(lambda x: x.get("rgncd"))
    grants.loc[:, "location.rgnnm"] = locations.apply(lambda x: x.get("rgnnm"))
    grants.loc[:, "location.ctrycd"] = locations.apply(lambda x: x.get("ctrycd"))
    grants.loc[:, "location.ctrynm"] = locations.apply(lambda x: x.get("ctrynm"))
    grants.loc[:, "location.rgnctrycd"] = locations.apply(
        lambda x: x.get("rgncd") if x.get("ctrynm") == "England" else x.get("ctrycd")
    )
    grants.loc[:, "location.rgnctrynm"] = locations.apply(
        lambda x: "{} - {}".format(x.get("ctrynm"), x.get("rgnnm"))
        if x.get("ctrynm") == "England"
        else x.get("ctrynm")
    )
    grants.loc[:, "location.latitude"] = locations.apply(lambda x: x.get("latitude"))
    grants.loc[:, "location.longitude"] = locations.apply(lambda x: x.get("longitude"))
    grants.loc[:, "location.source"] = locations.apply(lambda x: x.get("source"))
    grants = grants.drop(columns=["location"])

    # add datetime field
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
        json.dump(
            {"funders": funders, **{k: v for k, v in data.items() if k != "funders"}},
            a,
            indent=4,
        )
    print("Saved to `{}`".format(funder_ids_file))


if __name__ == "__main__":
    fetch_data()
