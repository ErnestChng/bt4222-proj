import os
import re
from datetime import datetime

import pandas as pd
import requests
import textract
from bs4 import BeautifulSoup

#### NOTE #####
# Press Conference Transcripts are in pdf. Need to download pdf before extracting text. Texts are saved to .txt
# Section 1 and 2 to run separately bc Section 2 takes a while due to extremely long historical transcripts.
# 2016-2021 info saved to fomc_pressConf.csv, 2006-2015 info saved to fomc_pressConf1.csv for now.

# TODO: Fix the following transcript issues?:
# NOTE: Following transcripts have issue retrieving text from pdf so .txt version not available:
# 1. https://www.federalreserve.gov/monetarypolicy/files/FOMC20151028meeting.pdf
# 2. https://www.federalreserve.gov/monetarypolicy/files/FOMC20150318meeting.pdf

base_dir = '/Users/jolene/Downloads/1.BT4222/Group Project/bt4222-proj'
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


def combine_paragraphs(paragraphs):
    section = -1
    paragraph_sections = []
    print('Combining paragraphs...')
    for paragraph in paragraphs:
        if not re.search('^(page|january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',
                paragraph.lower()):
            if len(re.findall(r'[A-Z]', paragraph[:10])) > 5 and not re.search('(present|frb/us|abs cdo|libor|rp–ioer|lsaps|cusip|nairu|s cpi|clos, r)',
                    paragraph[:10].lower()):
                section += 1
                paragraph_sections.append("")
            if section >= 0:
                paragraph_sections[section] += paragraph

    full_script = ''.join(paragraph_sections)
    return full_script


#### Section 1: Retrieve FOMC Press Conference Transcripts from 2016 to 2021 ####
r = requests.get(STATEMENT_URL)
soup = BeautifulSoup(r.text, 'html.parser')
presconfs = soup.find_all('a', href=re.compile('^/monetarypolicy/fomcpresconf\d{8}.htm'))

df = pd.DataFrame(columns=['Date', 'Speaker', 'Title', 'Link', 'Text'])

for presconf in presconfs:
    link = presconf.attrs['href']
    full_link = BASE_URL + link
    response = requests.get(full_link)
    soup_presconf = BeautifulSoup(response.text, 'html.parser')
    contents = soup_presconf.find_all('a', href=re.compile('^/mediacenter/files/FOMCpresconf\d{8}.pdf'))

    for content in contents:
        conf_link = content.attrs['href']
        full_conf_link = BASE_URL + conf_link

        date = pd.to_datetime(re.findall('[0-9]{8}', link)[0])
        speaker = retrieve_speaker_from_date(date)
        title = 'FOMC Press Conference Transcript'
        df.loc[len(df)] = [date, speaker, title, full_conf_link, ""]

for i in range(len(df)):
    link_url = df.loc[i, 'Link']
    date = pd.to_datetime(re.findall('[0-9]{8}', link_url)[0])
    pdf_filepath = base_dir + '/data/pressConfPdfs/PresConf_' + str(date.date()) + '.pdf'

    # Scripts are provided only in pdf. Save the pdf and pass the content
    res = requests.get(link_url)
    with open(pdf_filepath, 'wb') as f:
        f.write(res.content)

    pdf_file_parsed = textract.process(pdf_filepath).decode('utf-8')
    paragraphs = re.sub('(\n)(\n)+', '\n', pdf_file_parsed.strip())
    paragraphs = paragraphs.split('\n')
    full_script = combine_paragraphs(paragraphs)

    file_name = 'PresConf_' + str(date.date()) + '.txt'
    df.loc[i, 'Text'] = file_name

    # Write to text file
    file_path = base_dir + '/data/pressConfTexts/' + file_name
    file1 = open(file_path, 'w')
    file1.write(full_script)
    file1.close()

df.to_csv(os.path.join(base_dir, './data/macro/fomc_pressConf.csv'))

#### Section 2: Retrieve minutes from 2006 to 2015 ####
df = pd.DataFrame(columns=['Date', 'Speaker', 'Title', 'Link', 'Text'])

for year in range(2006, 2016):
    fomc_yearly_url = BASE_URL + '/monetarypolicy/fomchistorical' + str(year) + '.htm'
    r_year = requests.get(fomc_yearly_url)
    soup_yearly = BeautifulSoup(r_year.text, 'html.parser')
    presconf_hists = soup_yearly.find_all('a', href=re.compile('^/monetarypolicy/files/FOMC\d{8}meeting.pdf'))
    index = 1

    for presconf_hist in presconf_hists:
        presconf_hist_url = BASE_URL + presconf_hist.attrs['href']
        date = pd.to_datetime(re.findall('[0-9]{8}', presconf_hist_url)[0])
        speaker = retrieve_speaker_from_date(date)
        title = 'FOMC Press Conference Transcript'

        pdf_filepath = base_dir + '/data/pressConfPdfs/PresConf_' + str(date.date()) + '.pdf'
        file_name = 'PresConf_' + str(date.date()) + '.txt'
        df.loc[len(df)] = [date, speaker, title, presconf_hist_url, file_name]

        # save pdf
        res = requests.get(presconf_hist_url)
        with open(pdf_filepath, 'wb') as f:
            f.write(res.content)

        try:
            pdf_file_parsed = textract.process(pdf_filepath).decode('utf-8')
            paragraphs = re.sub('(\n)(\n)+', '\n', pdf_file_parsed.strip())
            paragraphs = paragraphs.split('\n')
            full_script = combine_paragraphs(paragraphs)

            # Write to text file
            file_path = base_dir + '/data/pressConfTexts/' + file_name
            file1 = open(file_path, 'w')
            file1.write(full_script)
            file1.close()

        except Exception as e:
            print(e)
            continue

df = df.set_index('Date').sort_index(ascending=False)
df.to_csv(os.path.join(base_dir, './data/textual/fomc_pressConf1.csv'))
