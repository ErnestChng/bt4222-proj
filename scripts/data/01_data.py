import time

from scripts.data.macro.macro_data import retrieve_macro_data
from scripts.data.textual.fomc_calendar import retrieve_fomc_calendar
from scripts.data.textual.fomc_minutes import retrieve_fomc_minutes
# from scripts.data.textual.fomc_press_conf import retrieve_press_conf
from scripts.data.textual.fomc_speeches import retrieve_fomc_speeches
from scripts.data.textual.fomc_statements import retrieve_fomc_statements
from scripts.data.textual.fomc_testimony import retrieve_fomc_testimony

if __name__ == "__main__":
    start_time = time.time()

    #### Scraping FOMC data ####
    minutes = retrieve_fomc_minutes()
    # press_conf = retrieve_press_conf()
    speeches = retrieve_fomc_speeches()
    statements = retrieve_fomc_statements()
    testimony = retrieve_fomc_testimony()
    calendar = retrieve_fomc_calendar()

    #### Retrieving Macro data ####
    macro = retrieve_macro_data()

    # #### Writing data ####
    # minutes.to_csv('data/textual/fomc_minutes.txt', sep=',', index=False)
    # # press_conf.to_csv('data/textual/fomc_press_conf.txt', sep=',', index=False)
    # speeches.to_csv('data/textual/fomc_speeches.txt', sep=',', index=False)
    # statements.to_csv('data/textual/fomc_statements.txt', sep=',', index=False)
    # testimony.to_csv('data/textual/fomc_testimony.txt', sep=',', index=False)
    # calendar.to_csv('data/textual/fomc_calendar.txt', sep=',', index=False)
    #
    # macro.to_csv('data/macro/macro_data.csv')
    # macro_ffill = macro.ffill()  # forward-filling data
    # macro_ffill.to_csv('data/macro/macro_data_filled.csv')

    print(f"Time taken: {time.time() - start_time}")
