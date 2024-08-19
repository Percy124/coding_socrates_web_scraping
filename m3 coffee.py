#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 11:44:38 2024

@author: percychui
"""

import requests
from bs4 import BeautifulSoup
#%%
def extract_product_details(url): # this table extract most infomration of the product
    
    response = requests.get("https://m3coffee.hk" + url)
    response.raise_for_status() 
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    details_div = soup.find('div', class_='product-single__box__text rte')
    if details_div:
        details_list = details_div.find('ul').find_all('li')
        product_info = {}
        for item in details_list:
            parts = item.text.strip().split(':', 1) 
            if len(parts) == 2:
                key, value = parts[0].strip(), parts[1].strip()
                product_info[key] = value
        return product_info
    else:
        return {}
#%%
all_links = [] # this link save all the url link of the products

for page_number in range(1, 7):
    url = f"https://m3coffee.hk/en/collections/coffeebeans?page={page_number}"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    product_links = soup.find_all('a', {'product-card-link': True})
    
    for link in product_links:
        href = link.get('href')
        all_links.append(href)

all_links = list(set(all_links)) 


#%%
all_product_details = [] # a list of dictionary that save all the product detail 
for link in all_links:
    details = extract_product_details(link)
    all_product_details.append(details)
        
last_dict_keys = list(all_product_details[-1].keys())

for product_dict in all_product_details:
    for key in last_dict_keys:
        if key not in product_dict:
            product_dict[key] = ''
for i, link in enumerate(all_links): # start scraping the remaining information of product
    full_url = "https://m3coffee.hk" + link
    response = requests.get(full_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    price_span = soup.find('span', class_='price__number')
    if price_span:
        price = price_span.text.strip().replace('HK$', '')
        all_product_details[i]['Price'] = price  
    else:
        all_product_details[i]['Price'] = '' 
    title_tag = soup.find('h1', class_='product-single__title')
    if title_tag:
        product_name = title_tag.text.strip()
        all_product_details[i]['Name'] = product_name 
    else:
        all_product_details[i]['Name'] = '' 
    image_meta_tags = soup.find_all('meta', property='og:image:secure_url')
    if image_meta_tags:
        image_url = image_meta_tags[0]['content'] 
        all_product_details[i]['image_url'] = image_url
    else:
        all_product_details[i]['image_url'] = '' 
for i, link in enumerate(all_links):
    all_product_details[i]['SourceURL'] = "https://m3coffee.hk" + link
    all_product_details[i]['Source_Type'] = 'M3'
# start adding the empty element that m3 website doesn't have but coffee carrol website does have
keys_to_add = [
    'Flavors_Spicy', 'Flavors_Choclaty', 'Flavors_Nutty', 'Flavors_Buttery',
    'Flavors_Fruity', 'Flavors_Flowery', 'Flavors_Winey', 'Flavors_Earthy',
    'Attributes _Brightness', 'Attributes_Body', 'Attributes_Aroma', 
    'Attributes_Complexity', 'Attributes_Balance', 'Attributes _Sweetness',
    'Comments'
]
for product_dict in all_product_details:
    for key in keys_to_add:
        product_dict[key] = ''

#%%
# start data cleansing
keys_to_remove = ['Baking place', 'Roasted date', 'Best before date', 'Material', 'Farm']
for product_dict in all_product_details:
    for key in keys_to_remove:
        if key in product_dict:
            del product_dict[key]
all_product_details_tmp = all_product_details.copy()
# all_product_details = all_product_details_tmp.copy()
for product in all_product_details:
    if isinstance(product['Weight'], str): 
        weights = product['Weight'].replace('g', '').split('/')  
    product['Weight'] = float(weights[0]) if weights[0] else -1.0 
    if isinstance(product['Price'], str): 
        product['Price'] = float(product['Price'].replace(',', '')) if product else -1.0
    if 'Altitude' in product:
        product['Altitude in meters'] = product.pop('Altitude')
    if isinstance(product['Altitude in meters'], str):
        altitude_str = product['Altitude in meters'].replace('m', '').replace(',', '')
    if '-' in altitude_str:
        altitude = float(altitude_str.split('-')[0])  
    else:
        altitude = float(altitude_str) if altitude_str else -1.0 
        product['Altitude in meters'] = altitude 
filtered_product_details = []
for product in all_product_details:
    if product['Taste']:
        product['Taste'] = [flavor.strip() for flavor in product['Taste'].split(',')]
        filtered_product_details.append(product)
all_product_details = filtered_product_details

for product in all_product_details:
    for key in [
        'Flavors_Spicy', 'Flavors_Choclaty', 'Flavors_Nutty', 'Flavors_Buttery',
        'Flavors_Fruity', 'Flavors_Flowery', 'Flavors_Winey', 'Flavors_Earthy',
        'Attributes _Brightness', 'Attributes_Body', 'Attributes_Aroma',
        'Attributes_Complexity', 'Attributes_Balance', 'Attributes _Sweetness',
        'Comments'
    ]:
        product[key] = -1
    if product['Weight'] != 0: 
        product['Price / 100g in HKD'] = round(product['Price'] / product['Weight'] * 100, 2)
    else:
        product['Price / 100g in HKD'] = -1  
    del product['Weight']
    del product['Price']
print(all_product_details)
#%%
# save all the data into mongodb
from pymongo import MongoClient

client = MongoClient('mongodb+srv://admin:0000@cluster0.xfwvw.mongodb.net/')
db = client['coffee']
collection = db['coffee_source_m3']
for product in all_product_details:
    collection.insert_one(product)
client.close()








