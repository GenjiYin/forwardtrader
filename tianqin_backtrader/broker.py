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