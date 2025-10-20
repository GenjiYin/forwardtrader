# 天勤量化 x Backtrader 实盘接入

将天勤量化行情/账户对接到 Backtrader，支持以 Backtrader 策略框架进行实盘运行与分钟级数据合成。

- 技术栈：Backtrader + TqSdk（TqApi/TqKq/TqAuth）
- 目录结构：
  - tianqin_backtrader/
    - store.py：账户与行情连接管理（TqApi 会话、重连机制、数据入口）
    - datafeed.py：基于盘口 tick 合成分钟线的数据源，实现 Backtrader DataBase
    - broker.py：交易执行（占位，待完善）
    - __init__.py：对外导出
  - test.py：最小可运行示例（双均线）
  - 1.ipynb：开发草稿

## 快速开始

- 安装依赖

```bash
pip install backtrader tqsdk
```

- 运行示例
  - 在 test.py 中设置账户 key/value（或使用当前默认）
  - 运行：

```bash
python test.py
```

示例流程：
- MyStore 建立到天勤的连接，并提供 `getdata(symbol)` 返回 Backtrader 数据源
- Mydatafeed 监听 tick，按分钟切分并合成 OHLCV + openinterest/amount，供 Backtrader 驱动
- `cerebro.adddata(data)` + `cerebro.addstrategy(...)` 后直接 `run()`

## 实盘特性

- 实时数据：使用 TqKq 通道 + `wait_update` 拉取最新行情
- 分钟合成：按分钟变更合成一根 K 线（open/high/low/close/volume/openinterest/amount）
- 重连逻辑（基础版）：
  - 9:00、21:00 定时重建会话
  - 交易时段内 `wait_update` 失败时自动重连
- `islive()` 返回 True，适配 Backtrader 实盘流

## 当前进度

- 已完成
  - 天勤连接与鉴权（MyStore）
  - 实时行情到 Backtrader 的 DataFeed 打通（Mydatafeed）
  - 分钟级 K 线合成与推送
  - 最小示例脚本可跑通

- 进行中
  - 断线重连策略细化（时段识别、异常回退、节假日/收盘处理）
  - 历史数据回填/导入
  - 数据持久化与行情落盘

- 待办
  - Broker 下单/撤单通道实现与风控
  - 参数化配置（key/value、订阅合约、频率、时区等）
  - 日志与监控
  - 文档与用法示例完善

## 使用示例

参考 `test.py`（双均线示例）：

```python
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

cerebro = bt.Cerebro()
store = MyStore()
data = store.getdata(instrument='SHFE.cu2512')
cerebro.adddata(data)
cerebro.addstrategy(DualMovingAverage)
cerebro.run()
```

## 注意事项

- 账号 key/value 需替换为你自己的天勤鉴权信息
- 实盘前请在仿真环境充分验证
- 网络中断与交易时段边界需做好容错与重试
- 本项目仅做接入示例，请在生产使用前补齐风控与日志监控
