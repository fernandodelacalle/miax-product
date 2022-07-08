#%%

import pandas as pd
import requests
import json

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
    
    def get_algos(self):
        url = f'{self.url_base}/participants/algorithms'
        params = {'competi': self.competi,
                'key': self.user_key}
        response = requests.get(url, params)
        algos = response.json()
        if algos:
            algos_df = pd.DataFrame(algos)
            return algos_df

    def allocs_to_frame(self, json_allocations):
        alloc_list = []
        for json_alloc in json_allocations:
            #print(json_alloc)
            allocs = pd.DataFrame(json_alloc['allocations'])
            allocs.set_index('ticker', inplace=True)
            alloc_serie = allocs['alloc']
            alloc_serie.name = json_alloc['date'] 
            alloc_list.append(alloc_serie)
        all_alloc_df = pd.concat(alloc_list, axis=1).T
        return all_alloc_df

    def get_allocations(self, algo_tag, market):
        url = f'{self.url_base}/participants/algo_allocations'
        params = {
            'key': self.user_key,
            'competi': self.competi,
            'algo_tag': algo_tag,
            'market': market,
        }
        response = requests.get(url, params)
        df_allocs = self.allocs_to_frame(response.json())
        return df_allocs

    def backtest_algo(self, algo_tag, market):
        url = f'{self.url_base}/participants/exec_algo'
        url_auth = f'{url}?key={self.user_key}'
        params = {
            'competi': self.competi,
            'algo_tag': algo_tag,
            'market': market,
            }
        response = requests.post(url_auth, data=json.dumps(params))
        if response.status_code == 200:
            exec_data = response.json()
            status = exec_data.get('status')
            res_data = exec_data.get('content')
            if res_data:
                performace = pd.Series(res_data['result'])
                trades = pd.DataFrame(res_data['trades'])
                return performace, trades
        else:
            exec_data = dict()
            print(response.text)
    
    def delete_allocs(self, algo_tag, market):
        url = f'{self.url_base}/participants/delete_allocations'
        url_auth = f'{url}?key={self.user_key}'
        params = {
            'competi': self.competi,
            'algo_tag': algo_tag,
            'market': market,
            }
        response = requests.post(url_auth, data=json.dumps(params))
        print(response.text)



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

algo_tag = 'test_user_1_miax9_algo1'
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

# %%
api_handler.get_algos()

# %%
api_handler.get_allocations(algo_tag, market)


# %%
performace, trades = api_handler.backtest_algo(algo_tag, market)


# %%
api_handler.delete_allocs(algo_tag, market)
