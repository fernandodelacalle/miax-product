#%%

import pandas as pd
import requests


#%%


class BMEApiHandler:

    def __init__(self):
        self.url_base = 'https://miax-gateway-jog4ew3z3q-ew.a.run.app'
        self.competi = 'mia_9'
        self.user_key = 'AIzaSyCp_OAFjfw5uM_3ko3pZbGqJRvXqBGxLYE'

    def get_ticker_master(self, market):
        url = f'{self.url_base}/data/ticker_master'
        params = {'competi': self.competi,
                'market': market,
                'key': self.user_key}
        response = requests.get(url, params)
        tk_master = response.json()
        maestro_df = pd.DataFrame(tk_master['master'])
        return maestro_df

    def get_close_data(self, market, tck):
        url = f'{self.url_base}/data/time_series'
        params = {
            'market': market,
            'key': self.user_key,
            'ticker': tck
        }
        response = requests.get(url, params)
        tk_data = response.json()
        series_data = pd.read_json(tk_data, typ='series')
        return series_data

    def get_ohlc_data(self, market, tck):
        url = f'{self.url_base}/data/time_series'
        params = {
            'market': market,
            'key': self.user_key,
            'ticker': tck,
            'close': False
        }
        response = requests.get(url, params)
        tk_data = response.json()
        df_data = pd.read_json(tk_data, typ='frame')
        return df_data



#%%



market = 'IBEX'

api_handler = BMEApiHandler()
ticker_master = api_handler.get_ticker_master(market=market)


#%%


data_close_dict = {}
for idx, row in ticker_master.iterrows():
    tck = row.ticker
    close_data = api_handler.get_close_data(market, tck)
    data_close_dict[tck] = close_data
df_close = pd.DataFrame(data_close_dict)

