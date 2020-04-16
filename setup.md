

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
dokku config:set covidtracker DB_URI=**DATABASE URL**
dokku config:set covidtracker GOOGLE_ANALYTICS=********
```