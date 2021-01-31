import quandl
import os
import pandas as pd

dir = '/Users/jolene/Downloads/1.BT4222/Group Project/bt4222-proj'
quandl.ApiConfig.api_key = '7zBDzsuMEcutufUJLKwc'
from_date = '2006-01-01'
indicators = ('DFEDTARL',  # FED rate lower bound
              'DFEDTARU',  # FED rate upper bound
              'GDPC1',     # Real GDP
              'CPIAUCSL',  # Consumer Price Index (CPI)
              'UNRATE',    # Unemployment Rate
              'PAYEMS',    # Total NonFarm payrolls (Employment)
              'RRSFS',     # Real Retail and Food Services Sales
              'GFDEBTN',   # Federal Debt
              'DFF')       # Effective Federal Funds Rate

full_data = pd.DataFrame()

for indicator in indicators:
    data = quandl.get(f"FRED/{indicator}", start_date=from_date)

    if full_data.empty:
        full_data = data
    else:
        full_data = pd.concat([full_data, data], axis=1)


full_data.columns = list(indicators)
full_data.to_csv(os.path.join(dir, './data/meta/market_data.csv'))

full_data = full_data.ffill()
full_data.to_csv(os.path.join(dir, './data/meta/market_data_filled.csv'))
