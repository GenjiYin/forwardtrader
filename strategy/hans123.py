import backtrader as bt
import datetime
from tianqin_backtrader.store import MyStore
import time

# hans123策略实盘

"""
注意事项: 
1. 铜开一手很贵, 非常贵, 请谨慎使用
2. 平今仓的手续费很高: 每手6块钱的最低费用, 外加万分之一的手续费
3. 不建议周五的时候开启程序, 周五夜盘直到凌晨, 平时铜夜盘是三点, 意味着可能留仓位在手上, 隔夜风险极大(贵金属就是这样的, 没办法)
4. 行情推送速度极快, 不建议手动干预下单过程
总结: 量力而行, 样例仅供参考, 盈亏自负
"""

class hans123(bt.Strategy):
    params = (
        ("N", 15), 
        ("TR", 0.6),
        ("close_all_minute", 8)
    )
    def __init__(self):
        self.state = None
        self.upper = None
        self.lower = None

        self.order_num = 0

        self.upper = None
        self.lower = None

        self.LowerAfterEntry = None
        self.HigherAfterEntry = None

        # 一天只做两手, 输了我认了
        self.total_open_num = 2
        self.counter = 0

    def next(self):
        if self.p.datafeed.history_phase:
        # 跳过回放数据阶段, 以免使用历史数据下单(必须存在, 可以不需要更改)
            return
        
        # 获取当前时间
        current_time = self.data.datetime.time(0)
        current_datetime = self.data.datetime.datetime()

        # 订单管理
        orders = self.broker.get_all_orders()
        orders_ids = list(orders.keys())
        for order in orders_ids:
            if orders[order].get('status', None) == "ALIVE":
                self.broker.cancel_order(order)

        # 只允许一个方向的持仓出现
        pos = self.broker.get_account_position(self.data0._name)
        long_pos = pos.get('pos_long', 0)
        short_pos = pos.get("pos_short", 0)
        pos = long_pos + short_pos

        # 盘前
        if (current_time >= datetime.time(9, 0) and current_time <= datetime.time(9, self.params.N)) or (current_time >= datetime.time(21, 0) and current_time <= datetime.time(21, self.params.N)):
            self.upper = self.data1.high[0] if self.upper is None else max(self.data1.high[0], self.upper)
            self.lower = self.data1.low[0] if self.lower is None else min(self.data1.low[0], self.lower)
            return

        # 尾盘平仓
        if (current_time >= datetime.time(14, 60-self.params.close_all_minute) and current_time <= datetime.time(15, 0)) or (current_time >= datetime.time(2, 60-self.params.close_all_minute) and current_time <= datetime.time(3, 0)):
            self.upper = None
            self.lower = None
            self.counter = 0
            if pos>0:
                self.sell(size=pos)
                print(current_datetime, '尾盘平多')

            elif pos < 0:
                self.buy(size=abs(pos))
                print(current_datetime, '尾盘平空')
            return
        
        # 盘中
        if self.counter <= self.total_open_num:
            if pos == 0:
                if self.data1.high[0] > self.upper and self.data1.open[0] < self.upper:
                    self.broker.buy_open(self.data0._name, size=3, limit_price=self.data1.high[0])
                    print(current_datetime, '开多')
                    self.counter += 1
                    return
                
                elif self.data1.low[0] < self.lower and self.data1.open[0] > self.lower:
                    self.broker.sell_open(self.data0._name, size=3, limit_price=self.data1.low[0])
                    print(current_datetime, "开空")
                    self.counter += 1
                    return
    
        # 移动止损
        # 记录多头最低价和空头最高价
        if self.position.size > 0:
            self.LowerAfterEntry = self.data1.low[0] if self.LowerAfterEntry is None else max(self.LowerAfterEntry, self.data1.low[0])
        
        elif self.position.size < 0:
            self.HigherAfterEntry = self.data1.high[0] if self.HigherAfterEntry is None else min(self.HigherAfterEntry, self.data1.high[0])
        else:
            self.LowerAfterEntry = None
            self.HigherAfterEntry = None
            
        if self.position.size > 0:
            Myprice = self.LowerAfterEntry - self.data1.open[0] * self.p.TR / 100
            if self.data1.low[0] <= Myprice:
                self.sell_close(self.data0._name, size=3, limit_price=self.data1.low[0])
                print(current_datetime, "多头跟踪止损")
                return

        if self.position.size < 0:
            Myprice2 = self.HigherAfterEntry + self.data1.open[0] * self.p.TR / 100
            if self.data1.high[0] >= Myprice2:
                self.buy_close(self.data0._name, size=3, limit_price=self.data1.high[0])
                print(current_datetime, "空头跟踪止损")
                return

        
# 创建引擎
cerebro = bt.Cerebro()
# 连接天勤（请在 MyStore 中配置您的登录信息）
store = MyStore(key='xxxxxxxxxxx', value='xxxxxxxxxxxxx', strategy_name='Hans123策略')
# 订阅合约分钟（示例：上期所铜主力，请按需修改）
data = store.getdata_v2(instrument='SHFE.cu2512', lookback=True)
# 加载经济商
broker = store.getbroker()
cerebro.setbroker(broker)
# 加载数据与策略
cerebro.adddata(data)
cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes)
cerebro.addstrategy(hans123, datafeed=data)
# 运行
cerebro.run()