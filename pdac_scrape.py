# -*- coding: utf-8 -*-
"""
Scrape PDAC site for exhibitor information.

Eric Robsky Huntley (ehuntley@mit.edu)
On behalf of Graphe.
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from argparse import ArgumentParser
import unidecode
from opencage.geocoder import OpenCageGeocode
from os import environ, path
import geopandas as gpd
from shapely.geometry import Point

parser = ArgumentParser()
parser.add_argument('-p', 
    '--path', 
    help = 'Directory in which to write data.'
    )
parser.add_argument('-g', 
    '--regeocode',
    action='store_true', 
    help = 'Recode addresses.'
    )
args = parser.parse_args()

if args.path:
   DIR = args.path
else: 
   print('Please supply directory in which to write data.')
   exit()
RECODE = args.regeocode

# Read modified Natural Earth Data.
# E.g., French Guiana depicted as a multipart geometry of France.

COUNTRIES = gpd.read_file(DIR + 'countries.geojson')
COUNTRIES.columns = map(str.lower, COUNTRIES.columns)
COUNTRIES = COUNTRIES[['name','name_long', 'iso_a2', 'iso_a3', 'geometry']]
COUNTRIES.to_csv(DIR + 'countries.csv', index=False)

BOOTHS = gpd.read_file(DIR + 'booths.geojson')
BOOTHS.to_csv(DIR + 'booths.csv', index=False)

GEOCODER = OpenCageGeocode(environ['OPENCAGE'])

def gc(row, query, country):
    q = row[query]
    is_q = isinstance(q, str)
    if is_q:
        q = q.strip()
    country = row[country]
    is_country = isinstance(country, str)
    if is_country:
        country = country.strip()
    if is_q and is_country:
        print('Geocoding ' + str(q) + '...')
        result = GEOCODER.geocode(q, countrycode=country)
    elif is_q:
        print('Geocoding ' + str(q) + '...')
        result = GEOCODER.geocode(q)
    else:
        result = None
    if result and len(result):
        row['geometry'] = Point(result[0]['geometry']['lng'], result[0]['geometry']['lat'])
    else:
        row['geometry'] = None
    return row

if RECODE:
    ADDRESSES = pd.read_csv(DIR + 'addresses.csv')
    ADDRESSES = gpd.GeoDataFrame(
            ADDRESSES.apply(lambda x: gc(x, 'add', 'country'), axis=1), 
            geometry='geometry'
            )
    ADDRESSES.to_file(DIR + 'addresses.geojson', driver='GeoJSON')
else:
    ADDRESSES = gpd.read_file(DIR + 'addresses.geojson')

def pros_tent(url):
    prospectors = pd.DataFrame()
    pros_soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    items = pros_soup.find_all('div', class_='sfitem')
    for i in items:
        full_name = i.find('p', class_='sfitemTitle')
        name = full_name.find('strong').get_text()
        if name:
            name.strip()
        booth = i.find('div', class_='sfitemBoothNumbers')
        if booth:
            booth = booth.get_text().strip()
        f = pd.Series({
                'name': name,
                'booth': booth.replace('corpmember, ', '').replace('A', '').replace('B','')
                })
        prospectors = prospectors.append(f, ignore_index=True)
    return prospectors

def core_shack(urls):
    df = pd.DataFrame()
    for l in urls:
        country_soup = BeautifulSoup(requests.get(l).content, 'html.parser')
        items = country_soup.find_all('div', class_='sfitem')
        for i in items:
            full_name = i.find('p', class_='sfitemTitle')
            proj_elem = full_name.find('strong')
            if proj_elem:
                proj = proj_elem.get_text().strip()[:-1]
            name = full_name.get_text().split(',', 1)[0].strip()
            loc = unidecode.unidecode(proj_elem.next_sibling.strip())
            for iter, c in COUNTRIES.iterrows():
                if (" " + c['name_long'] in loc) or (" " + c['iso_a3'] in loc) or (" " + c['iso_a2'] in loc):
                    country = c['iso_a2'].lower()
                    break
                else:
                    country = None
            loc = ','.join(loc.split(',')[0:-1]).strip()
            booth = i.find('div', class_='sfitemBoothNumbers')
            if booth:
                booth = booth.get_text().strip()
            website = i.find('div', class_='sfitemRichText')
            if website:
                website = website.find('a').get('href').strip()
            f = pd.Series({
                    'name': name,
                    'proj': proj,
                    'loc': loc,
                    'country': country,
                    'booth': booth.replace('corpmember, ', '').replace('A', '').replace('B',''),
                    'website': website
                    })
            df = df.append(f, ignore_index=True)
    firms = df[['name', 'website']]
    firms_by_booth = df[['name', 'booth']]
    projects = df[['proj', 'loc', 'country', 'name']]
    return (firms, firms_by_booth, projects)
    
def pdac_by_x(url, x_id, x_name, x_keep = True):
    base_url = url
    base_page = requests.get(base_url)
    soup = BeautifulSoup(base_page.content, 'html.parser')
    
    links = []
    for link in soup.find('div', id=x_id).find_all('a'):
        x = {
                'x': link.get_text(),
                'link': base_url + link.get('href')
                }
        links.append(x)
    firms = pd.DataFrame()
    for l in links:
        link_soup = BeautifulSoup(requests.get(l['link']).content, 'html.parser')
        items = link_soup.find_all('div', class_='sfitem')
        for i in items:
            name = i.find('p', class_='sfitemTitle')
            if name:
                name = name.get_text().strip()
            booth = i.find('div', class_='sfitemBoothNumbers')
            if booth:
                booth = booth.get_text().strip()
            website = i.find('div', class_='sfitemRichText')
            if website:
                website = website.find('a').get('href')
            if x_keep:
                firm = pd.Series({
                        'name': name,
                        x_name: l['x']
                        })
            else:
                firm = pd.Series({
                        'name': name,
                        'booth': booth.replace('corpmember, ', '').replace('A', '').replace('B',''),
                        'website': website,
                        })
            firms = firms.append(firm, ignore_index=True)
    if x_keep:
        xs = firms.drop_duplicates(subset=x_name).reset_index(drop=True)[[x_name]]
        return(xs, firms[['name', x_name]])
    else:
        firms_by_booth = firms.set_index(['name','website'])
        firms_by_booth = firms_by_booth.apply(lambda x: x.str.split(', ').explode()).reset_index()
        firms = firms[['name', 'website']]
        firms_by_booth = firms_by_booth[['name', 'booth']]
        return (firms, firms_by_booth)

def clean_countries(df):
    df = df.replace(
        ["Cote D'ivoire", 
        'Bosnia And Herzegowina', 
        'Laos',
        'Viet Nam', 
        'Congo, Democratic Republic Of',
        'Myanmar (Burma)',
        'Tanzania, United Republic Of'],
        ["Côte d'Ivoire", 
        'Bosnia and Herzegovina', 
        'Lao PDR',
        'Vietnam', 
        'Democratic Republic of the Congo',
        'Myanmar',
        'Tanzania']
    )
    # Remove null and invalid values
    df = df[df['country'] != 'NULL']
    df = df[df['country'] != 'Africa']
    df = df[df['country'] != 'West Africa']
    return df

def run_ix(directory):
    # INVESTORS EXCHANGE
    ix_url = 'https://www.pdac.ca/convention/exhibits/investors-exchange/'
    print("Scraping Investors Exchange (IX) exhibitors alphabetically...")
    firms, firms_by_booth =  pdac_by_x(
        url = ix_url + 'exhibitors',
        x_id = 'alphaChars', 
        x_name = 'alpha',
        x_keep=False
        )
    print("Geocoding IX exhibitors...")
    firms = ADDRESSES.merge(firms, on='name', how='right')

    print("Writing IX exhibitors to GeoJSON and CSV...")
    firms.to_file(directory + 'firms_ix.geojson', driver='GeoJSON')
    firms.to_csv(directory + 'firms_ix.csv', index=False)
    print("Writing IX firm-booth relationship to CSV...")
    firms_by_booth.to_csv(directory + 'firms_ix_by_booth.csv', index=False)
    
    print("Scraping IX exhibitors by commodity...")
    _, firms_by_commodity =  pdac_by_x(
        url = ix_url + 'exhibitor-list-by-commodity',
        x_id = 'commodityTypes', 
        x_name = 'commodity')
    print("Writing IX firm-commodity relationship to CSV...")
    firms_by_commodity.to_csv(directory + 'firms_ix_by_commodity.csv', index=False)
    
    print("Scraping investors exchange exhibitors by country of exploration...")
    countries, firms_by_country = pdac_by_x(
        url = ix_url + 'exhibitor-list-by-country-of-exploration',
        x_id = 'countries',
        x_name = 'country'
        )
    firms_by_country = clean_countries(firms_by_country)
    print("Writing firm-country relationship to CSV...")
    firms_by_country.to_csv(directory + 'firms_ix_by_country.csv', index=False)
    
def run_ts(directory):
    # TRADE SHOW
    ts_url = 'https://www.pdac.ca/convention/exhibits/trade-show/'
    print("Scraping trade show exhibitors alphabetically...")
    firms, firms_by_booth = pdac_by_x(
        url = ts_url + 'exhibitors',
        x_id = 'alphaChars',
        x_name = 'alpha',
        x_keep = False
    )
    print("Geocoding Trade Show (TS) exhibitors...")
    firms = ADDRESSES.merge(firms, on='name', how='right')
    print("Writing TS exhibitors to GeoJSON and CSV...")
    firms.to_file(directory + 'firms_ts.geojson', driver='GeoJSON')
    firms.to_csv(directory + 'firms_ts.csv', index=False)
    print("Writing TS firm-booth relationship to CSV...")
    firms_by_booth.to_csv(directory + 'firms_ts_by_booth.csv', index=False)

    print("Scraping TS exhibitors by business type...")
    _, ts_by_biztype = pdac_by_x(
        url = ts_url + 'exhibitor-list-by-business-type',
        x_id = 'businessTypes',
        x_name = 'biztype'
    )
    print("Writing to CSV...")
    ts_by_biztype.to_csv(directory + 'firms_ts_by_biztype.csv', index=False)
    
def run_cs(directory):
    # CORE SHACK
    cs_urls = ['https://www.pdac.ca/convention/exhibits/core-shack/session-a-exhibitors',
                'https://www.pdac.ca/convention/exhibits/core-shack/session-b-exhibitors']
    print("Scraping Core Shack (CS) exhibitors and geocoding projects...")
    firms, firms_by_booth, projects = core_shack(cs_urls)
    firms = ADDRESSES.merge(firms, on='name', how='right')

    print("Writing CS exhibitors to GeoJSON...")
    firms.to_file(directory + 'firms_cs.geojson', driver='GeoJSON')
    firms.to_csv(directory + 'firms_cs.csv', index=False)
    firms_by_booth.to_csv(directory + 'firms_cs_by_booth.csv', index=False)
    print("Geocoding CS projects...")
    projects = gpd.GeoDataFrame(
        projects.apply(lambda x: gc(x, 'loc', 'country'), axis=1),
        geometry='geometry'
        )
    print("Writing CS projects to GeoJSON...")
    projects.to_file(directory + 'firms_cs_by_projects.geojson', driver='GeoJSON')
    projects.to_csv(directory + 'firms_cs_by_projects.csv', index=False)

def run_pt(directory):
    pt_url = 'https://www.pdac.ca/convention/exhibits/prospectors-tent/exhibitors'
    print("Scraping Prospectors Tent (PT) exhibitors...")
    prospectors = pros_tent(pt_url)
    print("Writing PT exhibitors to CSV...")
    prospectors.to_csv(directory + 'prospectors.csv', index=False)

if __name__ == '__main__':
   run_ix(DIR)
   run_ts(DIR)
   run_cs(DIR)
   run_pt(DIR)
   print("Done.")
