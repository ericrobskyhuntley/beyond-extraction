-- Drop tables if they exist.
DROP TABLE IF EXISTS prospectors;
DROP TABLE IF EXISTS ix_by_booth;
DROP TABLE IF EXISTS ix_by_commodity;
DROP TABLE IF EXISTS ix_by_country;
DROP TABLE IF EXISTS ix;
DROP TABLE IF EXISTS ts_by_biztype;
DROP TABLE IF EXISTS ts_by_booth;
DROP TABLE IF EXISTS ts;
DROP TABLE IF EXISTS cs_by_projects;
DROP TABLE IF EXISTS cs;
DROP TABLE IF EXISTS booths;
DROP TABLE IF EXISTS countries;

-- Create booths table.
CREATE TABLE booths (
    booth_no VARCHAR(5),
    type CHAR(2),
    geom geometry(POLYGON, 4326, 2),
    CONSTRAINT booth_pkey PRIMARY KEY (booth_no)
);

-- Create prospectors table.
CREATE TABLE prospectors (
    name VARCHAR(50),
    booth_no VARCHAR (5),
    CONSTRAINT prospectors_pkey PRIMARY KEY (name),
    FOREIGN KEY (booth_no) REFERENCES booths(booth_no)
);

-- Create investors table.
CREATE TABLE ix (
    name VARCHAR(50),
    exchange VARCHAR,
    symbol VARCHAR,
    stock VARCHAR,
    add VARCHAR,
    country CHAR(3),
    website VARCHAR,
    geom GEOMETRY(POINT, 0, 2),
    CONSTRAINT investors_pkey PRIMARY KEY (name)
);

COPY ix(name, exchange, symbol, stock, add, country, website, geom)
FROM '/Users/ehuntley/Desktop/data/beyond-extraction/data/firms_ix.csv'  DELIMITER ',' CSV HEADER;
SELECT UpdateGeometrySRID('public', 'ix', 'geom', 4326);

-- Create trade show table.
CREATE TABLE ts (
    name VARCHAR(50),
    exchange VARCHAR(30),
    symbol VARCHAR(10),
    stock VARCHAR(10),
    add VARCHAR(200),
    country CHAR (2),
    website VARCHAR(100),
    geom GEOMETRY(POINT, 4326, 2),
    CONSTRAINT trade_pkey PRIMARY KEY (name)
);

-- Create trade show by biztype relationship table.
CREATE TABLE ts_by_biztype (
    id SERIAL NOT NULL,
    name VARCHAR(50),
    biztype VARCHAR(100),
    CONSTRAINT t_by_biz_pkey PRIMARY KEY (id),
    FOREIGN KEY (name) REFERENCES ts(name)
);

-- Create trade show by booth relationship table.
CREATE TABLE ts_by_booth (
    id SERIAL NOT NULL,
    name VARCHAR(50),
    booth_no VARCHAR(5),
    CONSTRAINT t_by_b_pkey PRIMARY KEY (id),
    FOREIGN KEY (name) REFERENCES ts(name),
    FOREIGN KEY (booth_no) REFERENCES booths(booth_no)
);

-- Create countries table.
CREATE TABLE countries (
    country VARCHAR(50),
    geom GEOMETRY(MULTIPOLYGON, 4326, 2),
    CONSTRAINT countries_pkey PRIMARY KEY (country)
);

-- Create investors by booth relationship table.
CREATE TABLE ix_by_booth (
    id SERIAL NOT NULL,
    name VARCHAR(50),
    booth_no VARCHAR(5),
    CONSTRAINT i_by_b_pkey PRIMARY KEY (id),
    FOREIGN KEY (name) REFERENCES ix(name),
    FOREIGN KEY (booth_no) REFERENCES booths(booth_no)
);

-- Create investors by commodity relationship table.
CREATE TABLE ix_by_commodity (
    id SERIAL NOT NULL,
    name VARCHAR(50),
    commodity VARCHAR(100),
    CONSTRAINT i_by_c_pkey PRIMARY KEY (id),
    FOREIGN KEY (name) REFERENCES ix(name)
);

-- Create investors by country relationship table.
CREATE TABLE ix_by_country (
    id SERIAL NOT NULL,
    name VARCHAR(50),
    country VARCHAR(50),
    CONSTRAINT i_by_cn_pkey PRIMARY KEY (id),
    FOREIGN KEY (name) REFERENCES ix(name),
    FOREIGN KEY (country) REFERENCES countries(country)
);

-- Create core shack table.
CREATE TABLE cs (
    name VARCHAR(50),
    exchange VARCHAR(30),
    symbol VARCHAR(10),
    stock VARCHAR(10),
    add VARCHAR(200),
    country CHAR (2),
    website VARCHAR(100),
    geom GEOMETRY(POINT, 4326, 2),
    CONSTRAINT cs_pkey PRIMARY KEY (name)
);

-- Create core shack by project table.
CREATE TABLE cs_by_projects (
    proj VARCHAR(50),
    loc VARCHAR(50),
    country CHAR (2),
    name VARCHAR(50),
    geom GEOMETRY(POINT, 4326, 2),
    CONSTRAINT c_by_p_pkey PRIMARY KEY (proj),
    FOREIGN KEY (name) REFERENCES cs(name)
);