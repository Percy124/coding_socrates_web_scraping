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
        if altitude_str.split('-')[0] != '---' and altitude_str.split('-')[0] != '' :
            altitude = float(altitude_str.split('-')[0]) 
        else:
            altitude = -1  
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
for product in all_product_details:
    product['Altitude in meters'] = -1 
for product in all_product_details:
    if 'Source_Type' in product:
        product['source_type'] = product.pop('Source_Type')
    if 'SourceURL' in product:
        product['sourceurl'] = product.pop('SourceURL')
    if 'Name' in product:
        product['name'] = product.pop('Name')
for i in range(len(all_product_details)):
    all_product_details[i]['Comments'] = ''
    all_product_details[i]['avg_rating from customer'] = -1
print(all_product_details)
#%%
from pymongo import MongoClient # save all the data into mongodb

client = MongoClient('mongodb+srv://admin:0000@cluster0.xfwvw.mongodb.net/')
db = client['coffee']
collection = db['coffee_source_m3']

# collection.delete_many({}) 

for product in all_product_details:
    collection.insert_one(product)

client.close()
#%%
import pandas as pd
import matplotlib.pyplot as plt
client = MongoClient('mongodb+srv://admin:0000@cluster0.xfwvw.mongodb.net/')
db = client['coffee']
collection = db['coffee_data_engineering_carrol']

# 1. Histogram of Top 10 Countries

pipeline_country = [
    {"$group": {"_id": "$Country", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 11}
]
top_countries = list(collection.aggregate(pipeline_country))
df_countries = pd.DataFrame(top_countries).rename(columns={"_id": "Country"})
df_countries = df_countries[df_countries['Country'].notna()]
df_countries.reset_index(drop=True, inplace=True)
plt.figure(figsize=(10, 6))
plt.bar(df_countries['Country'], df_countries['count'])
plt.xlabel("Country")
plt.ylabel("Number of Coffees")
plt.title("Top 10 Countries by Coffee Count")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("histogram_top_countries.png")
plt.close()
client.close()
#%%
# 2. Price Distribution by Region

client = MongoClient('mongodb+srv://admin:0000@cluster0.xfwvw.mongodb.net/')
db = client['coffee']
collection = db['coffee_data_engineering_carrol']
distinct_regions = collection.distinct("Region")
pipeline_top_regions = [
    {"$group": {"_id": "$Region", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 8}
]
top_regions = [doc["_id"] for doc in collection.aggregate(pipeline_top_regions)]
distinct_regions = top_regions[2:] 
num_regions = len(distinct_regions)
num_cols = 3  
num_rows = -(-num_regions // num_cols) 

fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows))
axes = axes.ravel() 

for i, region in enumerate(distinct_regions):
    pipeline_region = [
        {"$match": {"Region": region}},
        {"$project": {"_id": 0, "Price / 100g in HKD": 1}}
    ]
    prices_region = list(collection.aggregate(pipeline_region))
    df_prices = pd.DataFrame(prices_region)
    axes[i].hist(df_prices["Price / 100g in HKD"], bins=10)
    axes[i].set_title(f"Price Distribution in {region}")
    axes[i].set_xlabel("Price / 100g in HKD")
    axes[i].set_ylabel("Frequency")

for j in range(num_regions, num_rows * num_cols):
    axes[j].axis('off')

plt.tight_layout()
plt.savefig("price_distribution_by_region.png")
plt.close()

client.close()

























