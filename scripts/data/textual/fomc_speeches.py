import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver

BASE_URL = 'https://www.federalreserve.gov'

START_YEAR, END_YEAR = 2006, 2021

all_data = []
counter = 0

print("Launching webdriver...")
driver = webdriver.Chrome('chromedriver')

print("Collecting data...")
for year in range(START_YEAR, END_YEAR + 1):
    if year >= 2011:
        speech_url = f'{BASE_URL}/newsevents/speech/{year}-speeches.htm'
    else:
        speech_url = f'{BASE_URL}/newsevents/speech/{year}speech.htm'

    driver.get(speech_url)

    print(f"\nCollecting from Year {year}...")
    inner_html = driver.page_source
    soup = BeautifulSoup(inner_html, 'html.parser')
    posts = soup.find('div', class_='row eventlist').find_all('div', class_='row')

    for post in posts:
        try:
            counter += 1
            print(f"Collecting post #{counter}...")
            date = pd.to_datetime(post.find('time').text)

            title = post.find('a').text
            link = post.find('a').get('href')
            speaker = post.find('p', class_='news__speaker').text
            location = post.find_all('p')[-2].text

            # retrieving text from link
            post_url = BASE_URL + link
            driver.get(post_url)
            inner_html = driver.page_source
            inner_soup = BeautifulSoup(inner_html, 'html.parser')

            # TODO: fix the text
            paragraphs = inner_soup.find('div', class_='col-xs-12 col-sm-8 col-md-8').find_all('p')
            text = ''
            for paragraph in paragraphs:
                if not paragraph.find('a'):
                    text += paragraph.text.strip()

            all_data.append({
                'date': date,
                'speaker': speaker,
                'title': title,
                'location': location,
                'link': post_url,
                'text': text
            })

        except Exception as e:
            print(e)
            continue

print("\nCollection completed!")
driver.close()

df = pd.DataFrame(all_data).drop_duplicates().sort_values('date').reset_index(drop=True)

# TODO: figure out a way to write to csv with the newline characters
df.to_csv('data/textual/fomc_speeches.csv', index=False)
