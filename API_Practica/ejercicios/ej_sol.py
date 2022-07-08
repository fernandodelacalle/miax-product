#%%

import pandas as pd
import requests
import json

#%%

class BMEApiHandler:

    def __init__(self):
        self.url_base = 'https://miax-gateway-jog4ew3z3q-ew.a.run.app'
        self.competi = 'mia_9'
        self.user_key = ''

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

    def send_alloc(self, algo_tag, market, str_date, allocation):
        url = f'{self.url_base}/participants/allocation'
        url_auth = f'{url}?key={self.user_key}'
        print(url_auth)
        params = {
            'competi': self.competi,
            'algo_tag': algo_tag,
            'market': market,
            'date': str_date,
            'allocation': allocation
        }
        #print(json.dumps(params))
        response = requests.post(url_auth, data=json.dumps(params))
        print(response.json())



#%% Descarga el maestro de valores.

market = 'IBEX'
api_handler = BMEApiHandler()
ticker_master = api_handler.get_ticker_master(market=market)


#%% Descarga todos los datos para cada ticker del maestro.
# Baja solo el close. Con las series close,
#  crea un datafame donde tengas como columnas los tickers y filas las fechas.

data_close_dict = {}
for idx, row in ticker_master.iterrows():
    tck = row.ticker
    close_data = api_handler.get_close_data(market, tck)
    data_close_dict[tck] = close_data
df_close = pd.DataFrame(data_close_dict)

# %% 
# - Recorre este dataframe cada 200 filas 
# y crea una lista de allocations con valor 1/n_activos.
# - Envía el post de estos allocations.

algo_tag = ''
for fecha, data in df_close.iloc[::200].iterrows():
    print(fecha)
    in_index = data.dropna().index
    alloc = 1 / len(in_index)
    allocation = [ 
        {'ticker': tk, 'alloc': alloc} 
        for tk in in_index
    ]
    str_date = fecha.strftime('%Y-%m-%d')
    api_handler.send_alloc(algo_tag, market, str_date, allocation)


# %%
# - Usa la API para obtener todas las allocations introducidas.
# - Usa la API para ejecutar el backtesting.
# - Elimina todas las allocations.



