

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

# set up redis
dokku redis:create covidtrackercache
dokku redis:link covidtrackercache covidtracker
```