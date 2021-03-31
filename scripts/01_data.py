# import time

import pandas as pd


# from scripts.data.textual.fomc_calendar import retrieve_fomc_calendar
# from scripts.data.textual.fomc_minutes import retrieve_fomc_minutes
# # from scripts.data.textual.fomc_press_conf import retrieve_fomc_press_conf
# from scripts.data.textual.fomc_speeches import retrieve_fomc_speeches
# from scripts.data.textual.fomc_statements import retrieve_fomc_statements
# from scripts.data.textual.fomc_testimony import retrieve_fomc_testimony


def merge_data(minutes: pd.DataFrame,
               press_conf: pd.DataFrame,
               speeches: pd.DataFrame,
               statements: pd.DataFrame,
               testimony: pd.DataFrame,
               macro: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrame representing the combined raw data.

    :param minutes: DataFrame representing minutes
    :param press_conf: DataFrame representing press_conf
    :param speeches: DataFrame representing speeches
    :param statements: DataFrame representing statements
    :param testimony: DataFrame representing testimony
    :param macro: DataFrame representing macro
    :return:
    """
    print(f'minutes: {minutes.shape}')
    print(f'speeches: {speeches.shape}')
    print(f'statements: {statements.shape}')
    print(f'testimony: {testimony.shape}')
    print(f'press conference: {press_conf.shape}')

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

    print(f'macro: {macro.shape}')
    # reshape macro data to monthly
    macro = macro.resample("M").mean()
    print(f'macro after reshaping: {macro.shape}')

    for i in range(len(macro) - 1):
        date, next_date = macro.index[i], macro.index[i + 1]
        text_rows = combined[(combined['date'] >= date) & (combined['date'] < next_date)]

        merged_text_all = ""
        for doc_type in doc_types:
            merged_text = ""
            for text in text_rows.loc[text_rows['type'] == doc_type]['text']:
                merged_text += " " + text
            macro.loc[date, doc_type] = merged_text
            merged_text_all += merged_text

        macro.loc[date, 'text'] = merged_text_all

    macro = macro.reset_index()

    return macro


if __name__ == "__main__":
    # start_time = time.time()
    #
    # #### Scraping FOMC data ####
    # minutes = retrieve_fomc_minutes()
    # # press_conf = retrieve_fomc_press_conf() # requires pdf files
    # speeches = retrieve_fomc_speeches()
    # statements = retrieve_fomc_statements()
    # testimony = retrieve_fomc_testimony()
    # calendar = retrieve_fomc_calendar()
    #
    # #### Retrieving Macro data ####
    # # macro = retrieve_macro_data()
    #
    # # #### Writing data #### (uncomment if you want to rewrite current files)
    # # minutes.to_csv('data/textual/fomc_minutes.txt', sep=',', index=False)
    # # # press_conf.to_csv('data/textual/fomc_press_conf.txt', sep=',', index=False)
    # # speeches.to_csv('data/textual/fomc_speeches.txt', sep=',', index=False)
    # # statements.to_csv('data/textual/fomc_statements.txt', sep=',', index=False)
    # # testimony.to_csv('data/textual/fomc_testimony.txt', sep=',', index=False)
    # # calendar.to_csv('data/textual/fomc_calendar.txt', sep=',', index=False)
    # # macro.to_csv('data/macro/macro_data.csv')
    # # macro_ffill = macro.ffill()  # forward-filling data
    # # macro_ffill.to_csv('data/macro/macro_data_filled.csv')
    #
    # print(f"Time taken for data collection: {time.time() - start_time}")

    minutes = pd.read_csv('data/textual/fomc_minutes.txt', delimiter=',')
    press_conf = pd.read_csv('data/textual/fomc_press_conf.txt', delimiter=',')
    speeches = pd.read_csv('data/textual/fomc_speeches.txt', delimiter=',')
    statements = pd.read_csv('data/textual/fomc_statements.txt', delimiter=',')
    testimony = pd.read_csv('data/textual/fomc_testimony.txt', delimiter=',')

    macro = pd.read_csv('data/macro/macro_filled.csv')
    macro.set_index('date', inplace=True)
    macro.index = pd.to_datetime(macro.index)

    raw_data = merge_data(minutes, press_conf, speeches, statements, testimony, macro)
    raw_data.to_csv('data/raw_data.txt', sep=',', index=False)
