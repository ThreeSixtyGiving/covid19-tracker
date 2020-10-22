# 360Giving COVID19 Grants Tracker

![360Giving Logo](https://www.threesixtygiving.org/wp-content/themes/360giving2020/assets/images/360-logos/360giving-main.svg)

A tracker for UK grants published to the [360Giving Data Standard](http://standard.threesixtygiving.org/),
using data from the [360Giving Datastore](https://www.threesixtygiving.org/data/360giving-datastore/).

The app is built using [Dash by Plotly](https://dash.plotly.com/), which is based around the Flask
python web framework and react.

## Run development version

```sh
python -m venv env # create virtual env
source env/bin/activate # enter virtual environment (`env/Scripts/activate` on windows)
pip install -r requirements.txt # install needed requirements
mv .env-sample .env # rename .env file (linux)
```

You'll then need to edit the `.env` file, adding the correct values for `DB_URL` (the database connection
for the 306Giving Datastore) and `MAPBOX_TOKEN` (which shows the map).

Once the settings are correct you need to fetch the latest data.

```sh
python covidtracker/fetchdata.py
```

Finally run the development server

```sh
python index.py
```

## Setup using [dokku](http://dokku.viewdocs.io/dokku/)

1. On server:

```sh
dokku apps:create covidtracker
```

2. On client:

```sh
git remote add dokku dokku@<IPADDRESS>:covidtracker

```

3. On server:

```sh
# create a persistant directory
mkdir -p  /var/lib/dokku/data/storage/covidtracker
chown -R dokku:dokku /var/lib/dokku/data/storage/covidtracker
chown -R 32767:32767 /var/lib/dokku/data/storage/covidtracker
dokku storage:mount covidtracker /var/lib/dokku/data/storage/covidtracker:/app/storage

# set up settings
dokku config:set covidtracker DB_URI=**DATABASE URL**
dokku config:set covidtracker GOOGLE_ANALYTICS=********
dokku config:set -no-restart covidtracker DATA_DIR=/app/storage/data
dokku config:set -no-restart covidtracker FLASK_APP=covidtracker.app:server

# set up redis
dokku redis:create covidtrackercache
dokku redis:link covidtrackercache covidtracker
```

4. Set up cron tab for scheduled tasks (on server)

```sh
nano /etc/cron.d/covidtracker
```