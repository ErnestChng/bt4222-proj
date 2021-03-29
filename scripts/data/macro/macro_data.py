import pandas as pd
from fredapi import Fred


def retrieve_macro_data() -> pd.DataFrame():
    print('\nCollecting macro data...')

    API_KEY = '2fb48248f0ce3781c82ffca58fecfb36'
    INDICATORS = ['DFEDTARL',  # Federal Funds Target Range - lower bound
                  'DFEDTARU',  # Federal Funds Target Range - upper bound
                  'GDPC1',  # Real GDP
                  'CPIAUCSL',  # Consumer Price Index (CPI)
                  'UNRATE',  # Unemployment Rate
                  'PAYEMS',  # Total NonFarm payrolls (Employment)
                  'RRSFS',  # Real Retail and Food Services Sales
                  'GFDEBTN',  # Federal Debt
                  'VIXCLS',  # CBOE Volatility Index (VIX)
                  'DFF']  # Effective Federal Funds Rate

    fred = Fred(api_key=API_KEY)
    full_data = pd.DataFrame()

    START_DATE = '1/1/2006'

    for indicator in INDICATORS:
        df = pd.DataFrame(fred.get_series(indicator, observation_start=START_DATE))

        if full_data.empty:
            full_data = df
        else:
            full_data = pd.concat([full_data, df], axis=1)

    full_data.columns = INDICATORS

    return full_data
