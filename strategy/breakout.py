import backtrader as bt
from tianqin_backtrader.store import MyStore

"""
有胆你就来, 赔率1赔7, 胜率16%, 他确实帮我翻了六倍, 但是会体验到先砍掉你一般的资金, 然后急速拉上去的感觉
胜率低到和du博很类似了, 很看命……
"""

class Donchain_index(bt.Indicator):
    params = (
        ("period", 10), 
    )
    lines = (
        "hig", 
        "low", 
        "avg", 
    )
    def __init__(self):
        self.addminperiod(self.params.period + 1)

    def next(self):
        self.lines.hig[0] = max(self.data.high.get(-1, self.params.period))
        self.lines.low[0] = min(self.data.low.get(-1, self.params.period))
        self.lines.avg[0] = sum(self.data.close.get(-1, self.params.period)) / self.params.period

class Donchain(bt.Strategy):
    params = (
        ("TR", 2),
        ("donchain_period", 15), 
        ("trend_period", 100), 
        ("datafeed", None), 
    )
    def __init__(self):
        self.donchain = Donchain_index(self.data1, period=self.params.donchain_period)    # 先上分钟的唐奇安
        self.ma = bt.indicators.SMA(self.data1, period=self.params.trend_period)

        self.LowerAfterEntry = None
        self.HigherAfterEntry = None
    
    def next(self):
        if self.p.datafeed.history_phase:
        # 跳过回放数据阶段, 以免使用历史数据下单(必须存在, 可以不需要更改)
            return
        
        # 获取当前时间
        current_time = self.data.datetime.time()
        current_datetime = self.data.datetime.datetime()

        # 订单管理
        # orders = self.broker.get_all_orders()
        # orders_ids = list(orders.keys())
        # for order in orders_ids:
        #     if orders[order].get('status', None) == "ALIVE":
        #         self.broker.cancel_order(order)
        
        # 获取持仓
        pos = self.broker.get_account_position(self.data0._name)
        long_pos = pos.get('pos_long', 0)
        short_pos = pos.get("pos_short", 0)
        pos = long_pos + short_pos

        # 移动止盈止损
        # 记录多头最低价和空头最高价
        if long_pos > 0:
            self.LowerAfterEntry = self.data1.low[0] if self.LowerAfterEntry is None else max(self.LowerAfterEntry, self.data1.low[0])
        
        elif short_pos > 0:
            self.HigherAfterEntry = self.data1.high[0] if self.HigherAfterEntry is None else min(self.HigherAfterEntry, self.data1.high[0])
        else:
            self.LowerAfterEntry = None
            self.HigherAfterEntry = None

        if long_pos > 0:
            Myprice = self.LowerAfterEntry - self.data1.open[0] * self.p.TR / 100
            print(current_datetime, '多头止损点位: ', Myprice, '当前价格: ', self.data0.close[0])
            if self.data0.close[0] <= Myprice:
                self.broker.sell_close(self.data0._name, size=long_pos, limit_price=self.data1.low[0]-50)
                print(current_datetime, "多头跟踪止损")
                return

        if short_pos < 0:
            Myprice2 = self.HigherAfterEntry + self.data1.open[0] * self.p.TR / 100
            print(current_datetime, '空头止损点位: ', Myprice2, '当前价格: ', self.data0.close[0])
            if self.data0.close[0] >= Myprice2:
                self.broker.buy_close(self.data0._name, size=short_pos, limit_price=self.data1.high[0]+50)
                print(current_datetime, "空头跟踪止损")
                return


        # 开仓
        if pos == 0:
            if self.data0.close[0] > self.donchain.hig[0] and self.data0.close[0] > self.ma.sma[0]:
                print(current_datetime, "开多")
                self.broker.buy_open(self.data0._name, size=1, limit_price=self.data1.high[0] + 50)
            
            elif self.data0.close[0] < self.donchain.low[0] and self.data0.close[0] < self.ma.sma[0]:
                print(current_datetime, "开空")
                self.broker.sell_open(self.data0._name, size=1, limit_price=self.data1.low[0]-50)

# 创建引擎
cerebro = bt.Cerebro()
# 连接天勤（请在 MyStore 中配置您的登录信息）
store = MyStore(key='x6504368', value='q6504368', strategy_name='布林带')
# 订阅合约分钟（示例：上期所铜主力，请按需修改）
data = store.getdata_v2(instrument='SHFE.rb2601', lookback=True)
# 加载经济商
broker = store.getbroker()
cerebro.setbroker(broker)
# 加载数据与策略
cerebro.adddata(data)
cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes)
cerebro.addstrategy(Donchain, datafeed=data)
# 运行
cerebro.run()