import argparse
import sys
import time

import pandas as pd

from data.macro.macro_data import retrieve_macro_data
from data.textual.fomc_calendar import retrieve_fomc_calendar
from data.textual.fomc_minutes import retrieve_fomc_minutes
# from data.textual.fomc_press_conf import retrieve_fomc_press_conf
from data.textual.fomc_speeches import retrieve_fomc_speeches
from data.textual.fomc_statements import retrieve_fomc_statements
from data.textual.fomc_testimony import retrieve_fomc_testimony
from data.util import merge_data

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--type", required=True, help="Please specify 'overwrite' or 'merge'")
    args = vars(ap.parse_args())

    types = ('overwrite', 'merge')

    if args['type'] not in types:
        print("Please specify either 'overwrite' or 'merge' with the tag -t")
        sys.exit(1)

    if args['type'] == 'overwrite':
        print('\n==========Starting the scraping process==========')
        start_time = time.time()

        #### Scraping FOMC data ####
        minutes = retrieve_fomc_minutes()
        # press_conf = retrieve_fomc_press_conf()  # requires pdf files
        speeches = retrieve_fomc_speeches()
        statements = retrieve_fomc_statements()
        testimony = retrieve_fomc_testimony()
        calendar = retrieve_fomc_calendar()
        #### Retrieving Macro data ####
        macro = retrieve_macro_data()

        #### Writing data ####
        # minutes.to_csv('data/textual/fomc_minutes.txt', sep=',', index=False)
        # press_conf.to_csv('data/textual/fomc_press_conf.txt', sep=',', index=False)
        # speeches.to_csv('data/textual/fomc_speeches.txt', sep=',', index=False)
        # statements.to_csv('data/textual/fomc_statements.txt', sep=',', index=False)
        # testimony.to_csv('data/textual/fomc_testimony.txt', sep=',', index=False)
        # calendar.to_csv('data/textual/fomc_calendar.txt', sep=',', index=False)
        # macro.to_csv('data/macro/macro.csv')

        print("==========Done==========\n")
        print(f"Time taken for data collection: {time.time() - start_time}")
    else:  # merge existing csv files
        print('\n==========Starting the merging process==========')
        minutes = pd.read_csv('data/textual/fomc_minutes.txt', delimiter=',')
        press_conf = pd.read_csv('data/textual/fomc_press_conf.txt', delimiter=',')
        speeches = pd.read_csv('data/textual/fomc_speeches.txt', delimiter=',')
        statements = pd.read_csv('data/textual/fomc_statements.txt', delimiter=',')
        testimony = pd.read_csv('data/textual/fomc_testimony.txt', delimiter=',')

        macro = pd.read_csv('data/macro/macro.csv')
        macro.set_index('date', inplace=True)
        macro.index = pd.to_datetime(macro.index)

        raw_data = merge_data(minutes, press_conf, speeches, statements, testimony, macro)
        raw_data.to_csv('data/raw_data.txt', sep=',', index=False)
        print("==========Done==========\n")
