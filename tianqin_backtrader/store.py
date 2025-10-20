import backtrader as bt
from tqsdk import TqApi, TqSim, TqAuth, TqKq
from .datafeed import Mydatafeed
import time
import datetime

class MyStore:
    def __init__(self, key='xxxxx', value='xxxxxx'):
        print("天勤量化连接中......")
        self.key = key
        self.value = value
        self.tianqin = TqApi(TqKq(), auth=TqAuth(key, value))
        print("天勤连接成功......")
        
    def getdata(self, instrument):
        return Mydatafeed(dataname=instrument, store=self)
    
    def retry(self):
        """
        重连函数, 天勤量化在早盘或者午盘断线时, 会自动断线, 需要重新连接（有待完善）
        1. 早上9点的时候(重启一次)
        2. 晚上9点的时候(重启一次)
        3. 中途断线的时候, 一直重启
        """
        now = datetime.datetime.now()
        if now.hour == 9 and now.minute == 0:  # 早上开盘的时候重启一次
            self.tianqin.close()
            self.tianqin = TqApi(TqKq(), auth=TqAuth(self.key, self.value))
        
        if now.hour == 21 and now.minute == 0:  # 夜盘的时候重启一次
            self.tianqin.close()
            self.tianqin = TqApi(TqKq(), auth=TqAuth(self.key, self.value))
        
        if now.hour >= 9 and now.hour <= 15:  # 中途断线时, 一直重启
            for _ in range(2):
                ok = self.tianqin.wait_update(deadline=time.time()+1)
            if not ok:
                self.tianqin.close()
                self.tianqin = TqApi(TqKq(), auth=TqAuth(self.key, self.value))
        
        # while True:
        #     kline = self.tianqin.get_kline_serial(instrument, 10)
        #     conn = self.tianqin.wait_update(deadline=time.time()+10)
        #     if not conn:
        #         print("天勤量化重新连接中......")
        #         self.tianqin = TqApi(TqSim(init_balance=100000), auth=TqAuth(self.key, self.value))
                
        #         kline = self.tianqin.get_kline_serial(instrument, 10)
        #         conn = self.tianqin.wait_update(deadline=time.time()+10)
        #     else:
        #         return
            
