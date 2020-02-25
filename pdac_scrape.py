# -*- coding: utf-8 -*-
"""
Scrape PDAC site for vendor and prospector information.
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from argparse import ArgumentParser
import unidecode
from opencage.geocoder import OpenCageGeocode
from os import environ
import geopandas as gpd
from shapely.geometry import Point

parser = ArgumentParser()
parser.add_argument('-d', '--directory', help = 'Directory in which to write data.')
args = parser.parse_args()

if args.directory:
   DIR = args.directory + 'data/'
else: 
   print('Please supply directory in which to write data.')
   exit()

# Needed to modify Natural Earth Data---French Guiana depicted as a multipart geometry of France. (And not even distinguished.)
COUNTRIES = gpd.read_file('/home/ericmhuntley/Desktop/beyond-extraction/data/countries-custom.geojson')
COUNTRIES.columns = map(str.lower, COUNTRIES.columns)
COUNTRIES = COUNTRIES[['name','name_long', 'iso_a2', 'iso_a3', 'geometry']]
COUNTRIES['geometry'] = COUNTRIES.centroid

ADDRESSES = pd.read_csv('/home/ericmhuntley/Desktop/beyond-extraction/data/addresses.csv')
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

def country_locate(country_op):
    for i, c in COUNTRIES.iterrows():
        if c['name_long'] in country_op['country']:
            country_op['geometry'] = c['geometry']
            break
        else:
            country_op['geometry'] = None
    return country_op

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
                    'booth': booth.replace('corpmember, ', ''),
                    'website': website
                    })
            df = df.append(f, ignore_index=True)
    firms = df[['name', 'booth', 'website']]
    projects = df[['proj', 'loc', 'country', 'name']]
    return (firms, projects)
    
def pdac_by_x(url, thing_id, thing_name, keep_thing = True):
    base_url = url
    base_page = requests.get(base_url)
    soup = BeautifulSoup(base_page.content, 'html.parser')
    
    links = []
    for link in soup.find('div', id=thing_id).find_all('a'):
        thing = {
                'thing': link.get_text(),
                'link': base_url + link.get('href')
                }
        links.append(thing)
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
            if keep_thing:
                firm = pd.Series({
                        'name': name,
                        'booth': booth.replace('corpmember, ', ''),
                        'website': website,
                        thing_name: l['thing']
                        })
            else:
                firm = pd.Series({
                        'name': name,
                        'booth': booth.replace('corpmember, ', ''),
                        'website': website,
                        })
            firms = firms.append(firm, ignore_index=True)
    if keep_thing:
        things = firms.drop_duplicates(subset=thing_name).reset_index(drop=True)[[thing_name]]
        return(things, firms[['name', thing_name]])
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
        
    print("Scraping IX exhibitors alphabetically...")
    firms =  pdac_by_x(url = 'https://www.pdac.ca/convention/exhibits/investors-exchange/exhibitors',
                             thing_id = 'alphaChars', 
                             thing_name = 'alpha',
                             keep_thing=False
                             )
    print("Geocoding IX exhibitors...")
    firms = firms.merge(ADDRESSES, on='name', how='left')
    firms = gpd.GeoDataFrame(
        firms.apply(lambda x: gc(x, 'add', 'country'), axis=1), 
        geometry='geometry'
        )
    print("Writing IX exhibitors to GeoJSON...")
    firms.to_file(directory + 'firms_ix.geojson', 
        driver='GeoJSON',
        index_label='id'
        )
    
    print("Scraping investors exchange exhibitors by commodity...")
    commodities, firms_by_commodity =  pdac_by_x(url = 'https://www.pdac.ca/convention/exhibits/investors-exchange/exhibitor-list-by-commodity',
                                 thing_id = 'commodityTypes', 
                                 thing_name = 'commodity'
                                 )
    print("Writing commodities to CSV...")
    commodities.to_csv(directory + 'commodities.csv', 
        index_label='id'
        )
    print("Writing firm-commodity relationship to CSV...")
    firms_by_commodity.to_csv(directory + 'firms_by_commodity.csv', 
        index_label='id'
        )
    
    print("Scraping investors exchange exhibitors by country of exploration...")
    countries, firms_by_country = pdac_by_x(url = 'https://www.pdac.ca/convention/exhibits/investors-exchange/exhibitor-list-by-country-of-exploration',
                              thing_id = 'countries', 
                              thing_name = 'country'
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
    countries.to_file(directory + 'countries.geojson',
        driver='GeoJSON', 
        index_label='id'
        )
    print("Writing firm-country relationship to CSV...")
    firms_by_country.to_csv(directory + 'firms_by_country.csv', 
        index_label='id'
        )
    
def run_ts(directory):
    # TRADE SHOW
    
    print("Scraping trade show exhibitors alphabetically...")
    firms = pdac_by_x(url = 'https://www.pdac.ca/convention/exhibits/trade-show/exhibitors',
                            thing_id = 'alphaChars',
                            thing_name = 'alpha',
                            keep_thing = False
                            )
    print("Geocoding IX exhibitors...")
    firms = firms.merge(ADDRESSES, on='name', how='left')
    firms = gpd.GeoDataFrame(
        firms.apply(lambda x: gc(x, 'add', 'country'), axis=1),
        geometry='geometry'
    )
    print("Writing TS exhibitors to GeoJSON...")
    firms.to_file(directory + 'firms_ts.geojson',
                  driver='GeoJSON',
                  index_label='id'
                  )
    
    print("Scraping trade show exhibitors by business type...")
    biztypes, ts_by_biztype = pdac_by_x(url = 'https://www.pdac.ca/convention/exhibits/trade-show/exhibitor-list-by-business-type',
                          thing_id = 'businessTypes',
                          thing_name = 'biztype'
                          )
    print("Writing to CSV...")
    biztypes.to_csv(directory + 'biztypes.csv', index_label='id')
    ts_by_biztype.to_csv(directory + 'firms_by_biztype.csv', index_label='id')
    
def run_cs(directory):
    # CORE SHACK
    
    # print("Scraping core shack exhibitors and geocoding projects...")
    firms, projects = core_shack(['https://www.pdac.ca/convention/exhibits/core-shack/session-a-exhibitors',
                                  'https://www.pdac.ca/convention/exhibits/core-shack/session-b-exhibitors'])
    firms.to_csv(directory + 'firms_cs.csv', 
        index_label='id'
                 )
    firms = firms.merge(ADDRESSES, on='name', how='left')
    firms = gpd.GeoDataFrame(
        firms.apply(lambda x: gc(x, 'add', 'country'), axis=1),
        geometry='geometry'
    )
    print("Writing CS exhibitors to GeoJSON...")
    firms.to_file(directory + 'firms_ts.geojson',
                  driver='GeoJSON',
                  index_label='id'
                  )
    projects = gpd.GeoDataFrame(
        projects.apply(lambda x: gc(x, 'loc', 'country'), axis=1),
        geometry='geometry'
        )
    print("Writing Core Shack projects to GeoJSON...")
    projects.to_file(directory + 'firms_by_projects.geojson', 
        driver='GeoJSON', 
        index_label='id'
        )


if __name__ == '__main__':
#    run_ix(DIR)
#    run_ts(DIR)
   run_cs(DIR)
   print("Done.")
