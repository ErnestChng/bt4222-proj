import re
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def retrieve_fomc_minutes() -> pd.DataFrame:
    print('\nCollecting fomc minutes data...')

    BASE_URL = 'https://www.federalreserve.gov'
    CALENDAR_URL = f'{BASE_URL}/monetarypolicy/fomccalendars.htm'

    def get_speaker(date: datetime) -> str:
        """
        Retrieve speaker using date. If date is not within CHAIR_DICT, then speaker will be an empty string.

        :param date: Datetime representing the date of the article
        :return: String representing the Speaker
        """
        speaker = ''

        CHAIR_DICT = {
            ('1987-08-11', '2006-01-31'): 'Alan Greenspan',
            ('2006-02-01', '2014-01-31'): 'Ben Bernanke',
            ('2014-02-03', '2018-02-03'): 'Janet Yellen',
            ('2018-02-05', '2022-02-05'): 'Jerome Powell',
        }

        for (start_date, end_date), chair in CHAIR_DICT.items():
            start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
            if start_date < date <= end_date:
                speaker = chair

        return speaker

    #### Retrieve minutes from 2016 to 2021 ####
    print("Launching webdriver...")
    # driver = webdriver.Chrome('chromedriver')
    driver = webdriver.Chrome(ChromeDriverManager(version="89.0.4389.23").install())

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
            speaker = get_speaker(date)

            driver.get(BASE_URL + link)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            article = soup.find('div', class_='col-xs-12 col-sm-8 col-md-9')

            paragraphs = article.find_all('p')
            text = ''
            for paragraph in paragraphs:
                text += paragraph.text.strip()

            all_data.append({
                'date': date,
                'speaker': speaker,
                'link': f'{BASE_URL}{link}',
                'text': text.strip()
            })

        except Exception as e:
            print(e)
            continue

    #### Retrieve minutes from 2006 to 2016 ####
    for year in range(2006, 2015):
        try:
            minutes_url = f'{BASE_URL}/monetarypolicy/fomchistorical{year}.htm'
            print(minutes_url)
            driver.get(minutes_url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            contents = soup.find_all('a', href=re.compile('(^/monetarypolicy/fomcminutes|^/01_data.py/minutes|^/01_data.py/MINUTES)'))

            for content in contents:
                try:
                    counter += 1
                    print(f"Collecting post #{counter}...")

                    link = content.get('href')
                    date = pd.to_datetime(re.findall('[0-9]{8}', link)[0])
                    speaker = get_speaker(date)

                    driver.get(BASE_URL + link)
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')

                    paragraphs = soup.find_all('p')
                    text = ''
                    for paragraph in paragraphs:
                        text += paragraph.text.strip()

                    all_data.append({
                        'date': date,
                        'speaker': speaker,
                        'link': f'{BASE_URL}{link}',
                        'text': text
                    })

                except Exception as e:
                    print(e)
                    continue

        except Exception as e:
            print(e)
            continue

    print("\nCollection completed!")
    driver.close()

    df = pd.DataFrame(all_data).drop_duplicates().sort_values('date').reset_index(drop=True)
    df['title'] = 'Minutes of the Federal Open Market Committee'

    return df


# df = retrieve_fomc_minutes()
# df.to_csv('data/textual/fomc_minutes.txt', sep=',', index=False)
