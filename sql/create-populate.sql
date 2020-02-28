-- Drop views if they exist.

DROP VIEW IF EXISTS exhibitor_addresses;
DROP VIEW IF EXISTS investor_to_countries;
DROP VIEW IF EXISTS booth_to_investor;
DROP VIEW IF EXISTS investor_by_countries;
DROP VIEW IF EXISTS booth_summary;

-- Drop tables if they exist.

DROP TABLE IF EXISTS ix_by_commodity;
DROP TABLE IF EXISTS ix_by_country;
DROP TABLE IF EXISTS ts_by_biztype;
DROP TABLE IF EXISTS cs_by_projects;
DROP TABLE IF EXISTS exhibitor_by_booth;
DROP TABLE IF EXISTS exhibitors;
DROP TABLE IF EXISTS booths;
DROP TABLE IF EXISTS countries;

-- Create booths table.

CREATE TABLE booths (
    booth_no VARCHAR(5),
    type CHAR(2),
    geom geometry(POLYGON, 0, 2),
    CONSTRAINT booth_pkey PRIMARY KEY (booth_no),
    CONSTRAINT check_types 
        CHECK (type IN ('ts', 'tn', 'ix', 'pt', 'cs') )
);

-- Populate booths table.

COPY booths(booth_no, type, geom)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/booths.csv'  DELIMITER ',' CSV HEADER;

SELECT UpdateGeometrySRID('public', 'booths', 'geom', 4326);

-- Create exhibitors table.

CREATE TABLE exhibitors (
    name VARCHAR,
    exchange VARCHAR,
    symbol VARCHAR,
    stock VARCHAR,
    add VARCHAR,
    city VARCHAR,
    region VARCHAR,
    state VARCHAR,
    country CHAR(3),
    website VARCHAR,
    geom GEOMETRY(POINT, 0, 2),
    CONSTRAINT investors_pkey PRIMARY KEY (name)
);

-- Create exhibitor-booth relationship table.

CREATE TABLE exhibitor_by_booth (
    id SERIAL NOT NULL,
    name VARCHAR,
    booth_no VARCHAR(5),
    CONSTRAINT t_by_b_pkey PRIMARY KEY (id),
    FOREIGN KEY (name) REFERENCES exhibitors(name),
    FOREIGN KEY (booth_no) REFERENCES booths(booth_no)
);

-- Populate exhibitors table from IX, trade show, core shack.

CREATE TEMP TABLE ex
(LIKE exhibitors INCLUDING DEFAULTS)
ON COMMIT PRESERVE ROWS;

COPY ex(add,city,country,exchange,geom,name,region,state,stock,symbol,website)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/firms_ix.csv'  DELIMITER ',' CSV HEADER;
COPY ex(add,city,country,exchange,geom,name,region,state,stock,symbol,website)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/firms_ts.csv'  DELIMITER ',' CSV HEADER;
COPY ex(add,city,country,exchange,geom,name,region,state,stock,symbol,website)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/firms_cs.csv'  DELIMITER ',' CSV HEADER;

INSERT INTO exhibitors SELECT * FROM ex 
ON CONFLICT DO NOTHING;

DROP TABLE ex;

-- Populate exhibitors table from Prospectors Tent.

CREATE TEMPORARY TABLE prospectors (
    name VARCHAR(50),
    booth_no VARCHAR (5)
)
ON COMMIT PRESERVE ROWS;

COPY prospectors(booth_no, name)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/prospectors.csv'  DELIMITER ',' CSV HEADER;
INSERT INTO exhibitors (name) SELECT name FROM prospectors ON CONFLICT DO NOTHING;

-- Update exhibitor CRS (necessary due to CSV import).

SELECT UpdateGeometrySRID('public', 'exhibitors', 'geom', 4326);

-- Populate exhibitors-booth relationship tables from all categories.

COPY exhibitor_by_booth(name, booth_no)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/firms_ix_by_booth.csv'  DELIMITER ',' CSV HEADER;
COPY exhibitor_by_booth(name, booth_no)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/firms_ts_by_booth.csv'  DELIMITER ',' CSV HEADER;
COPY exhibitor_by_booth(name, booth_no)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/firms_cs_by_booth.csv'  DELIMITER ',' CSV HEADER;
INSERT INTO exhibitor_by_booth(name, booth_no) SELECT name, booth_no FROM prospectors 
ON CONFLICT DO NOTHING;

-- Done with prospectors temp table.

DROP TABLE prospectors;

-- Create trade show-biztype relationship table.

CREATE TABLE ts_by_biztype (
    id SERIAL NOT NULL,
    name VARCHAR,
    biztype VARCHAR,
    CONSTRAINT t_by_biz_pkey PRIMARY KEY (id),
    FOREIGN KEY (name) REFERENCES exhibitors(name)
);

-- Populate trade show-biztype relationship table.

COPY ts_by_biztype(name, biztype)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/firms_ts_by_biztype.csv'  DELIMITER ',' CSV HEADER;

-- Create countries table.

CREATE TABLE countries (
    country VARCHAR,
    country_long VARCHAR,
    iso_a2 CHAR(3),
    iso_a3 CHAR(3),
    geom GEOMETRY(MULTIPOLYGON, 0, 2),
    CONSTRAINT countries_pkey PRIMARY KEY (country_long)
);

-- Populate countries table with Natural Earth data (csv-ed).

COPY countries(country, country_long, iso_a2, iso_a3, geom)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/countries.csv'  DELIMITER ',' CSV HEADER;

-- Update countries CRS (necessary due to CSV import).

SELECT UpdateGeometrySRID('public', 'countries', 'geom', 4326);

-- Create investor-commodity relationship table.

CREATE TABLE ix_by_commodity (
    id SERIAL NOT NULL,
    name VARCHAR,
    commodity VARCHAR,
    CONSTRAINT i_by_c_pkey PRIMARY KEY (id),
    FOREIGN KEY (name) REFERENCES exhibitors(name)
);

-- Populate investor-commodity relationship table.

COPY ix_by_commodity(name, commodity)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/firms_ix_by_commodity.csv'  DELIMITER ',' CSV HEADER;

-- Create investor-country relationship table.

CREATE TABLE ix_by_country (
    id SERIAL NOT NULL,
    name VARCHAR,
    country VARCHAR,
    CONSTRAINT i_by_cn_pkey PRIMARY KEY (id),
    FOREIGN KEY (name) REFERENCES exhibitors(name),
    FOREIGN KEY (country) REFERENCES countries(country_long)
);

-- Populate investor-country relationship table.

COPY ix_by_country(name, country)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/firms_ix_by_country.csv'  DELIMITER ',' CSV HEADER;

-- Create core shack-project relationship table.

CREATE TABLE cs_by_projects (
    proj VARCHAR,
    loc VARCHAR,
    city VARCHAR,
    region VARCHAR,
    state VARCHAR,
    country CHAR (3),
    name VARCHAR,
    geom GEOMETRY(POINT, 0, 2),
    CONSTRAINT c_by_p_pkey PRIMARY KEY (proj),
    FOREIGN KEY (name) REFERENCES exhibitors(name)
);

-- Populate core shack-project relationship table.

COPY cs_by_projects(proj,loc,country,name,geom,city,region,state)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/firms_cs_by_projects.csv'  DELIMITER ',' CSV HEADER;

-- Update CS project CRS (necessary due to CSV import).

SELECT UpdateGeometrySRID('public', 'cs_by_projects', 'geom', 4326);