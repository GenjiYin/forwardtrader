import backtrader as bt
import time
import datetime
from .session_calendar import is_trading_time, is_trading_daily, is_trading_night

"""
还需要将数据保存下来!!!!!!!!!!!!
还要将历史数据导入进去
"""

class Mydatafeed(bt.feed.DataBase):
    params = (
        ("store", None), 
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
    
    def start(self):
        pass
    
    def islive(self):
        return True
    
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
        now = datetime.datetime.now()

        if (self.trading_daily is None or self.trading_night is None) or (now.hour==8 and now.minute==56):
            # 判断早夜盘是否存在
            self.trading_daily = is_trading_daily()
            self.trading_night = is_trading_night()

        if not self.trading_daily:   # 早盘没有那夜盘也一般没有
            return None

        if not is_trading_time(self.p.dataname):
            # 非交易时间段, 不管
            return None
        
        self.p.store._fix_time_reconnect()

        tick = self.p.store.tianqin.get_quote(self.p.dataname)
        for _ in range(2):
            ok = self.p.store.tianqin.wait_update(deadline=time.time()+5)
        
        if len(self.price) == 0:
            # 没有数据的时候添加数据
            self._append_tick(tick)
            return None
        elif self.mintue_datetime[-1].split(':')[-2] != tick['datetime'].split('.')[0].split(':')[-2]:
            # 当分钟改变的时候先合成分钟数据, 再清空数据
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
            self._append_tick(tick)
        
            time.sleep(0.5)
            return True
        else:
            self._append_tick(tick)
            return None
        
        
        
