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
        # 使用收盘价作为计算源
        self.dataclose = self.datas[0].close
        # 定义移动均线指标
        self.sma_fast = bt.ind.SMA(self.dataclose, period=self.p.fast)
        self.sma_slow = bt.ind.SMA(self.dataclose, period=self.p.slow)
        # 交叉指标：>0 上穿，<0 下穿，=0 持平
        self.crossover = bt.ind.CrossOver(self.sma_fast, self.sma_slow)

    def next(self):
        # 当前K线时间
        dt = self.datas[0].datetime.datetime(0)
        # 无持仓时，出现上穿信号 -> 买入
        if not self.position and self.crossover > 0:
            print(f"[{dt}] 买入信号: close={self.dataclose[0]:.2f}")
            # 如需真实下单，开启：self.buy()
        # 有持仓时，出现下穿信号 -> 平仓
        elif self.position and self.crossover < 0:
            print(f"[{dt}] 卖出/平仓信号: close={self.dataclose[0]:.2f}")
            # 如需真实平仓，开启：self.close()

# 创建引擎
cerebro = bt.Cerebro()
# 连接天勤（请在 MyStore 中配置您的鉴权信息）
store = MyStore()
# 订阅合约（示例：上期所铜主力，请按需修改）
data = store.getdata(instrument='SHFE.cu2512')
# 加载数据与策略
cerebro.adddata(data)
cerebro.addstrategy(DualMovingAverage)
# 运行
cerebro.run()
