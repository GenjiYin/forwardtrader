from backtrader.broker import BrokerBase

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
        """
        获取特定标的持仓
        """
        pos = self.p.store.tianqin.get_position(instrument)
        if pos.pos == 0:
            return {}
        return {k: v for k, v in pos.items()}
    
    def get_account_positions(self):
        """获取所有持仓(待优化)"""
        pos = self.p.store.tianqin.get_position()
        ins = list({k: dict(v) for k, v in pos.items()}.keys())
        positions = {}
        for i in ins:
            p = self.get_account_position(i)
            if len(p) == 0:
                continue
            else:
                positions[i] = p
        return positions
    
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
        self.p.store.tianqin.wait_update()
        return [order]
    
    def sell_close(self, instrument:str, size:int, limit_price:float=None):
        """平多(先平今再平昨)"""
        pos = self.get_account_position(instrument)
        if len(pos)==0:
            print("无持仓, 无法多平仓")
            return
        
        if pos['pos_long'] == 0:
            print("无多仓, 无法平仓")
            return
        
        order_1 = None
        order_2 = None
        pos_long_today = pos['pos_long_today']
        pos_long_his = pos['pos_long_his']
        
        # 先平今, 再平昨
        if size <= pos_long_today:
            return [self.p.store.tianqin.insert_order(
                            symbol=instrument, 
                            direction='SELL', 
                            offset='CLOSETODAY', 
                            volume=size, 
                            limit_price=limit_price
                        )]
        else:
            if pos_long_today > 0:
                order_1 = self.p.store.tianqin.insert_order(
                    symbol=instrument, 
                    direction='SELL', 
                    offset='CLOSETODAY', 
                    volume=pos_long_today, 
                    limit_price=limit_price
                )
            order_2 = self.p.store.tianqin.insert_order(
                symbol=instrument, 
                direction='SELL', 
                offset='CLOSE', 
                volume=size if pos_long_his >= size else pos_long_his, 
                limit_price=limit_price
            )
            if order_1 and order_2:
                return [order_1, order_2]
            if order_1 and order_2 is None:
                return [order_1]
            if order_1 is None and order_2:
                return [order_2]

    
    def sell_open(self, instrument:str, size:int, limit_price:float=None):
        """开空"""
        order = self.p.store.tianqin.insert_order(
            symbol=instrument, 
            direction='SELL', 
            offset='OPEN', 
            volume=size, 
            limit_price=limit_price
        )
        self.p.store.tianqin.wait_update()
        return [order]
    
    def buy_close(self, instrument:str, size:int, limit_price:float=None):
        """平空"""
        pos = self.get_account_position(instrument)
        if len(pos)==0:
            print("无持仓, 无法多空仓")
            return
        
        if pos['pos_short'] == 0:
            print("无空仓, 无法平仓")
            return
        
        order_1 = None
        order_2 = None
        pos_short_today = pos['pos_short_today']
        pos_short_his = pos['pos_short_his']
        
        # 先平今, 再平昨
        if size <= pos_short_today:
            return [self.p.store.tianqin.insert_order(
                            symbol=instrument, 
                            direction='BUY', 
                            offset='CLOSETODAY', 
                            volume=size, 
                            limit_price=limit_price
                        )]
        else:
            if pos_short_today > 0:
                order_1 = self.p.store.tianqin.insert_order(
                    symbol=instrument, 
                    direction='BUY', 
                    offset='CLOSETODAY', 
                    volume=pos_short_today, 
                    limit_price=limit_price
                )
            order_2 = self.p.store.tianqin.insert_order(
                symbol=instrument, 
                direction='BUY', 
                offset='CLOSE', 
                volume=size if pos_short_his >= size else pos_short_his, 
                limit_price=limit_price
            )
            if order_1 and order_2:
                return [order_1, order_2]
            if order_1 and order_2 is None:
                return [order_1]
            if order_1 is None and order_2:
                return [order_2]
    
    def memory_cache(self):
        return