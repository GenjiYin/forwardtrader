import backtrader as bt
from tianqin_backtrader.store import MyStore  

class mystrategy(bt.Strategy):
    def __init__(self):
        pass
    
    def next(self):
        pass

cerebro = bt.Cerebro()
store = MyStore()
data = store.getdata(instrument='SHFE.cu2512')
cerebro.adddata(data)
cerebro.addstrategy(mystrategy)
cerebro.run()