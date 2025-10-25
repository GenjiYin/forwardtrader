import backtrader as bt
import datetime
from tianqin_backtrader.store import MyStore

# 简单双均线策略示例
# 逻辑：
# - 计算短期与长期移动均线
# - 短均线上穿长均线 -> 产生买入信号
# - 短均线下穿长均线 -> 产生卖出/平仓信号
class DualMovingAverage(bt.Strategy):
    params = dict(fast=5, slow=20, datafeed=None)

    def __init__(self):
        self.dataclose = self.datas[0].close

    def next(self):
        if self.p.datafeed.history_phase:
            # 跳过回放数据阶段, 以免使用历史数据下单(必须存在, 可以不需要更改)
            return

        # 当前K线时间
        current_time = self.data.datetime.time()
        current_datetime = self.data.datetime.datetime()
        # print(current_datetime, '时刻bidprice: ', self.data0.bid_price[0])
        # pos = self.broker.get_account_position(self.data0._name)
        # print(current_datetime, '可用资金: ', self.broker.getcash(), "总资金: ", self.broker.getvalue())
        # print(self.data0._name, " 持仓: ", pos)

        pos = self.broker.get_account_position(self.data0._name)
        print(current_datetime, self.p.fast)

        # if len(pos) == 0:
        #     # 空仓时开空一手
        #     print(current_datetime, '开空')
        #     orders = self.broker.sell_open(self.data0._name, 1, self.data0.ask_price[0])
        # else:
        #     # 多仓时平空一手
        #     print(current_datetime, '平空')
        #     orders = self.broker.buy_close(self.data0._name, 1, self.data0.bid_price[0])

        

# 创建引擎
cerebro = bt.Cerebro()
# 连接天勤（请在 MyStore 中配置您的登录信息）
store = MyStore(key='xxxxxx', value='xxxxxxx')
# 订阅合约（示例：上期所铜主力，请按需修改）
data = store.getdata(instrument='SHFE.cu2512', lookback=True)
# 加载经济商
broker = store.getbroker()
cerebro.setbroker(broker)
# 加载数据与策略
cerebro.adddata(data)
cerebro.resampledata(data, timeframe=bt.TimeFrame.Days)
cerebro.addstrategy(DualMovingAverage, datafeed=data)
# 运行
cerebro.run()
