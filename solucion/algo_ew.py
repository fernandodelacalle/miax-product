import pandas as pd
import requests, json


class ApiHandler:
    def __init__(self, market, algo_tag):
        self.market = market
        self.competi = 'mia_7'
        self.user_key = 'AIzaSyCWjvfiRkwssq-LX0Gwy6nsLfznrE44fuw'
        self.url_base = 'https://miax-gateway-jog4ew3z3q-ew.a.run.app'
        self.algo_tag = algo_tag
    
    def get_ticker_master(self):
        url = f'{self.url_base}/data/ticker_master'
        headers = {'Content-Type': 'application/json'}
        params = {'competi': self.competi,
                  'market': self.market,
                  'key': self.user_key}
        response = requests.get(url, params)
        tk_master = response.json()
        maestro_df = pd.DataFrame(tk_master['master'])
        return maestro_df

    def get_close_data(self, ticker):
        url2 = f'{self.url_base}/data/time_series'
        params = {'market': self.market,
                  'key': self.user_key,
                  'ticker': ticker}
        response = requests.get(url2, params)
        tk_data = response.json()
        series_data = pd.read_json(tk_data, typ='series')
        return series_data
    
    def get_all_close(self):
        df = pd.DataFrame({
            tck: self.get_close_data(tck)
            for tck in ticker_master.loc[:, 'ticker'].to_list()
        })
        return df

    def update_all_close(self):
        self.df_all_close = self.get_all_close()
    

    def send_alloc(self, iday, allocation):
        url = f'{self.url_base}/participants/allocation'
        url_auth = f'{url}?key={self.user_key}'

        str_date = iday.strftime('%Y-%m-%d')
        params = {
            'competi': self.competi,
            'algo_tag': self.algo_tag,
            'market': self.market,
            'date': str_date,
            'allocation': allocation
        }
        #print(json.dumps(params))
        response = requests.post(url_auth, data=json.dumps(params))
        print(response.json())
        
    def run_backtest(self):
        url = f'{self.url_base}/participants/exec_algo'
        url_auth = f'{url}?key={self.user_key}'
        params = {
            'competi': self.competi,
            'algo_tag': self.algo_tag,
            'market': self.market,
        }
        response = requests.post(url_auth, data=json.dumps(params))
        if response.status_code == 200:
            exec_data = response.json()
            status = exec_data.get('status')
            print(status)
            res_data = exec_data.get('content')
            trades = None
            if res_data:
                self.dellete_all_allocs()
                print(pd.Series(res_data['result']))
                trades = pd.DataFrame(res_data['trades'])
            return res_data
        else:
            exec_data = dict()
            print(response.text)
            
    def dellete_all_allocs(self):
        url = f'{self.url_base}/participants/delete_allocations'
        url_auth = f'{url}?key={self.user_key}'
        params = {
            'competi': self.competi,
            'algo_tag': self.algo_tag,
            'market': self.market,
        }
        response = requests.post(url_auth, data=json.dumps(params))
        
def gen_alloc_data(ticker, alloc):
    return {'ticker': ticker,
            'alloc': alloc}

class AlgoEW:
    def __init__(self, market, algo_tag, rebal_period):
        self.market = market
        self.algo_tag = algo_tag
        self.rebal_period = rebal_period
        self.ah = ApiHandler(market=market, algo_tag=algo_tag)  
    
    def daily_proc(self):
        # 1. llamar a get_allocs
        # 2. el día de hoy - ultima rebal <= self.rebal_period
        # 3. ejecuto
        data = self.ah.get_all_close()
        data_today = data.iloc[-1,:]
        date = data_today.name
        w = 1/data_today.shape[0]
        alloc_list = [
            gen_alloc_data(tck, w) for tck in data_today.index
        ]
        self.ah.send_alloc(date, alloc_list)
        
        
        
algo_1 = AlgoEW(market='IBEX', algo_tag='test_user_1_miax7_algo2', rebal_period=30)  
algo_1.daily_proc()  

        