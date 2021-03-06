import re
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

BASE_URL = 'https://www.federalreserve.gov'

CALENDAR_URL = f'{BASE_URL}/monetarypolicy/fomccalendars.htm'

CHAIR_DICT = {
    ('1987-08-11', '2006-01-31'): 'Alan Greenspan',
    ('2006-02-01', '2014-01-31'): 'Ben Bernanke',
    ('2014-02-03', '2018-02-03'): 'Janet Yellen',
    ('2018-02-05', '2022-02-05'): 'Jerome Powell',
}


def retrieve_speaker_from_date(date: datetime) -> str:
    """
    Retrieve speaker using date.

    :param date: Datetime representing the date of the article
    :return: String representing the Speaker
    """
    speaker = ''

    for (start_date, end_date), chair in CHAIR_DICT.items():
        start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
        if start_date < date < end_date:
            speaker = chair

    return speaker


#### Retrieve minutes from 2014 to 2021 ####
print("Launching webdriver...")
driver = webdriver.Chrome('chromedriver')

print("Collecting data...")
driver.get(CALENDAR_URL)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

all_data = []
counter = 0

contents = soup.find_all('a', href=re.compile('^/monetarypolicy/fomcminutes\d{8}.htm'))

for content in contents:
    try:
        counter += 1
        print(f"Collecting post #{counter}...")

        link = content.get('href')
        date = pd.to_datetime(re.findall('[0-9]{8}', link)[0])
        speaker = retrieve_speaker_from_date(date)

        driver.get(BASE_URL + link)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        article = soup.find('div', class_='col-xs-12 col-sm-8 col-md-9')
        title = article.find('h3')

        # TODO: fix the text
        paragraphs = article.find_all('p')
        text = ''
        for paragraph in paragraphs:
            text += paragraph.text.strip()

        all_data.append({
            'date': date,
            'speaker': speaker,
            'title': title,
            'link': f'{BASE_URL}{link}',
            'text': text.strip()
        })

    except Exception as e:
        print(e)
        continue

#### Retrieve minutes from 2006 to 2014 ####
for year in range(2006, 2014):
    try:
        minutes_url = f'{BASE_URL}/monetarypolicy/fomchistorical{year}.htm'
        driver.get(minutes_url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        contents = soup.find_all('a', href=re.compile('(^/monetarypolicy/fomcminutes|^/fomc/minutes|^/fomc/MINUTES)'))

        for content in contents:
            counter += 1
            print(f"Collecting post #{counter}...")

            link = content.get('href')
            date = pd.to_datetime(re.findall('[0-9]{8}', link)[0])
            speaker = retrieve_speaker_from_date(date)

            if date == datetime(1996, 1, 30):
                date = datetime(1996, 1, 31)
            elif date == datetime(1996, 7, 2):
                date = datetime(1996, 7, 3)
            elif date == datetime(1997, 2, 4):
                date = datetime(1997, 2, 5)
            elif date == datetime(1997, 7, 1):
                date = datetime(1997, 7, 2)
            elif date == datetime(1998, 2, 3):
                date = datetime(1998, 2, 4)
            elif date == datetime(1998, 6, 30):
                date = datetime(1998, 7, 1)
            elif date == datetime(1999, 2, 2):
                date = datetime(1999, 2, 3)
            elif date == datetime(1999, 6, 29):
                date = datetime(1999, 6, 30)

            driver.get(BASE_URL + link)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            article = soup.find('div', class_='col-xs-12 col-sm-8 col-md-9')
            title = article.find('h3')

            # TODO: fix the text
            paragraphs = soup.find_all('p')
            text = ''
            for paragraph in paragraphs:
                text += paragraph.text.strip()

            all_data.append({
                'date': date,
                'speaker': speaker,
                'title': title,
                'link': f'{BASE_URL}{link}',
                'text': text
            })

    except Exception as e:
        print(e)
        continue

print("\nCollection completed!")
driver.close()

df = pd.DataFrame(all_data).drop_duplicates().sort_values('date').reset_index(drop=True)

# TODO: figure out a way to write to csv with the newline characters
df.to_csv('data/textual/fomc_minutes.csv', index=False)
