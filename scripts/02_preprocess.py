import datetime as dt
import os
from typing import Optional, Union

import pandas as pd

os.chdir('/Users/ernestchng/PycharmProjects/bt4222-proj')


def preprocess() -> pd.DataFrame:
    minutes = pd.read_csv('data/textual/fomc_minutes.txt', delimiter=',')
    speeches = pd.read_csv('data/textual/fomc_speeches.txt', delimiter=',')
    statements = pd.read_csv('data/textual/fomc_statements.txt', delimiter=',')
    testimony = pd.read_csv('data/textual/fomc_testimony.txt', delimiter=',')
    press_conf = pd.read_csv('data/textual/fomc_press_conf.txt', delimiter=',')

    # TODO: shift this operations into fomc_press_conf (Jolene)
    press_conf.columns = press_conf.columns.str.lower()
    press_conf = press_conf.sort_values('date', ascending=False)
    press_conf.reset_index(drop=True, inplace=True)

    print(f'minutes: {minutes.shape}')
    print(f'speeches: {speeches.shape}')
    print(f'statements: {statements.shape}')
    print(f'testimony: {testimony.shape}')
    print(f'press conference: {press_conf.shape}')

    fomc_calendar = pd.read_csv('data/textual/fomc_calendar.txt', delimiter=',')
    fomc_calendar.set_index('date', inplace=True)
    fomc_calendar.index = pd.to_datetime(fomc_calendar.index)

    def get_next_meeting(curr_date: Union[str, dt.datetime]) -> Optional[dt.datetime]:
        """
        Retrieves next FOMC meeting date using fomc_calendar.txt.

        :param curr_date: Str or Datetime representing current date
        :return: Datetime representing the next meeting date or None
        """
        if type(curr_date) is str:
            try:
                curr_date = dt.datetime.strptime(curr_date, '%Y-%m-%d')
            except ValueError:
                return None

        curr_date = curr_date + dt.timedelta(days=2)
        fomc_calendar.sort_index(ascending=True, inplace=True)

        if fomc_calendar.index[0] > curr_date:
            return None
        else:
            for date in fomc_calendar.index:
                if curr_date < date:
                    return date
            return None

    def process_df(df: pd.DataFrame, doc_type: str):
        """
        Helper function to prepare dataframe for concatenation in the subsequent steps.

        Adds two new columns called 'next_meeting' and 'type'.

        :param df: DataFrame to be processed
        :param doc_type: Str representing the type of FOMC data (i.e. minutes, speeches)
        :return: Processed DataFrame
        """
        df_new = pd.DataFrame({
            'type': doc_type,
            'date': df['date'],
            'speaker': df['speaker'],
            'link': df['link'],
            'text': df['text'],
            'title': df['title'],
            'next_meeting': df['date'].map(get_next_meeting),
        })

        print("Shape of the DataFrame: ", df_new.shape)

        return df_new

    minutes = process_df(minutes, 'minutes')
    speeches = process_df(speeches, 'speeches')
    statements = process_df(statements, 'statements')
    testimony = process_df(testimony, 'testimony')
    press_conf = process_df(press_conf, 'pressconf')

    # combining fomc data together
    combined = pd.concat([minutes, speeches, statements, testimony, press_conf], sort=False)
    combined = combined.reset_index(drop=True)
    combined['date'] = pd.to_datetime(combined['date'])

    doc_types = combined['type'].unique()

    macro = pd.read_csv('data/macro/macro_filled.csv')
    macro.set_index('date', inplace=True)
    macro.index = pd.to_datetime(macro.index)

    # reshape macro data to monthly
    macro = macro.resample("M").mean()

    for date, row in macro.iterrows():
        # for a macro data date, get data from that date till next meeting.
        next_meeting_date = combined[combined['next_meeting'] >= date]['next_meeting'].min()
        text_rows = combined[(combined['date'] >= date) & (combined['date'] < next_meeting_date)]
        # note: should be after current i date (inclusive) and before next meeting date (exclusive)

        merged_text_all = ""
        for doc_type in doc_types:
            merged_text = ""
            for text in text_rows.loc[text_rows['type'] == doc_type]['text']:
                merged_text += " " + text
            macro.loc[date, doc_type] = merged_text
            merged_text_all += merged_text
        macro.loc[date, 'text'] = merged_text_all

    # Check if most of docs are merged
    count_text, count_train = 0, 0

    for doc_type in doc_types:
        count = 0
        for text in combined.loc[combined['type'] == doc_type]['text']:
            count += len(text.split())
        print(f'{count} words in original text for {doc_type}')
        count_text += count

        count = 0
        for text in macro[doc_type]:
            count += len(text.split())
        print(f'{count} words in merged text for {doc_type}')
        count_train += count

    print(f'Total: {count_text} words in original text')
    print(f'Total: {count_train} words in merged text')
    print(f'Total: {macro["text"].apply(lambda x: len(x.split())).sum()} words in text column of merged text')

    macro = macro.reset_index()

    return macro


if __name__ == '__main__':
    processed = preprocess()
    processed.to_csv('data/processed.txt', sep=',', index=False)
