import re
from datetime import datetime

import pandas as pd
import requests
import textract
from bs4 import BeautifulSoup

#### NOTE #####
# Press Conference Transcripts are in pdf. Need to download pdf before extracting text.

# TODO: Fix the following transcript issues?:
# NOTE: Following transcripts have issue retrieving text from pdf:
# 1. https://www.federalreserve.gov/monetarypolicy/files/FOMC20151028meeting.pdf
# 2. https://www.federalreserve.gov/monetarypolicy/files/FOMC20150318meeting.pdf

BASE_URL = 'https://www.federalreserve.gov'
STATEMENT_URL = 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'


def retrieve_fomc_press_conf() -> pd.DataFrame:
    """
        Retrieves FOMC press conference transcripts from 2006 to now.

        :return: DataFrame representing FOMC press conference transcripts
    """
    print('\n==========Collecting fomc press conference data==========')

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

    def combine_paragraphs(paragraphs: list) -> str:
        """
        Combines paragraphs of text extracted from pdf into a single chunk of text.

        :param paragraphs: List of paragraphs in press conference pdf text
        :return: String of the combined text
        """
        section = -1
        paragraph_sections = []
        for paragraph in paragraphs:
            if not re.search(
                    '^(page|january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',
                    paragraph.lower()):
                if len(re.findall(r'[A-Z]', paragraph[:10])) > 5 and not re.search(
                        '(present|frb/us|abs cdo|libor|rp–ioer|lsaps|cusip|nairu|s cpi|clos, r)',
                        paragraph[:10].lower()):
                    section += 1
                    paragraph_sections.append("")
                if section >= 0:
                    paragraph_sections[section] += paragraph

        combined_script = ''.join(paragraph_sections)
        return combined_script

    def parse_text_from_pdf(file_path: str) -> str:
        """
        Parses text from pdf given file path of downloaded pdf.

        :param file_path: String of file path
        :return: String of entire text
        """
        pdf_file_parsed = textract.process(file_path).decode('utf-8')
        paragraphs = re.sub('(\n)(\n)+', '\n', pdf_file_parsed.strip())
        paragraphs = paragraphs.split('\n')
        full_script = combine_paragraphs(paragraphs)

        return full_script

    def parse_contents(df: pd.DataFrame, contents: list) -> pd.DataFrame:
        """
        Downloads pdf from press conference url and extracts text.

        :param df: DataFrame of press conference transcripts
        :param contents: List of conference urls enclosed by <a> tags
        :return: DataFrame of press conference transcripts
        """
        for content in contents:
            full_conf_link = BASE_URL + content.attrs['href']
            date = pd.to_datetime(re.findall('[0-9]{8}', full_conf_link)[0])
            speaker = get_speaker(date)

            # Download pdf from url & extract text from pdf
            pdf_filepath = 'data/pressConfPdfs/PresConf_' + str(date.date()) + '.pdf'
            res = requests.get(full_conf_link)
            with open(pdf_filepath, 'wb') as f:
                f.write(res.content)

            try:
                full_script = parse_text_from_pdf(pdf_filepath)
                title = 'Press Conference Transcripts'
                df.loc[len(df)] = [date, speaker, full_conf_link, full_script, title]

            except Exception as e:
                print(e)
                continue
        return df

    #### Retrieve fomc Press Conference Transcripts from 2016 to 2021 ####
    print('Retrieving transcripts from 2016 - 2021...')
    r = requests.get(STATEMENT_URL)
    soup = BeautifulSoup(r.text, 'html.parser')
    presconfs = soup.find_all('a', href=re.compile('^/monetarypolicy/fomcpresconf\d{8}.htm'))
    df = pd.DataFrame(columns=['date', 'speaker', 'link', 'text', 'title'])

    # Get pdf url from press conference url
    counter = 0
    for presconf in presconfs:
        counter += 1
        print(f"Collecting post #{counter}/{len(presconfs)}...")
        link = presconf.attrs['href']
        full_link = BASE_URL + link
        response = requests.get(full_link)
        soup_presconf = BeautifulSoup(response.text, 'html.parser')
        contents = soup_presconf.find_all('a', href=re.compile('^/mediacenter/files/FOMCpresconf\d{8}.pdf'))
        df = parse_contents(df, contents)

    #### Retrieve fomc Press Conference Transcripts from 2006 to 2015 ####
    print('Retrieving transcripts from 2006 - 2015...')
    for year in range(2006, 2016):
        print(f'Collecting post for {year}...')
        yearly_url = BASE_URL + '/monetarypolicy/fomchistorical' + str(year) + '.htm'
        r_year = requests.get(yearly_url)
        soup_yearly = BeautifulSoup(r_year.text, 'html.parser')
        contents = soup_yearly.find_all('a', href=re.compile('^/monetarypolicy/files/FOMC\d{8}meeting.pdf'))
        df = parse_contents(df, contents)

    df = df.set_index('date').sort_index(ascending=True).reset_index()

    print("==========Done==========\n")

    return df

# if __name__ == '__main__':
#     df = retrieve_fomc_press_conf()
#     df.to_csv('data/textual/fomc_press_conf.txt', sep=',', index=False, )
