import datetime as dt
from typing import Optional, Union

import pandas as pd

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


def get_next_meeting_date(curr_date: Union[str, dt.datetime]) -> Optional[dt.datetime]:
    if type(curr_date) is str:
        try:
            curr_date = dt.datetime.strptime(curr_date, '%Y-%m-%d')
        except Exception as e:
            return None

    curr_date = curr_date + dt.timedelta(days=2)

    fomc_calendar.sort_index(ascending=True, inplace=True)

    if fomc_calendar.index[0] > curr_date:
        return None
    else:
        for i in range(len(fomc_calendar)):
            if curr_date < fomc_calendar.index[i]:
                return fomc_calendar.index[i]
        return None


def reorganize_df(df: pd.DataFrame, doc_type: str):
    """
    Reorganize the loaded dataframe, which has been obtained by FomcGetData for further processing
        - Add type
        - Add word count
        - Add rate, decision (for meeting documents, None for the others)
        - Add next meeting date, rate and decision
        - Copy contents to org_text
        - Remove line breaks from contents in text
        - Split contents by "[SECTION]" to list in text_sections
    """

    dict = {
        'type': doc_type,
        'date': df['date'],
        'title': df['title'],
        'speaker': df['speaker'],
        'next_meeting': df['date'].map(get_next_meeting_date),
        'text': df['text']
    }

    new_df = pd.DataFrame(dict)
    print("Shape of the dataframe: ", new_df.shape)

    return new_df


minutes = reorganize_df(minutes, 'minutes')
speeches = reorganize_df(speeches, 'speeches')
statements = reorganize_df(statements, 'statements')
testimony = reorganize_df(testimony, 'testimony')
press_conf = reorganize_df(press_conf, 'pressconf')

text_no_split = pd.concat([minutes,
                           speeches,
                           statements,
                           testimony,
                           press_conf], sort=False)

text_no_split.reset_index(drop=True, inplace=True)

############################################################

text_df = text_no_split

from collections import defaultdict

doc_types = text_df['type'].unique()

merged_dict = defaultdict(list)

train_df = pd.read_csv('data/macro/macro_filled.csv').rename(columns={'Unnamed: 0': 'date'})
train_df.set_index('date', inplace=True)
train_df.index = pd.to_datetime(train_df.index)
text_df['date'] = pd.to_datetime(text_df['date'])

# reshape macro data to monthly
train_df = train_df.resample("M").mean()

for i, row in train_df.iterrows():

    # for a macro data date, get data from that date till next meeting.
    next_meeting_date = text_df[text_df['next_meeting'] >= i]['next_meeting'].min()
    text_rows = text_df[(text_df['date'] >= i) & (text_df['date'] < next_meeting_date)]
    # note: should be after current i date (inclusive) and before next meeting date (exclusive)

    merged_text_all = ""
    for doc_type in doc_types:
        merged_text = ""
        for text in text_rows.loc[text_rows['type'] == doc_type]['text']:
            merged_text += " " + text
        train_df.loc[i, doc_type] = merged_text
        merged_text_all += merged_text
    train_df.loc[i, 'text'] = merged_text_all

# Check if most of docs are merged
count_text, count_train = 0, 0

for doc_type in doc_types:
    count = 0
    for text in text_df.loc[text_df['type'] == doc_type]['text']:
        count += len(text.split())
    print("{} words in original text for {}".format(count, doc_type))
    count_text += count

    count = 0
    for text in train_df[doc_type]:
        count += len(text.split())
    print("{} words in merged text for {}".format(count, doc_type))
    count_train += count

print("Total: {} words in original text".format(count_text))
print("Total: {} words in merged text".format(count_train))
print("Total: {} words in text column of merged text".format(train_df['text'].apply(lambda x: len(x.split())).sum()))

print("Before dropping: ", train_df.shape)
# train_df = train_df.loc[train_df['text'] != ""]
# print("After dropping: ", train_df.shape)

train_df = train_df.reset_index()
train_df.to_csv('data/processed.txt', sep=',', index=False)
