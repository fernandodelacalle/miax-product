import pandas as pd
import requests, json
from datetime import datetime


class BMEApiHandler:
    
    def __init__(self):
        self.url_base = 'https://miax-gateway-jog4ew3z3q-ew.a.run.app'
        self.competi = 'mia_10'
        self.user_key = ''
        self.market = 'IBEX'

    def get_ticker_master(self):
        url = f'{self.url_base}/data/ticker_master'
        params = {
            'competi': self.competi,
            'market': self.market,
            'key': self.user_key
        }
        response = requests.get(url, params)
        tk_master = response.json()
        maestro_df = pd.DataFrame(tk_master['master'])
        return maestro_df

    def get_ohlcv_data(self, tck):
        url2 = f'{self.url_base}/data/time_series'
        params = {'market': self.market,
          'key': self.user_key,
          'ticker': tck,
          'close': False}
        response = requests.get(url2, params)
        tk_data = response.json()
        df_data = pd.read_json(tk_data, typ='frame')
        return df_data
    
    
    def get_close_data(self, tck):
        url2 = f'{self.url_base}/data/time_series'
        params = {
            'market': self.market,
            'key': self.user_key,
            'ticker': tck,
            'close': True
        }
        response = requests.get(url2, params)
        tk_data = response.json()
        series_data = pd.read_json(tk_data, typ='series')
        return series_data

    def send_alloc(self, algo_tag, date, allocation):
        url = f'{self.url_base}/participants/allocation?key={self.user_key}'
        data = {
            'competi': self.competi,
            'algo_tag': algo_tag,
            'market': self.market,
            'date': date,
            'allocation': allocation
        }
        response = requests.post(url, data=json.dumps(data))
        print(response.text)

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

    def get_allocs(self, algo_tag):
        url = f'{self.url_base}/participants/algo_allocations'
        params = {
            'key': self.user_key,
            'competi': self.competi,
            'algo_tag': algo_tag,
            'market': self.market,
        }
        response = requests.get(url, params)
        return self.allocs_to_frame(response.json())

    def delete_allocs(self, algo_tag):
        url = f'{self.url_base}/participants/delete_allocations'
        url_auth = f'{url}?key={user_key}'
        params = {
            'competi': self.competi,
            'algo_tag': algo_tag,
            'market': self.market,
            }
        response = requests.post(url_auth, data=json.dumps(params))
        print(response.status_code)


    def get_algos(self):
        url = f'{self.url_base}/participants/algorithms'
        params = {
            'competi': self.competi,
            'key': self.user_key
        }
        response = requests.get(url, params)
        algos = response.json()
        algos_df = pd.DataFrame(algos)
        return algos_df

    def exec_algo(self, algo_tag):
        url = f'{self.url_base}/participants/exec_algo?key={user_key}'
        params = {
            'competi': self.competi,
            'algo_tag': algo_tag,
            'market': self.market,
        }
        response = requests.post(url, data=json.dumps(params))
        if response.status_code == 200:
            exec_data = response.json()
            status = exec_data.get('status')
            print(status)
            res_data = exec_data.get('content')
            if res_data:
                metrics = pd.Series(res_data['result'])
                trades = pd.DataFrame(res_data['trades'])
                return metrics, trades
        else:
            exec_data = dict()
            print(response.text)
    
    def get_exec_results(self, algo_tag):
        url = f'{self.url_base}/participants/algo_exec_results'
        params = {
            'key': user_key,
            'competi': competi,
            'algo_tag': algo_tag,
            'market': market,
        }

        response = requests.get(url, params)
        exec_data = response.json()
        print(exec_data.get('status'))
        res_data = exec_data.get('content')
        if res_data:
            metrics = pd.Series(res_data['result'])
            trades = pd.DataFrame(res_data['trades'])
            return metrics, trades
        

        


class EqwAlgo:
    
    def __init__(self, algo_tag, n_days):
        self.algo_tag = algo_tag
        self.n_days = n_days
        self.apih = BMEApiHandler()
        self.df_close = None   
    
    def get_all_data(self):
        maestro = self.apih.get_ticker_master()
        data_close_all = {}
        for _, row in maestro.iterrows():
            tck = row.ticker
            print(f"Download: {tck}", end=' ')
            close_data = self.apih.get_close_data(tck)
            data_close_all[tck] = close_data    
            df_close = pd.DataFrame(data_close_all)
        self.df_close = df_close

    def send_allocs_backtest(self):
        self.apih.delete_allocs(self.algo_tag)
        for date, data in self.df_close.iloc[::self.n_days].iterrows():
            print(date)
            tcks_activos = data.dropna().index
            alloc = 1/tcks_activos.shape[0]
            allocations_to_sent = [
                {'ticker': tck, 'alloc': alloc}
                for tck in tcks_activos
            ]
            date = date.strftime('%Y-%m-%d')
            self.apih.send_alloc(self.algo_tag, date, allocations_to_sent)
    
    def run_algo_backtest(self):
        self.get_all_data()
        self.send_allocs_backtest()
        print(apih.exec_algo(self.algo_tag))
    
    def get_result_timeout(self):
        metrics, trades = self.apih.get_exec_results(self.algo_tag)
        print(metrics)
        
    def get_allocs(self):
        self.apih.get_allocs(self.algo_tag)
        
        
    def run_day(self):          
        maestro = self.apih.get_ticker_master()
        tck_today = maestro[maestro.end_date == ''].ticker

        alloc = 1/tck_today.shape[0]
        allocations_to_sent = [
            {'ticker': tck, 'alloc': alloc}
            for tck in tck_today
        ]
        today = datetime.now()
        date = today.strftime('%Y-%m-%d')
        self.apih.send_alloc(self.algo_tag, date, allocations_to_sent)

        
        
    def run_day_comp(self):
        allocs = self.apih.get_allocs(self.algo_tag)
        last_day_alloc = pd.Timestamp(allocs.index[-1])
        
        today = datetime.now()
        days_delta = (today - last_day_alloc).days
        
        if days_delta > self.n_days:

            print('me toca rebal')     
            maestro = self.apih.get_ticker_master()
            tck_today = maestro[maestro.end_date == ''].ticker

            alloc = 1/tck_today.shape[0]
            allocations_to_sent = [
                {'ticker': tck, 'alloc': alloc}
                for tck in tck_today
            ]
            today = datetime.now()
            date = today.strftime('%Y-%m-%d')
            self.apih.send_alloc(self.algo_tag, date, allocations_to_sent)
        else:
            print('no toca')
        


eq_w_1 = EqwAlgo(algo_tag='test_user_1_miax10_algo3', n_days=100)
eq_w_1.run_day()


