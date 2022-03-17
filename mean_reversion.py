import alpaca_trade_api as tradeapi
import numpy as np
import requests
import warnings

warnings.filterwarnings('ignore')

SEC_KEY = 'ErfbtC51cM2GNWas76y1dc7wfiWeNONmvdxd32AX'
PUB_KEY = 'PKDN7L1U2E94IU8IOX97'
BASE_URL = 'https://paper-api.alpaca.markets'
CRYPTO_BASE_URL = BASE_URL + '/v1beta1/crypto/{symbol}/trades'

class TradingBot():

  def __init__(self):
    self.api = tradeapi.REST(key_id=PUB_KEY, secret_key=SEC_KEY, base_url=BASE_URL)
    self.mode = 'buy'
    self.asset_lst = ['AMZN']
    self.portfolio = {}
    self.quantity = 0.01
    self.lower_buy_threshold = -0.001
    self.trend_buy_threshold = 0.002
    self.upper_sell_threshold = 0.001
    self.trend_sell_threshold = -0.002
    self.lookback = 5

  def buy_asset(self, asset, quantity):
    self.api.submit_order(
      symbol=asset,
      qty=quantity,
      side='buy',
      type='market', 
      time_in_force='gtc' # Good 'til cancelled
    )
    self.portfolio[asset] = self.api.get_position(asset).cost_basis
    self.mode = 'sell'

  def sell_asset(self, asset, quantity):
    self.api.submit_order(
      symbol=asset,
      qty=quantity,
      side='sell',
      type='market', 
      time_in_force='gtc' # Good 'til cancelled
    )
    self.mode = 'buy'

  def backtest(self, hours_to_test):

    historical_data = {}
    for asset in self.asset_lst:
      market_data = self.api.get_barset(asset, 'minute', limit=60*hours_to_test)[asset]
      close_prices = np.array([bar.c for bar in market_data])
      historical_data[asset] = close_prices

    balance = 100000
    transactions = {}
    modes = {}

    for asset in self.asset_lst:
      transactions[asset] = {'Buy':0, 'Sell':0}
      modes[asset] = 'buy'

    for i in range(len(close_prices) - self.lookback + 1):
      for asset in self.asset_lst:
        current_price = historical_data[asset][i + self.lookback - 1]
        moving_avg = np.mean(historical_data[asset][i:i + self.lookback])

        if current_price < (1 + self.lower_buy_threshold) * moving_avg and modes[asset] == 'buy':
          balance -= current_price * self.quantity
          modes[asset] = 'sell'
          transactions[asset]['Buy'] += 1
        if current_price > (1 + self.upper_sell_threshold) * moving_avg and modes[asset] == 'sell':
          balance += current_price * self.quantity
          modes[asset] = 'buy'
          transactions[asset]['Sell'] += 1

    for asset in self.asset_lst:
      if transactions[asset]['Buy'] > transactions[asset]['Sell']:
        balance += historical_data[asset][-1]

    print(transactions)
    print(str(round((balance - 100000) * 100 / 100000, 5)) + " percent change")

  def run(self):
    # TODO
    return

bot = TradingBot()
bot.backtest(16)