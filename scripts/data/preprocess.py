import datetime as dt

import pandas as pd

minutes = pd.read_csv('data/textual/fomc_minutes.txt', delimiter=',')
speeches = pd.read_csv('data/textual/fomc_speeches.txt', delimiter=',')
statements = pd.read_csv('data/textual/fomc_statements.txt', delimiter=',')
testimony = pd.read_csv('data/textual/fomc_testimony.txt', delimiter=',')
pressconf = pd.read_csv('data/textual/fomc_press_conf.txt', delimiter=',')

pressconf.columns = pressconf.columns.str.lower()
pressconf = pressconf.sort_values('date', ascending=False)
pressconf.reset_index(drop=True, inplace=True)

print(f'minutes: {minutes.shape}')
print(f'speeches: {speeches.shape}')
print(f'statements: {statements.shape}')
print(f'testimony: {testimony.shape}')
print(f'testimony: {pressconf.shape}')

fomc_calendar = pd.read_csv('data/textual/fomc_calendar.txt', delimiter=',')
fomc_calendar.set_index('date', inplace=True)
fomc_calendar.index = pd.to_datetime(fomc_calendar.index)


def get_next_meeting_date(x):
    '''
    Returns the next fomc meeting date for the given date x, referring to fomc_calendar DataFrame.
    Usually FOMC Meetings takes two days, so it starts searching from x+2.
    x should be of datetime type or yyyy-mm-dd format string.
    '''
    # If x is string, convert to datetime
    if type(x) is str:
        try:
            x = dt.datetime.strptime(x, '%Y-%m-%d')
        except:
            return None

    # Add two days to get the day after next
    x = x + dt.timedelta(days=2)

    # Just in case, sort fomc_calendar from older to newer
    fomc_calendar.sort_index(ascending=True, inplace=True)

    if fomc_calendar.index[0] > x:
        # If the date is older than the first FOMC Meeting, do not return any date.
        return None
    else:
        for i in range(len(fomc_calendar)):
            if x < fomc_calendar.index[i]:
                return fomc_calendar.index[i]
        # If x is greater than the newest FOMC meeting date, do not return any date.
        return None


def reorganize_df(df, doc_type):
    '''
    Reorganize the loaded dataframe, which has been obrained by FomcGetData for further processing
        - Add type
        - Add word count
        - Add rate, decision (for meeting documents, None for the others)
        - Add next meeting date, rate and decision
        - Copy contents to org_text
        - Remove line breaks from contents in text
        - Split contents by "[SECTION]" to list in text_sections
    '''

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
pressconf = reorganize_df(pressconf, 'pressconf')

text_no_split = pd.concat([minutes,
                           speeches,
                           statements,
                           testimony,
                           pressconf], sort=False)

text_no_split.reset_index(drop=True, inplace=True)

############################################################

text_df = text_no_split

from collections import defaultdict

doc_types = text_df['type'].unique()

merged_dict = defaultdict(list)

train_df = pd.read_csv('data/macro/api_market_data_filled.csv').rename(columns={'Unnamed: 0': 'date'})
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
train_df = train_df.loc[train_df['text'] != ""]
print("After dropping: ", train_df.shape)

train_df = train_df.reset_index()
train_df.to_csv('data/textual/processed_text.txt', sep=',', index=False)
