import backtrader as bt
import time
import datetime
from collections import deque
from backtrader.utils import date2num

"""
还需要将数据保存下来!!!!!!!!!!!!
还要就爱那个历史数据导入进去
"""
def trans_time(ts):
    try:
        from datetime import datetime
        timestamp_s = ts / 1e9
        dt_object = datetime.fromtimestamp(timestamp_s)
        formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_time
    except:
        return ts

class Mydatafeed(bt.feed.DataBase):
    params = (
        ("store", None), 
    )
    
    def __init__(self):
        super(Mydatafeed, self).__init__()
        self.price = []
        self.volume = []
        self.openinterest = []
        self.datetime = []
        self.amount = []
    
    def start(self):
        pass
    
    def islive(self):
        return True
    
    def _append_tick(self, tick):
        price = tick['bid_price1']
        amount = tick['amount']
        date = tick['datetime'].split('.')[0]
        # date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        openinterest = tick['open_interest']
        volume = tick['volume']
        
        self.price.append(price)
        self.volume.append(volume)
        self.openinterest.append(openinterest)
        self.datetime.append(date)
        self.amount.append(amount)
    
    def _clear(self):
        self.price = []
        self.volume = []
        self.openinterest = []
        self.datetime = []
        self.amount = []
    
    def _load(self):
        # self.p.retry(self.p.dataname)
        """
        获取数据(只能自己合成, 使用盘口数据合成)
        """
        # 这里完善重启逻辑
        
        ok = self.p.store.tianqin.wait_update(deadline=time.time()+1)
        if not ok:   # 收盘之后
            print("行情结束, 等待")
            return None
        
        tick = self.p.store.tianqin.get_quote(self.p.dataname)
        
        if len(self.price) == 0:
            # 没有数据的时候添加数据
            self._append_tick(tick)
            return None
        elif self.datetime[-1].split(':')[-2] != tick['datetime'].split('.')[0].split(':')[-2]:
            # 当分钟改变的时候先合成分钟数据, 再清空数据
            self.lines.datetime[0] = date2num(datetime.datetime.strptime(tick['datetime'].split('.')[0], '%Y-%m-%d %H:%M:%S'))
            self.lines.close[0] = self.price[-1]
            self.lines.open[0] = self.price[0]
            self.lines.high[0] = max(self.price)
            self.lines.low[0] = min(self.price)
            self.lines.volume[0] = self.volume[-1]
            self.lines.openinterest[0] = self.openinterest[-1]
            self.lines.amount[0] = self.amount[-1]
            
            self._clear()
        
            time.sleep(0.5)
            return True
        else:
            return None
        
        
        
