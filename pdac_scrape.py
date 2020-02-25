# -*- coding: utf-8 -*-
"""
Scrape PDAC site for exhibitor information.
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
parser.add_argument('-p', '--path', help = 'Directory in which to write data.')
args = parser.parse_args()

if args.path:
   DIR = args.path
else: 
   print('Please supply directory in which to write data.')
   exit()

# Needed to modify Natural Earth Data---French Guiana depicted as a multipart geometry of France. (And not even distinguished.)
COUNTRIES = gpd.read_file(DIR + 'countries-custom.geojson')
COUNTRIES.columns = map(str.lower, COUNTRIES.columns)
COUNTRIES = COUNTRIES[['name','name_long', 'iso_a2', 'iso_a3', 'geometry']]
COUNTRIES['geometry'] = COUNTRIES.centroid

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

if path.isfile(DIR + 'addresses.geojson'):
    ADDRESSES = gpd.read_file(DIR + 'addresses.geojson')
else: 
    ADDRESSES = pd.read_csv(DIR + 'addresses.csv')
    ADDRESSES = gpd.GeoDataFrame(
            ADDRESSES.apply(lambda x: gc(x, 'add', 'country'), axis=1), 
            geometry='geometry'
            )
    ADDRESSES.to_file(DIR + 'addresses.geojson', driver='GeoJSON')

print(ADDRESSES.head())
def country_locate(country_op):
    for i, c in COUNTRIES.iterrows():
        if c['name_long'] in country_op['country']:
            country_op['geometry'] = c['geometry']
            break
        else:
            country_op['geometry'] = None
    return country_op

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
    firms = df[['name', 'booth', 'website']]
    projects = df[['proj', 'loc', 'country', 'name']]
    return (firms, projects)
    
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
                        'booth': booth.replace('corpmember, ', '').replace('A', '').replace('B',''),
                        'website': website,
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
        return firms

def clean_countries(df):
    df = df.replace(
        ["Cote D'ivoire", 
        'Bosnia And Herzegowina', 
        'Laos',
        'Viet Nam', 
        'Congo, Democratic Republic Of'],
        ["Côte d'Ivoire", 
        'Bosnia and Herzegovina', 
        'Lao PDR',
        'Vietnam', 
        'Democratic Republic of the Congo']
    )
    # Remove null values
    df = df[df['country'] != 'NULL']
    return df


def run_ix(directory):
    # INVESTORS EXCHANGE
    ix_url = 'https://www.pdac.ca/convention/exhibits/investors-exchange/'
    print("Scraping IX exhibitors alphabetically...")
    firms =  pdac_by_x(
        url = ix_url + 'exhibitors',
        x_id = 'alphaChars', 
        x_name = 'alpha',
        x_keep=False
        )
    print("Geocoding IX exhibitors...")
    firms = ADDRESSES.merge(firms, on='name', how='right')
    print("Writing IX exhibitors to GeoJSON...")
    firms.to_file(directory + 'firms_ix.geojson', driver='GeoJSON')
    
    print("Scraping investors exchange exhibitors by commodity...")
    commodities, firms_by_commodity =  pdac_by_x(
        url = ix_url + 'exhibitor-list-by-commodity',
        x_id = 'commodityTypes', 
        x_name = 'commodity')
    print("Writing commodities to CSV...")
    commodities.to_csv(directory + 'commodities.csv')
    print("Writing firm-commodity relationship to CSV...")
    firms_by_commodity.to_csv(directory + 'firms_by_commodity.csv')
    
    print("Scraping investors exchange exhibitors by country of exploration...")
    countries, firms_by_country = pdac_by_x(
        url = ix_url + 'exhibitor-list-by-country-of-exploration',
        x_id = 'countries',
        x_name = 'country'
        )
    countries = clean_countries(countries)
    print("Locating countries...")
    countries = gpd.GeoDataFrame(
        countries.apply(
            country_locate, axis=1
            ), 
        geometry='geometry'
        )
    countries = countries.dropna(subset=['geometry'])
    print("Writing countries to GeoJSON...")
    countries.to_file(directory + 'countries.geojson', driver='GeoJSON')
    print("Writing firm-country relationship to CSV...")
    firms_by_country.to_csv(directory + 'firms_by_country.csv')
    
def run_ts(directory):
    # TRADE SHOW
    ts_url = 'https://www.pdac.ca/convention/exhibits/trade-show/'
    print("Scraping trade show exhibitors alphabetically...")
    firms = pdac_by_x(
        url = ts_url + 'exhibitors',
        x_id = 'alphaChars',
        x_name = 'alpha',
        x_keep = False
    )
    print("Geocoding IX exhibitors...")
    firms = ADDRESSES.merge(firms, on='name', how='right')
    print("Writing TS exhibitors to GeoJSON...")
    firms.to_file(directory + 'firms_ts.geojson', driver='GeoJSON')
    
    print("Scraping trade show exhibitors by business type...")
    biztypes, ts_by_biztype = pdac_by_x(
        url = ts_url + 'exhibitor-list-by-business-type',
        x_id = 'businessTypes',
        x_name = 'biztype'
    )
    print("Writing to CSV...")
    biztypes.to_csv(directory + 'biztypes.csv')
    ts_by_biztype.to_csv(directory + 'firms_by_biztype.csv')
    
def run_cs(directory):
    # CORE SHACK
    cs_urls = ['https://www.pdac.ca/convention/exhibits/core-shack/session-a-exhibitors',
                'https://www.pdac.ca/convention/exhibits/core-shack/session-b-exhibitors']
    print("Scraping Core Shack (CS) exhibitors and geocoding projects...")
    firms, projects = core_shack(cs_urls)
    firms = ADDRESSES.merge(firms, on='name', how='right')
    firms = gpd.GeoDataFrame(firms, geometry='geometry')

    print("Writing CS exhibitors to GeoJSON...")
    firms.to_file(directory + 'firms_cs.geojson', driver='GeoJSON')
    print("Geocoding CS projects...")
    projects = gpd.GeoDataFrame(
        projects.apply(lambda x: gc(x, 'loc', 'country'), axis=1),
        geometry='geometry'
        )
    print("Writing CS projects to GeoJSON...")
    projects.to_file(directory + 'firms_by_projects.geojson', driver='GeoJSON')

def run_pt(directory):
    pt_url = 'https://www.pdac.ca/convention/exhibits/prospectors-tent/exhibitors'
    print("Scraping Prospectors Tent (PT) exhibitors...")
    prospectors = pros_tent(pt_url)
    print("Writing PT exhibitors to CSV...")
    prospectors.to_csv(directory + 'prospectors.csv')


if __name__ == '__main__':
   run_ix(DIR)
   run_ts(DIR)
   run_cs(DIR)
   run_pt(DIR)
   print("Done.")
