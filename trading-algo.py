from zipline.api import record, symbol, order_target_percent, set_benchmark, get_open_orders
from zipline import run_algorithm
from zipline.utils.calendars.exchange_calendar_lse import LSEExchangeCalendar
import pytz
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
from collections import OrderedDict
from datetime import datetime


def initialize(context):
    set_benchmark(symbol("ETH"))


def handle_data(context, data):

    slow_ma = data.history(symbol("ETH"), fields='price', bar_count=50, frequency="1d").mean()
    fast_ma = data.history(symbol("ETH"), fields='price', bar_count=20, frequency="1d").mean()

    if fast_ma < slow_ma:
        if symbol("ETH") not in get_open_orders():
            order_target_percent(symbol("ETH"), 0.04)

    if fast_ma > slow_ma:
        if symbol("ETH") not in get_open_orders():
            order_target_percent(symbol("ETH"), 0.96)

    record(BTC=data.current(symbol('ETH'), fields='price'))


data = OrderedDict()
data['ETH'] = pd.read_csv("ETH-USD.csv")

data['ETH']['Date'] = pd.to_datetime(data['ETH']['Date'], utc=True)
data['ETH'].set_index('Date', inplace=True)
data['ETH'] = data['ETH'].resample("1d").mean()
data['ETH'].fillna(method="ffill", inplace=True)
data['ETH'] = data['ETH'][["High", "Low", "Close", "Open", "Volume"]]
print(data['ETH'].head())

panel = pd.Panel(data)
panel.minor_axis = ["high", "low", "close", "open", "volume"]
panel.major_axis = panel.major_axis.tz_localize(pytz.utc)
print(panel)

perf = run_algorithm(start=datetime(2017, 7, 1, 0, 0, 0, 0, pytz.utc),
                     end=datetime(2018, 6, 15, 0, 0, 0, 0, pytz.utc),
                     initialize=initialize,
                     capital_base=1000,
                     handle_data=handle_data,
                     trading_calendar=LSEExchangeCalendar(),
                     data=panel)

style.use("ggplot")

perf.portfolio_value.plot(label='Portfolio')
perf.BTC.plot(label='Ethereum')

plt.legend(loc=2)
plt.show()
