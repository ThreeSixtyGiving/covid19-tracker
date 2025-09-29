import os

import click
import pandas as pd

# from covidtracker.settings import AREAS_FILE
AREAS_FILE = os.getenv(
    "AREAS_FILE", os.path.join(os.path.dirname(__file__), "../assets/data/areas.json")
)

AREA_CSVS = [
    ("https://github.com/drkane/geo-lookups/raw/master/la_all_codes.csv", "LADCD"),
    ("https://github.com/drkane/geo-lookups/raw/master/msoa_la.csv", "MSOA11CD"),
    ("https://github.com/drkane/geo-lookups/raw/master/lsoa_la.csv", "LSOA11CD"),
]


@click.command()
@click.option(
    "--areas-file", default=AREAS_FILE, help="Location to save the list of funders"
)
def fetch_areas(areas_file=AREAS_FILE):
    df = pd.concat(
        [
            pd.read_csv(a[0], index_col=a[1])[
                [
                    "LAD20CD",
                    "LAD20NM",
                    "UTLACD",
                    "UTLANM",
                    "RGNCD",
                    "RGNNM",
                    "CTRYCD",
                    "CTRYNM",
                ]
            ]
            for a in AREA_CSVS
        ]
    )
    df = df[~df.index.duplicated()]
    print("Found {:,.0f} areas".format(len(df)))
    print("Saving areas to file")
    df.to_json(areas_file, orient="index", indent=4)
    print("Saved to `{}`".format(areas_file))


if __name__ == "__main__":
    fetch_areas()
