import os
import pandas as pd
from fredapi import Fred

dir = '/Users/jolene/Downloads/1.BT4222/Group Project/bt4222-proj'
fred = Fred(api_key='2fb48248f0ce3781c82ffca58fecfb36')
start_date = '1/1/2006'
indicators = ('DFEDTARL',  # Federal Funds Target Range - lower bound
              'DFEDTARU',  # Federal Funds Target Range - upper bound
              'GDPC1',     # Real GDP
              'CPIAUCSL',  # Consumer Price Index (CPI)
              'UNRATE',    # Unemployment Rate
              'PAYEMS',    # Total NonFarm payrolls (Employment)
              'RRSFS',     # Real Retail and Food Services Sales
              'GFDEBTN',   # Federal Debt
              'VIXCLS',    # CBOE Volatility Index (VIX)
              'DFF')       # Effective Federal Funds Rate

full_data = pd.DataFrame()

for indicator in indicators:
    df = pd.DataFrame(fred.get_series(indicator, observation_start=start_date))

    if full_data.empty:
        full_data = df
    else:
        full_data = pd.concat([full_data, df], axis=1)


full_data.columns = list(indicators)
full_data.to_csv(os.path.join(dir, './data/meta/api_market_data.csv'))

full_data = full_data.ffill()
full_data.to_csv(os.path.join(dir, './data/meta/api_market_data_filled.csv'))
