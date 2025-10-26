import backtrader as bt
import time
import datetime
import pandas as pd
from backtrader.utils.py3 import queue
from backtrader.utils import date2num
from .session_calendar import is_trading_time, is_trading_daily, is_trading_night

"""
核对一下成交量的聚合方式
"""

class Mydatafeed(bt.feed.DataBase):
    params = (
        ("store", None), 
        ("lookback", False)
    )
    
    lines = ("bid_price", "ask_price", )
    def __init__(self):
        super(Mydatafeed, self).__init__()
        self.price = []
        self.volume = []
        self.openinterest = []
        self.mintue_datetime = []
        self.amount = []

        self.trading_daily = None         # 用来记录当天日盘是否会开盘
        self.trading_night = None         # 用来记录当天夜盘是否会开盘

        self.history_phase = True if self.p.lookback else False        # 标记当前是否处于历史数据阶段

        self.get_history_queue()
    
    def start(self):
        pass
    
    def islive(self):
        return True
    
    def get_history_queue(self):
        """历史数据回填专用队列"""
        self.qhist = queue.Queue()
        def trans_time(ts):
            try:
                from datetime import datetime
                timestamp_s = ts / 1e9
                dt_object = datetime.fromtimestamp(timestamp_s)
                formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                return formatted_time
            except:
                return ts
        data = self.p.store.tianqin.get_kline_serial(self.p.dataname, duration_seconds=60, data_length=10000)
        df = data.copy().sort_values("datetime")
        df['datetime'] = df['datetime'].apply(trans_time)
        df = df[df['datetime']>=df[df['datetime'].str.contains(" 21:00")]['datetime'].iloc[0]]
        for i in range(len(df)):
            msg = df.iloc[i].to_dict()
            msg['datetime'] = date2num(datetime.datetime.strptime(msg['datetime'], '%Y-%m-%d %H:%M:%S'))
            self.qhist.put(msg)
        
        self.qhist.put({})
    
    def _append_tick(self, tick):
        price = tick['bid_price1']
        date = tick['datetime'].split('.')[0]
        # date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        openinterest = tick['open_interest']
        volume = tick['volume']
        
        self.price.append(price)
        self.volume.append(volume)
        self.openinterest.append(openinterest)
        self.mintue_datetime.append(date)
    
    def _clear(self):
        self.price = []
        self.volume = []
        self.openinterest = []
        self.mintue_datetime = []
    
    def _load(self):
        """
        获取数据
        这里最前面需要写一个重启机制
        1. 非交易时间段: 直接return None
        2. 交易时间段, 开盘那一刻(9点)和夜盘(21点)那一刻重新连接, 然后wait_update返回True可以继续, 否则None(因为有可能节假日也是false)
        """
        while True:
            if self.p.lookback:
                # 加载历史数据
                msg = self.qhist.get_nowait()
                if len(msg) != 0:
                    self.lines.datetime[0] = msg['datetime']
                    self.lines.close[0] = msg['close']
                    self.lines.open[0] = msg['open']
                    self.lines.high[0] = msg['high']
                    self.lines.low[0] = msg['low']
                    self.lines.volume[0] = msg['volume']
                    self.lines.openinterest[0] = 0
                    self.lines.bid_price[0] = 0
                    self.lines.ask_price[0] = 0
                    return True
                else:
                    self.p.lookback = False
                    self.history_phase = False
                    continue
            
            else:
                now = datetime.datetime.now()

                if (self.trading_daily is None or self.trading_night is None) or (now.hour==8 and now.minute==56):
                    # 判断早夜盘是否存在
                    self.trading_daily = is_trading_daily()
                    self.trading_night = is_trading_night()

                if not self.trading_daily:   # 早盘没有那夜盘也一般没有
                    # print("非交易日")
                    continue

                if not is_trading_time(self.p.dataname):
                    # 非交易时间段, 不管
                    # print("非交易时间段")
                    continue
                
                self.p.store._fix_time_reconnect()
                self.p.store.save()

                tick = self.p.store.tianqin.get_quote(self.p.dataname)
                for _ in range(2):
                    ok = self.p.store.tianqin.wait_update(deadline=time.time()+5)
                
                if len(self.price) == 0:
                    # 没有数据的时候添加数据
                    self._append_tick(tick)
                    continue
                elif self.mintue_datetime[-1].split(':')[-2] != tick['datetime'].split('.')[0].split(':')[-2]:
                    # 当分钟改变的时候先合成分钟数据, 再清空数据
                    self._append_tick(tick)
                    self.lines.datetime[0] = self.date2num(datetime.datetime.strptime(tick['datetime'].split('.')[0], '%Y-%m-%d %H:%M:%S'))
                    self.lines.close[0] = self.price[-1]
                    self.lines.open[0] = self.price[0]
                    self.lines.high[0] = max(self.price)
                    self.lines.low[0] = min(self.price)
                    self.lines.volume[0] = self.volume[-1]
                    self.lines.openinterest[0] = self.openinterest[-1]
                    self.lines.bid_price[0] = tick['bid_price1']
                    self.lines.ask_price[0] = tick['ask_price1']
                    
                    self._clear()
                    return True
                else:
                    self._append_tick(tick)
                    continue

class Dailyfeed(bt.feed.DataBase):
    params = (
        ("store", None), 
        ("lookback", False)
    )
    def __init__(self):
        super(Dailyfeed, self).__init__()
        self.price = []
        self.volume = []
        self.openinterest = []
        self.mintue_datetime = []
        self.amount = []

        self.trading_daily = None         # 用来记录当天日盘是否会开盘
        self.trading_night = None         # 用来记录当天夜盘是否会开盘

        self.history_phase = True if self.p.lookback else False        # 标记当前是否处于历史数据阶段

        self.get_history_queue()

    def start(self):
        pass
    
    def islive(self):
        return True
    
    def get_history_queue(self):
        """历史数据回填专用队列"""
        self.qhist = queue.Queue()
        def trans_time(ts):
            try:
                from datetime import datetime
                timestamp_s = ts / 1e9
                dt_object = datetime.fromtimestamp(timestamp_s)
                formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                return formatted_time
            except:
                return ts
        data = self.p.store.tianqin.get_kline_serial(self.p.dataname, duration_seconds=60, data_length=10000)
        df = data.copy().sort_values("datetime")
        df['datetime'] = df['datetime'].apply(trans_time)
        df['datetime'] = pd.to_datetime(df['datetime'])
        # df = df[df['datetime']>=df[df['datetime'].str.contains(" 21:00")]['datetime'].iloc[0]]

        def aggregate_k_lines(df, date_col='datetime'):
            """
            将分钟行情数据按照夜盘21:00到次日15:00聚合成K线
            """
            # 确保date列是datetime类型
            df = df.copy()
            df.sort_values(date_col, inplace=True)

            # 创建交易日标识
            # 如果时间在21:00-23:59，属于次日交易日
            # 如果时间在00:00-15:00，属于当日交易日
            def get_trading_day(dt):
                if dt.hour >= 21:  # 夜盘时间，属于次日
                    return dt.date() + pd.Timedelta(days=1)
                else:  # 白天时间，属于当日
                    return dt.date()
            df['trading_day'] = df[date_col].apply(get_trading_day)
            return df
        
        def aggregate_group(group):
            return pd.Series({
                'open': group['open'].iloc[0],
                'high': group['high'].max(),
                'low': group['low'].min(),
                'close': group['close'].iloc[-1],
                'volume': group['volume'].sum(),
                'amount': group.get('amount', group['volume'] * group['close']).sum(),
                'start_time': group['datetime'].iloc[0],
                'end_time': group['datetime'].iloc[-1],
                'bar_count': len(group)
            })
        df = aggregate_k_lines(df).groupby('trading_day').apply(aggregate_group, include_groups=False).reset_index()
        for i in range(len(df)):
            msg = df.iloc[i].to_dict()
            msg['datetime'] = msg['end_time'].strftime("%Y-%m-%d %H:%M:%S")
            msg['datetime'] = date2num(datetime.datetime.strptime(msg['datetime'], '%Y-%m-%d %H:%M:%S'))
            self.qhist.put(msg)

        self.qhist.put({})

    def _append_tick(self, tick):
        price = tick['bid_price1']
        date = tick['datetime'].split('.')[0]
        # date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        openinterest = tick['open_interest']
        volume = tick['volume']
        
        self.price.append(price)
        self.volume.append(volume)
        self.openinterest.append(openinterest)
        self.mintue_datetime.append(date)
    
    def _clear(self):
        self.price = []
        self.volume = []
        self.openinterest = []
        self.mintue_datetime = []

    def _load(self):
        while True:
            if self.p.lookback:
                # 加载历史数据
                msg = self.qhist.get_nowait()
                if len(msg) != 0:
                    self.lines.datetime[0] = msg['datetime']
                    self.lines.close[0] = msg['close']
                    self.lines.open[0] = msg['open']
                    self.lines.high[0] = msg['high']
                    self.lines.low[0] = msg['low']
                    self.lines.volume[0] = msg['volume']
                    self.lines.openinterest[0] = 0
                    return True
                else:
                    self.p.lookback = False
                    self.history_phase = False
                    continue
            else:
                now = datetime.datetime.now()

                if (self.trading_daily is None or self.trading_night is None) or (now.hour==8 and now.minute==56):
                    # 判断早夜盘是否存在
                    self.trading_daily = is_trading_daily()
                    self.trading_night = is_trading_night()

                if not self.trading_daily:   # 早盘没有那夜盘也一般没有
                    # print("非交易日")
                    continue

                if not is_trading_time(self.p.dataname):
                    # 非交易时间段, 不管
                    # print("非交易时间段")
                    continue

                tick = self.p.store.tianqin.get_quote(self.p.dataname)
                for _ in range(2):
                    ok = self.p.store.tianqin.wait_update(deadline=time.time()+5)

                if len(self.price) == 0:
                    # 没有数据的时候添加数据
                    self._append_tick(tick)
                    continue
                elif now.hour == 14 and now.minute == 59 and now.second == 55 and len(self.price) > 0:
                    # 天数发生变化, 对tick进行聚合
                    self._append_tick(tick)
                    self.lines.datetime[0] = self.date2num(datetime.datetime.strptime(tick['datetime'].split('.')[0], '%Y-%m-%d %H:%M:%S'))
                    self.lines.close[0] = self.price[-1]
                    self.lines.open[0] = self.price[0]
                    self.lines.high[0] = max(self.price)
                    self.lines.low[0] = min(self.price)
                    self.lines.volume[0] = sum(self.volume)
                    self.lines.openinterest[0] = sum(self.openinterest)

                    self._clear()
                    return True
                else:
                    self._append_tick(tick)
                    continue