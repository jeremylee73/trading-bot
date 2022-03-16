import alpaca_trade_api as tradeapi
import numpy as np
import warnings

warnings.filterwarnings('ignore')

SEC_KEY = 'ErfbtC51cM2GNWas76y1dc7wfiWeNONmvdxd32AX'
PUB_KEY = 'PKDN7L1U2E94IU8IOX97'
BASE_URL = 'https://paper-api.alpaca.markets'

class TradingBot():

  def __init__(self):
    self.api = tradeapi.REST(key_id=PUB_KEY, secret_key=SEC_KEY, base_url=BASE_URL)
    self.mode = 'buy'
    self.stock_lst = ['AMZN', 'SPY', 'AAPL', 'GOOG', 'BABA']
    self.portfolio = {}
    self.quantity = 1
    self.lower_buy_threshold = -0.001
    self.trend_buy_threshold = 0.002
    self.upper_sell_threshold = 0.001
    self.trend_sell_threshold = -0.002
    self.lookback = 5

  def buy_stock(self, stock, quantity):
    self.api.submit_order(
      symbol=stock,
      qty=quantity,
      side='buy',
      type='market', 
      time_in_force='gtc' # Good 'til cancelled
    )
    self.portfolio[stock] = self.api.get_position(stock).cost_basis
    self.mode = 'sell'

  def sell_stock(self, stock, quantity):
    self.api.submit_order(
      symbol=stock,
      qty=quantity,
      side='sell',
      type='market', 
      time_in_force='gtc' # Good 'til cancelled
    )
    self.mode = 'buy'

  def backtest(self, hours_to_test):

    historical_data = {}
    for stock in self.stock_lst:
      market_data = self.api.get_barset(stock, 'minute', limit=60*hours_to_test)[stock]
      close_prices = np.array([bar.c for bar in market_data])
      historical_data[stock] = close_prices
    
    balance = 100000
    transactions = {}
    modes = {}

    for stock in self.stock_lst:
      transactions[stock] = {'Buy':0, 'Sell':0}
      modes[stock] = 'buy'

    for i in range(len(close_prices) - self.lookback + 1):
      for stock in self.stock_lst:
        current_price = historical_data[stock][i + self.lookback - 1]
        moving_avg = np.mean(historical_data[stock][i:i + self.lookback])

        if moving_avg < (1 + self.lower_buy_threshold) * current_price and modes[stock] == 'buy':
          balance -= current_price
          modes[stock] = 'sell'
          transactions[stock]['Buy'] += 1
        if moving_avg > (1 + self.upper_sell_threshold) * current_price and modes[stock] == 'sell':
          balance += current_price
          modes[stock] = 'buy'
          transactions[stock]['Sell'] += 1

    for stock in self.stock_lst:
      if transactions[stock]['Buy'] > transactions[stock]['Sell']:
        balance += historical_data[stock][-1]

    print(transactions)

    return balance

  def run(self):
    # TODO
    return

bot = TradingBot()
print(bot.backtest(1))