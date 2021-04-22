import numpy as np
import pandas as pd


def merge_data(minutes: pd.DataFrame,
               press_conf: pd.DataFrame,
               speeches: pd.DataFrame,
               statements: pd.DataFrame,
               testimony: pd.DataFrame,
               macro: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge FOMC Textual data with Macro Data

    :param minutes: DataFrame representing minutes
    :param press_conf: DataFrame representing press_conf
    :param speeches: DataFrame representing speeches
    :param statements: DataFrame representing statements
    :param testimony: DataFrame representing testimony
    :param macro: DataFrame representing macro
    :return: DataFrame representing the combined raw data.
    """
    print(f'minutes: {minutes.shape}')
    print(f'speeches: {speeches.shape}')
    print(f'statements: {statements.shape}')
    print(f'testimony: {testimony.shape}')
    print(f'press conference: {press_conf.shape}')
    print(f'macro: {macro.shape}')

    minutes['type'] = 'minutes'
    speeches['type'] = 'speeches'
    statements['type'] = 'statements'
    testimony['type'] = 'testimony'
    press_conf['type'] = 'pressconf'

    # combining fomc data together
    combined = pd.concat([minutes, speeches, statements, testimony, press_conf], sort=False)
    combined = combined.reset_index(drop=True)
    combined['date'] = pd.to_datetime(combined['date'])
    doc_types = combined['type'].unique()

    for i in range(len(macro) - 1):
        date, next_date = macro.index[i], macro.index[i + 1]
        text_rows = combined[(combined['date'] >= date) & (combined['date'] < next_date)]

        merged_text_all = ""
        for doc_type in doc_types:
            merged_text = ""
            for text in text_rows.loc[text_rows['type'] == doc_type]['text']:
                merged_text += " " + text
            macro.loc[date, doc_type] = merged_text

            # to add in speaker for deeper analysis
            speaker = text_rows.loc[text_rows['type'] == doc_type, 'speaker'].dropna()
            if len(speaker) != 0:
                macro.loc[date, f'{doc_type}_speaker'] = '[next]'.join(list(speaker))
            else:
                macro.loc[date, f'{doc_type}_speaker'] = np.nan

            merged_text_all += merged_text

        macro.loc[date, 'text'] = merged_text_all

    macro = macro.reset_index()

    # to add in speaker for deeper analysis
    macro['speeches_speaker'] = macro['speeches_speaker'].replace(np.nan, '').apply(lambda x: x.split('[next]'))
    macro['testimony_speaker'] = macro['testimony_speaker'].replace(np.nan, '').apply(lambda x: x.split('[next]'))

    print(f'\nCombined raw_data: {macro.shape}')

    return macro
