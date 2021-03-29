import re
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


# TODO: refactor this entire code (Ernest)

def retrieve_fomc_calendar() -> pd.DataFrame:
    """
    Retrieves FOMC calendar from 2006 to now.

    :return: DataFrame representing FOMC calendar.
    """
    print('\n==========Collecting fomc calendar data==========')

    BASE_URL = 'https://www.federalreserve.gov'
    CALENDAR_URL = f'{BASE_URL}/monetarypolicy/fomccalendars.htm'

    START_YEAR = 2006

    date_list = []

    #### Retrieve FOMC Meeting date from 2015 to 2020 ####
    response = requests.get(CALENDAR_URL)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    contents = html_soup.find_all('div', {"class": "panel panel-default"})

    for content in contents:
        m_year = content.find('h4').get_text()[:4]
        m_months = content.find_all('div', {"class": "fomc-meeting__month"})
        m_dates = content.find_all('div', {"class": "fomc-meeting__date"})
        print(f'YEAR: {m_year} - {len(m_dates)} meetings found.')

        for (m_month, m_date) in zip(m_months, m_dates):
            month_name = m_month.get_text().strip()
            date_text = m_date.get_text().strip()
            is_forecast = False
            is_unscheduled = False
            is_month_short = False

            if "cancelled" in date_text:
                continue
            elif "notation vote" in date_text:
                date_text = date_text.replace("(notation vote)", "").strip()
            elif "unscheduled" in date_text:
                date_text = date_text.replace("(unscheduled)", "").strip()
                is_unscheduled = True

            if "*" in date_text:
                date_text = date_text.replace("*", "").strip()
                is_forecast = True

            if "/" in month_name:
                month_name = re.findall(r".+/(.+)$", month_name)[0]
                is_month_short = True

            if "-" in date_text:
                date_text = re.findall(r".+-(.+)$", date_text)[0]

            meeting_date_str = m_year + "-" + month_name + "-" + date_text
            if is_month_short:
                meeting_date = datetime.strptime(meeting_date_str, '%Y-%b-%d')
            else:
                meeting_date = datetime.strptime(meeting_date_str, '%Y-%B-%d')

            date_list.append({"date": meeting_date, "unscheduled": is_unscheduled, "forecast": is_forecast, "confcall": False})

    ##### Retrieve FOMC Meeting date from 2006 to 2015 ####
    for year in range(START_YEAR, 2015):
        hist_url = f'{BASE_URL}/monetarypolicy/fomchistorical{str(year)}.htm'
        response = requests.get(hist_url)
        html_soup = BeautifulSoup(response.text, 'html.parser')

        if year in [2011, 2012, 2013, 2014]:
            panel_headings = html_soup.find_all('h5', {"class": "panel-heading"})
        else:
            panel_headings = html_soup.find_all('div', {"class": "panel-heading"})

        print(f'YEAR: {year} - {len(panel_headings)} meetings found.')

        for panel_heading in panel_headings:
            date_text = panel_heading.get_text().strip()
            regex = r"(January|February|March|April|May|June|July|August|September|October|November|December).*\s(\d*-)*(\d+)\s+(Meeting|Conference Calls?|\(unscheduled\))\s-\s(\d+)"
            date_text_ext = re.findall(regex, date_text)[0]
            meeting_date_str = date_text_ext[4] + "-" + date_text_ext[0] + "-" + date_text_ext[2]
            if meeting_date_str == '1992-June-1':
                meeting_date_str = '1992-July-1'
            elif meeting_date_str == '1995-January-1':
                meeting_date_str = '1995-February-1'
            elif meeting_date_str == '1998-June-1':
                meeting_date_str = '1998-July-1'
            elif meeting_date_str == '2012-July-1':
                meeting_date_str = '2012-August-1'
            elif meeting_date_str == '2013-April-1':
                meeting_date_str = '2013-May-1'

            meeting_date = datetime.strptime(meeting_date_str, '%Y-%B-%d')
            is_confcall = "Conference Call" in date_text_ext[3]
            is_unscheduled = "unscheduled" in date_text_ext[3]

            date_list.append({
                'date': meeting_date,
                'unscheduled': is_unscheduled,
                'forecast': False,
                'confcall': is_confcall
            })

    df = pd.DataFrame(date_list).sort_values(by=['date'])
    df.reset_index(drop=True, inplace=True)

    print("==========Done==========\n")

    return df

# df = retrieve_fomc_calendar()
# df.to_csv('data/textual/fomc_calendar.txt', sep=',', index=False)
