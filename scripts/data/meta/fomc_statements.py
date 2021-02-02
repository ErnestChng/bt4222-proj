import re
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

dir = '/Users/jolene/Downloads/1.BT4222/Group Project/bt4222-proj'
BASE_URL = 'https://www.federalreserve.gov'
STATEMENT_URL = 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'


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
        if start_date <= date <= end_date:
            speaker = chair

    return speaker

#### Retrieve FOMC statements from 2016 to 2021 ####
response = requests.get(STATEMENT_URL)
html_soup = BeautifulSoup(response.text, 'html.parser')
contents = html_soup.find_all('a', href=re.compile('^/newsevents/pressreleases/monetary\d{8}[ax].htm'))
df = pd.DataFrame(columns=['Date', 'Speaker', 'Title', 'Link', 'Text'])

for content in contents:
    link = content.attrs['href']
    date = pd.to_datetime(re.findall('[0-9]{8}', link)[0])
    speaker = retrieve_speaker_from_date(date)

    full_link = BASE_URL + link
    inner_soup = BeautifulSoup(requests.get(full_link).text, 'html.parser')
    details = inner_soup.find('div', id='article')
    title = details.find('h3', class_='title').text
    statement = details.find('div', class_='col-xs-12 col-sm-8 col-md-8').text.strip().replace('\n', ' ')

    df.loc[len(df)] = [date, speaker, title, full_link, statement]



#### Retrieve minutes from 2006 to 2015 ####
for year in range(2006, 2015):
    statement_url = BASE_URL + '/monetarypolicy/fomchistorical' + str(year) + '.htm'
    response = requests.get(statement_url)
    inner_soup = BeautifulSoup(response.text, 'html.parser')
    contents = inner_soup.findAll('a', text = 'Statement')

    for content in contents:
        link = content.attrs['href']
        date = pd.to_datetime(re.findall('[0-9]{8}', link)[0])
        speaker = retrieve_speaker_from_date(date)

        full_link = BASE_URL + link
        inner_soup = BeautifulSoup(requests.get(full_link).text, 'html.parser')
        details = inner_soup.find('div', id='article')
        title = details.find('h3', class_='title').text
        statement = details.find('div', class_='col-xs-12 col-sm-8 col-md-8').text.strip().replace('\n', ' ')

        df.loc[len(df)] = [date, speaker, title, full_link, statement]


df = df.set_index('Date').sort_index(ascending=False)
df.to_csv(os.path.join(dir, './data/meta/fomc_statements.csv'))
