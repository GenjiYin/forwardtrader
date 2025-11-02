import backtrader as bt
from tqsdk import TqApi, TqSim, TqAuth, TqKq
from .datafeed import Mydatafeed
from .datafeed_v2 import Mydatafeed_v2, TickDataFeed
from .session_calendar import CLASS_SESSIONS
from .broker import MyBroker
import time
import datetime
import pandas as pd
import os

class MyStore:
    def __init__(self, key='xxxxx', value='xxxxxx', strategy_name=""):
        print("天勤量化连接中......")
        self.key = key
        self.value = value
        self.tianqin = TqApi(TqKq(), auth=TqAuth(self.key, self.value))
        print("天勤连接成功......")
        
        # ✅ 新增：记录已执行重连的“分钟键”
        self._reconnect_done = set()

        # 新建一个文件夹专门用来储存持仓、订单成交情况、委托单
        current_dir = os.getcwd()
        self.save_path = os.path.join(current_dir, strategy_name)
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        # 记录保存文件的执行情况
        self.save_done = set()
        
    def getdata(self, instrument, lookback=False):
        self.ins = instrument

        # 设置开盘时间和收盘时间
        sessionstart = datetime.time(21, 00, 00)
        sessionend = datetime.time(15, 00, 00)
        return Mydatafeed_v2(dataname=instrument, store=self, lookback=lookback, sessionstart=sessionstart, sessionend=sessionend)
    
    def getdata_v2(self, instrument, lookback=None):
        self.ins = instrument
        sessionstart = datetime.time(21, 00, 00)
        sessionend = datetime.time(15, 00, 00)
        return TickDataFeed(dataname=instrument, store=self, lookback=lookback, sessionstart=sessionstart, sessionend=sessionend)
    
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
        minute_key = now.strftime("%H:%M")  # 例如 "09:00"
        
        # ✅ 每天 21:20 清空重连记录
        if now.hour == 21 and now.minute == 20:
            if "21:20" not in self._reconnect_done:
                self._reconnect_done.clear()
                self._reconnect_done.add("21:20")
            return None

        # ✅ 如果这一分钟已经重连过，就跳过
        if minute_key in self._reconnect_done:
            return None
        
        # 早盘重连
        if now.hour == 9 and now.minute == 0:
            print(f"{now} 早盘固定时点重连")
            self._reconnect()
            self._reconnect_done.add(minute_key)
            return None
        
        # 下午重连
        if now.hour == 13 and now.minute == 30:
            print(f"{now} 下午固定时点重连")
            self._reconnect()
            self._reconnect_done.add(minute_key)
            return None
        
        # 夜盘重连
        if now.hour == 21 and now.minute == 0:
            print(f"{now} 夜盘固定时点重连")
            self._reconnect()
            self._reconnect_done.add(minute_key)
            return None
        
        return True
    
    def _save_csv(self, save_type):
        """
        保存的文件类型
        可选: trade、order、position、account
        """
        if save_type == 'trade':
            data = pd.DataFrame([dict(i) for i in self.tianqin.get_trade().values()])
            if len(data) == 0:
                return
            data['trade_date_time'] = data['trade_date_time'].apply(lambda x: datetime.datetime.fromtimestamp(x / 10**9).strftime('%Y-%m-%d %H:%M:%S'))
        elif save_type == 'order':
            data = pd.DataFrame([dict(i) for i in self.tianqin.get_order().values()])
            if len(data) == 0:
                return
            data['insert_date_time'] = data['insert_date_time'].apply(lambda x: datetime.datetime.fromtimestamp(x / 10**9).strftime('%Y-%m-%d %H:%M:%S'))
        elif save_type == 'position':
            data = pd.DataFrame([dict(i) for i in self.tianqin.get_position().values()])
            if len(data) == 0:
                return
            data['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        elif save_type == 'account':
            data = pd.DataFrame([{k: v for k, v in zip(list(self.tianqin.get_account().keys()), list(self.tianqin.get_account().values()))}])
            if len(data) == 0:
                return
            data['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        else:
            raise ValueError('参数save_type选项只能选择trade、order、position、account')
        
        file_path = os.path.join(self.save_path, save_type + '.csv')
        if not os.path.exists(file_path):
            data.to_csv(file_path, index=False)

        else:
            d = pd.read_csv(file_path)
            d = pd.concat([d, data], axis=0).reset_index(drop=True)
            if save_type == 'order':
                d = d.drop_duplicates(subset=['order_id'], keep='last')
            elif save_type == 'position':
                d = d.drop_duplicates(subset=['instrument_id'], keep='last')
            elif save_type == 'trade':
                d = d.drop_duplicates(keep='last')
            elif save_type == 'account':
                d = d = d.drop_duplicates(subset=['date'], keep='last')
            d.to_csv(file_path, index=False)

    def save(self):
        # 获取该品种最后时刻
        sessions = CLASS_SESSIONS.get(self.ins.split('.')[-1][:2].upper())
        final_time = sessions[-1][-1]
        final_time = datetime.datetime.strptime(final_time, "%H:%M")
        start_time = datetime.datetime.strptime(sessions[-1][0], "%H:%M")
        clear_time = start_time + datetime.timedelta(minutes=1)

        now = datetime.datetime.now()
        minute_key = now.strftime("%H:%M")  # 例如 "09:00"

        if now.hour == clear_time.hour and now.minute == clear_time.minute and minute_key not in self.save_done:
            self.save_done.clear()
            self.save_done.add(minute_key)
            return None

        # 下午保存
        if now.hour == 14 and now.minute == 59 and minute_key not in self.save_done:
            print(f"{now} 交易记录保存")
            self._save_csv('order')
            self._save_csv('trade')
            self._save_csv('position')
            self._save_csv('account')
            self.save_done.add(minute_key)
            return None
        
        # 凌晨保存
        if now.hour == final_time.hour and now.minute == final_time.minute - 1 and minute_key not in self.save_done:
            print(f"{now} 交易记录保存")
            self._save_csv('order')
            self._save_csv('trade')
            self._save_csv('position')
            self._save_csv('account')
            self.save_done.add(minute_key)
            return None
        