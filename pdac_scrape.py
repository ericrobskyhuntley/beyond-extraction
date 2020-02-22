# -*- coding: utf-8 -*-
"""
Scrape PDAC site for vendor and prospector information.
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-d', '--directory', help = 'Directory in which to write data.')
args = parser.parse_args()

if args.directory:
    DIR = args.directory
else: 
    print('Please supply directory in which to write data.')
    exit()

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
            proj_loc = proj_elem.next_sibling.strip()
            country_code = 
            booth = i.find('div', class_='sfitemBoothNumbers')
            if booth:
                booth = booth.get_text().strip()
            website = i.find('div', class_='sfitemRichText')
            if website:
                website = website.find('a').get('href').strip()
            firm = pd.Series({
                    'name': name,
                    'proj': proj,
                    'proj_loc': proj_loc,
                    'country_code': ,
                    'booth': booth.replace('corpmember, ', ''),
                    'website': website,
                    })
            df = df.append(firm, ignore_index=True)
    return(df)
    
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
    df = pd.DataFrame()
    for l in links:
        country_soup = BeautifulSoup(requests.get(l['link']).content, 'html.parser')
        items = country_soup.find_all('div', class_='sfitem')
        for i in items:
            name = i.find('p', class_='sfitemTitle')
            if name:
                name = name.get_text()
            booth = i.find('div', class_='sfitemBoothNumbers')
            if booth:
                booth = booth.get_text()
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
            df = df.append(firm, ignore_index=True)
    return(df)
    
def run(directory):
    # INVESTORS EXCHANGE
        
    print("Scraping investors exchange exhibitors alphabetically...")
    ix_by_alpha =  pdac_by_x(url = 'https://www.pdac.ca/convention/exhibits/investors-exchange/exhibitors',
                             thing_id = 'alphaChars', 
                             thing_name = 'alpha',
                             keep_thing = False)
    print("Writing to CSV...")
    ix_by_alpha.to_csv(directory + 'ix_by_alpha.csv', index_label='id')
    
    print("Scraping investors exchange exhibitors by commodity...")
    ix_by_commodity =  pdac_by_x(url = 'https://www.pdac.ca/convention/exhibits/investors-exchange/exhibitor-list-by-commodity',
                                 thing_id = 'commodityTypes', 
                                 thing_name = 'commodity')
    print("Writing to CSV...")
    ix_by_commodity.to_csv(directory + 'ix_by_commodity.csv', index_label='id')
    
    print("Scraping investors exchange exhibitors by country of exploration...")
    ix_by_country = pdac_by_x(url = 'https://www.pdac.ca/convention/exhibits/investors-exchange/exhibitor-list-by-country-of-exploration',
                              thing_id = 'countries', 
                              thing_name = 'country')
    print("Writing to CSV...")
    ix_by_country.to_csv(directory + 'ix_by_country.csv', index_label='id')
    
    # TRADE SHOW
    
    print("Scraping trade show exhibitors alphabetically...")
    ts_by_alpha = pdac_by_x(url = 'https://www.pdac.ca/convention/exhibits/trade-show/exhibitors',
                            thing_id = 'alphaChars',
                            thing_name = 'alpha',
                            keep_thing = False)
    print("Writing to CSV...")
    ts_by_alpha.to_csv(directory + 'ts_by_alpha.csv', index_label='id')
    
    print("Scraping trade show exhibitors by business type...")
    ts_by_biz = pdac_by_x(url = 'https://www.pdac.ca/convention/exhibits/trade-show/exhibitor-list-by-business-type',
                          thing_id = 'businessTypes',
                          thing_name = 'biz_type')
    print("Writing to CSV...")
    ts_by_biz.to_csv(directory + 'ts_by_biz.csv', index_label='id')
    
    
    # CORE SHACK
    
    print("Scraping core shack exhibitors...")
    cs = core_shack(['https://www.pdac.ca/convention/exhibits/core-shack/session-a-exhibitors',
                     'https://www.pdac.ca/convention/exhibits/core-shack/session-b-exhibitors'])
    print("Writing to CSV...")
    cs.to_csv(directory + 'data/core_shack.csv', index_label='id')

if __name__ == '__main__':
    run(DIR)
    print("Done.")