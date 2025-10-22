import backtrader as bt
from tqsdk import TqApi, TqSim, TqAuth, TqKq
from .datafeed import Mydatafeed
from .broker import MyBroker
import time
import datetime

class MyStore:
    def __init__(self, key='xxxxx', value='xxxxxx'):
        print("天勤量化连接中......")
        self.key = key
        self.value = value
        self.tianqin = TqApi(TqKq(), auth=TqAuth(self.key, self.value))
        print("天勤连接成功......")
        
    def getdata(self, instrument):
        self.ins = instrument
        return Mydatafeed(dataname=instrument, store=self)
    
    def getbroker(self):
        return MyBroker(store=self)
    
    def _reconnect(self):
        """重连"""
        try:
            # 关闭现有连接
            self.tianqin.close()
            # 重连
            self.tianqin = TqApi(TqKq(), auth=TqAuth(self.key, self.value))
        except Exception as e:
            print('重连失败: ', e)

    def _fix_time_reconnect(self):
        """固定时点重连"""
        now = datetime.datetime.now()
        
        # 早盘重连
        if now.hour == 9 and now.minute == 0:
            print(f"{now} 早盘固定时点重连")
            self._reconnect()
            return None
        
        # 下午重连
        if now.hour == 13 and now.minute == 30:
            print(f"{now} 下午固定时点重连")
            self._reconnect()
            return None
        
        # 夜盘重连
        if now.hour == 21 and now.minute == 0:
            print(f"{now} 夜盘固定时点重连")
            self._reconnect()
            return None
        
        return True
