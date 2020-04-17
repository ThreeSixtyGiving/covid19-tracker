

1. On server:

```sh
dokku apps:create covidtracker
```

2. On client:

```sh
git remote add dokku dokku@64.227.43.70:covidtracker

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
dokku config:set -no-restart covidtracker GRANTS_DATA_FILE=/app/storage/data/grants_data.json
dokku config:set -no-restart covidtracker FUNDER_IDS_FILE=/app/storage/data/funder_ids.json
```