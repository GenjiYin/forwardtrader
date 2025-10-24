from backtrader.broker import BrokerBase
from backtrader.order import Order, OrderBase
from backtrader.position import Position

class MyBroker(BrokerBase):
    params = (
        ("store", None),
    )
    def __init__(self):
        super(MyBroker, self).__init__()
        pass

    def get_notification(self):
        return None

    def getcash(self):
        """获取可用资金"""
        return self.p.store.tianqin.get_account().available
    
    def getvalue(self):
        """获取总资金"""
        return self.p.store.tianqin.get_account().balance
    
    def get_account_position(self, instrument: str):
        """获取特定标的持仓(待优化)"""
        pos = self.p.store.tianqin.get_position(instrument)
        return {k: v for k, v in pos.items()}
    
    def get_account_positions(self):
        """获取所有持仓(待优化)"""
        pos = self.p.store.tianqin.get_position()
        return {k: dict(v) for k, v in pos.items()}
    
    def get_order(self, order_id):
        return self.p.store.tianqin.get_order(order_id)
    
    def buy_open(self, instrument:str, size:int, limit_price:float=None):
        """开多"""
        order = self.p.store.tianqin.insert_order(
            symbol=instrument, 
            direction='BUY', 
            offset='OPEN', 
            volume=size, 
            limit_price=limit_price
        )
        return order
    
    def sell_close(self, instrument:str, size:int, limit_price:float=None):
        """平多"""
        order = self.p.store.tianqin.insert_order(
            symbol=instrument, 
            direction='SELL', 
            offset='CLOSE', 
            volume=size, 
            limit_price=limit_price
        )
        return order
    
    def sell_open(self, instrument:str, size:int, limit_price:float=None):
        """开空"""
        order = self.p.store.tianqin.insert_order(
            symbol=instrument, 
            direction='SELL', 
            offset='OPEN', 
            volume=size, 
            limit_price=limit_price
        )
        return order
    
    def buy_close(self, instrument:str, size:int, limit_price:float=None):
        """平空"""
        order = self.p.store.tianqin.insert_order(
            symbol=instrument, 
            direction='BUY', 
            offset='CLOSE', 
            volume=size, 
            limit_price=limit_price
        )
        return order
    
    def memory_cache(self):
        return