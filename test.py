import backtrader as bt
from tianqin_backtrader.store import MyStore

# 简单双均线策略示例
# 逻辑：
# - 计算短期与长期移动均线
# - 短均线上穿长均线 -> 产生买入信号
# - 短均线下穿长均线 -> 产生卖出/平仓信号
class DualMovingAverage(bt.Strategy):
    params = dict(fast=5, slow=20)

    def __init__(self):
        pass

    def next(self):
        # 当前K线时间
        current_time = self.data.datetime.time()
        current_datetime = self.data.datetime.datetime()
        # print(current_datetime, '时刻收盘价: ', self.data0.close[0])
        print(current_datetime, '可用资金: ', self.broker.getcash(), "持仓市值: ", self.broker.getvalue())

# 创建引擎
cerebro = bt.Cerebro()
# 连接天勤（请在 MyStore 中配置您的登录信息）
store = MyStore(key='xxxxx', value='xxxxxx')
# 订阅合约（示例：上期所铜主力，请按需修改）
data = store.getdata(instrument='SHFE.cu2512')
# 加载经济商
broker = store.getbroker()
cerebro.setbroker(broker)
# 加载数据与策略
cerebro.adddata(data)
cerebro.addstrategy(DualMovingAverage)
# 运行
cerebro.run()
