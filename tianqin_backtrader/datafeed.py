import backtrader as bt
import time
import datetime
import pandas as pd
from backtrader.utils.py3 import queue
from backtrader.utils import date2num
from .session_calendar import is_trading_time, is_trading_daily, is_trading_night

"""
需要详细检查一下历史数据
"""

class Mydatafeed(bt.feed.DataBase):
    params = (
        ("store", None), 
        ("lookback", False)
    )
    
    lines = ("bid_price1", "ask_price1", "bid_price2", "ask_price2", )
    def __init__(self):
        super(Mydatafeed, self).__init__()
        self.price = []
        self.volume = []
        self.openinterest = []
        self.mintue_datetime = []
        self.amount = []

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
        sd = df['datetime'].iloc[0]
        ed = df['datetime'].iloc[-1]
        print(f"品种 {self.p.dataname} 历史数据填充 ====== 开始日期: {sd} ====== 结束日期: {ed} ======")
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
                msg = self.qhist.get()
                if len(msg) != 0:
                    self.lines.datetime[0] = msg['datetime']
                    self.lines.close[0] = msg['close']
                    self.lines.open[0] = msg['open']
                    self.lines.high[0] = msg['high']
                    self.lines.low[0] = msg['low']
                    self.lines.volume[0] = msg['volume']
                    self.lines.openinterest[0] = 0
                    self.lines.bid_price1[0] = 0
                    self.lines.ask_price1[0] = 0
                    self.lines.bid_price2[0] = 0
                    self.lines.ask_price2[0] = 0
                    return True
                else:
                    self.p.lookback = False
                    self.history_phase = False
                    continue
            
            else:
                now = datetime.datetime.now()

                # if (self.trading_daily is None) or (now.hour==8 and now.minute==56):
                #     # 判断早早盘盘是否存在
                #     self.trading_daily = is_trading_daily()
                #     self.trading_night = is_trading_night()

                # if not self.trading_daily:   # 早盘没有那夜盘也一般没有
                #     # print("非交易日")
                #     continue

                if not is_trading_time(self.p.dataname):
                    # 非交易时间段, 不管
                    # print("非交易时间段")
                    continue
                
                self.p.store._fix_time_reconnect()     # 开盘重新启动
                self.p.store.save()                    # 数据保存

                tick = self.p.store.tianqin.get_quote(self.p.dataname)
                false_count = 0
                for _ in range(3):
                    ok = self.p.store.tianqin.wait_update(deadline=time.time()+5)
                    if not ok:
                        print("==================重连中========================")
                        false_count += 1
                if false_count == 3:
                    # 连续三次都重连不上说明不是交易日
                    continue
                
                if len(self.price) == 0:
                    # 没有数据的时候添加数据
                    self._append_tick(tick)
                    continue
                elif self.mintue_datetime[-1].split(':')[-2] != tick['datetime'].split('.')[0].split(':')[-2]:
                    # 当分钟改变的时候先合成分钟数据, 再清空数据
                    self.lines.datetime[0] = self.date2num(datetime.datetime.strptime(tick['datetime'].split('.')[0], '%Y-%m-%d %H:%M:%S'))
                    self.lines.close[0] = self.price[-1]
                    self.lines.open[0] = self.price[0]
                    self.lines.high[0] = max(self.price)
                    self.lines.low[0] = min(self.price)
                    self.lines.volume[0] = self.volume[-1]
                    self.lines.openinterest[0] = self.openinterest[-1]
                    self.lines.bid_price1[0] = tick['bid_price1']
                    self.lines.ask_price1[0] = tick['ask_price1']
                    self.lines.bid_price2[0] = tick['bid_price2']
                    self.lines.ask_price2[0] = tick['ask_price2']
                    
                    self._clear()
                    self._append_tick(tick)
                    return True
                else:
                    self._append_tick(tick)
                    continue
