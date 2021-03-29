import pandas as pd
from fredapi import Fred


def retrieve_macro_data() -> pd.DataFrame():
    """
    Retrieves macro data using FRED api from 2006 to today.

    :return: DataFrame representing macro data.
    """
    print('\n==========Collecting macro data==========')

    INDICATORS = {
        'DFEDTARL': 'Federal Funds Target Range - lower bound',
        'DFEDTARU': 'Federal Funds Target Range - upper bound',
        'GDPC1': 'Real GDP',
        'CPIAUCSL': 'Consumer Price Index (CPI)',
        'UNRATE': 'Unemployment Rate',
        'PAYEMS': 'Total NonFarm payrolls (Employment)',
        'RRSFS': 'Real Retail and Food Services Sales',
        'GFDEBTN': 'Federal Debt',
        'VIXCLS': 'CBOE Volatility Index (VIX)',
        'DFF': 'Effective Federal Funds Rate',
    }

    START_DATE = '1/1/2006'

    API_KEY = '2fb48248f0ce3781c82ffca58fecfb36'
    fred = Fred(api_key=API_KEY)

    full_data = pd.DataFrame()

    for indicator, name in INDICATORS.items():
        print(f'Indicator: {indicator}, Name: {name}')
        df = pd.DataFrame(fred.get_series(indicator, observation_start=START_DATE))

        if full_data.empty:
            full_data = df
        else:
            full_data = pd.concat([full_data, df], axis=1)

    full_data.columns = list(INDICATORS.keys())

    print("==========Done==========\n")

    return full_data

# df = retrieve_macro_data()
# df.to_csv('data/macro/macro_data.csv')
# df_filled = df.ffill()
# df_filled.to_csv('data/macro/macro_data_filled.csv')
