import json

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = 'https://www.federalreserve.gov'
TESTIMONY_URL = BASE_URL + '/json/ne-testimony.json'

response = requests.get(TESTIMONY_URL)
decoded = response.content.decode('utf-8-sig')
records = json.loads(decoded)

all_data = []
counter, len_records = 0, len(records)

print("Launching webdriver...")
# driver = webdriver.Chrome('chromedriver')
driver = webdriver.Chrome(ChromeDriverManager(version="89.0.4389.23").install())

print("Collecting data...")
for record in records:
    counter += 1
    print(f"Collecting post #{counter}/{len_records}...")
    try:
        link = record.get('l')

        if link:
            post_url = BASE_URL + link
            driver.get(post_url)
            inner_html = driver.page_source
            inner_soup = BeautifulSoup(inner_html, 'html.parser')

            # TODO: fix the text
            text = inner_soup.find('div', class_='col-xs-12 col-sm-8 col-md-8').text.strip()

            all_data.append({
                'date': pd.to_datetime(record.get('d').split(' ')[0]),
                'speaker': record.get('s'),
                'title': record.get('t'),
                'location': record.get('lo'),
                'link': post_url,
                'text': text
            })

    except Exception as e:
        print(e)
        continue

print("\nCollection completed!")
driver.close()

df = pd.DataFrame(all_data).drop_duplicates().sort_values('date').reset_index(drop=True)
df.to_csv('data/textual/fomc_testimony.txt', sep=',', index=False)
