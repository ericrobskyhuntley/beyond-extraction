# Beyond Extraction Resources

⛔️ DEPRECATED/NO LONGER MAINTAINED ⛔️

To scrape exhibitor data, simply run the following command from the terminal:

```sh
python pdac_scrape.py -p 'data/path/'
```

To populate a PostGIS database, first create the database and enable the PostGIS extension:

```sql
CREATE DATABASE pdac;
CREATE EXTENSION postgis;
```

You can then run the provided `.sql` files from the command line using the `psql` utility.

```sh
# To create and populate tables...
psql -h localhost -d pdac -U postgres -f ./sql/create-populate.sql
# To create views...
psql -h localhost -d pdac -U postgres -f ./sql/create-views.sql
```
