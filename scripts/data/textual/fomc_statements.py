import re
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


# TODO: Refactor this Jolene

def retrieve_fomc_statements() -> pd.DataFrame:
    """
    Retrieves FOMC statements from 2006 to now.

    :return: DataFrame representing FOMC statements
    """
    print('\n==========Collecting fomc statements data==========')

    BASE_URL = 'https://www.federalreserve.gov'
    STATEMENT_URL = 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'

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
            if start_date <= date <= end_date:
                speaker = chair

        return speaker

    counter = 0

    #### Retrieve FOMC statements from 2016 to 2021 ####
    response = requests.get(STATEMENT_URL)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    contents = html_soup.find_all('a', href=re.compile('^/newsevents/pressreleases/monetary\d{8}[ax].htm'))
    df = pd.DataFrame(columns=['Date', 'Speaker', 'Title', 'Link', 'Text'])

    for content in contents:
        counter += 1
        print(f"Collecting post #{counter}...")
        link = content.attrs['href']
        date = pd.to_datetime(re.findall('[0-9]{8}', link)[0])
        speaker = get_speaker(date)

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
        contents = inner_soup.findAll('a', text='Statement')

        for content in contents:
            counter += 1
            print(f"Collecting post #{counter}...")
            link = content.attrs['href']
            date = pd.to_datetime(re.findall('[0-9]{8}', link)[0])
            speaker = get_speaker(date)

            full_link = BASE_URL + link
            inner_soup = BeautifulSoup(requests.get(full_link).text, 'html.parser')
            details = inner_soup.find('div', id='article')
            title = details.find('h3', class_='title').text
            statement = details.find('div', class_='col-xs-12 col-sm-8 col-md-8').text.strip().replace('\n', ' ')

            df.loc[len(df)] = [date, speaker, title, full_link, statement]

    df.columns = df.columns.str.lower()
    df = df.drop_duplicates().sort_values('date').reset_index(drop=True)

    print("==========Done==========\n")

    return df


# if __name__ == '__main__':
#     df = retrieve_fomc_statements()
#     df.to_csv('data/textual/fomc_statements.txt', sep=',', index=False)
