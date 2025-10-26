# 天勤量化 x Backtrader 实盘接入

将天勤量化行情/账户对接到 Backtrader，支持以 Backtrader 策略框架进行实盘运行与分钟级数据合成。

- 技术栈：Backtrader + TqSdk（TqApi/TqKq/TqAuth）
- 目录结构：
  - tianqin_backtrader/
    - store.py：账户与行情连接管理（TqApi 会话、智能重连机制、数据入口）
    - datafeed.py：基于盘口 tick 合成分钟线的数据源，实现 Backtrader DataBase
    - broker.py：完整交易执行系统（支持四向交易、智能平仓、持仓管理）
    - session_calendar.py：交易时间判断工具（支持多品种、日夜盘识别）
    - __init__.py：对外导出
    - performance_tracker.py：交易绩效记录管理器（自动保存交易数据）
  - test.py：调试样例（支持多空双向交易）
  - test.ipynb：Jupyter 笔记本测试文件
  - figure/：项目相关图片资源

## 快速开始

### 环境准备
安装python>=3.12, 使用pip命令安装相关库

```bash
pip install backtrader tqsdk
```

### 配置账户
在 `test.py` 中设置您的天勤账户信息：
```python
store = MyStore(key='您的天勤账号', value='您的天勤密码')
```

### 运行策略

```bash
python test.py
```

### Jupyter 测试

```bash
jupyter notebook test.ipynb
```

### 系统架构

1. **连接管理**：`MyStore` 建立与天勤的稳定连接，提供智能重连机制
2. **数据流**：`Mydatafeed` 实时监听 tick 数据，按分钟合成 OHLCV + 买卖价
3. **交易执行**：`MyBroker` 提供完整的四向交易功能与持仓管理
4. **策略框架**：标准 Backtrader 策略，支持复杂交易逻辑

### 核心特性

- ✅ **实盘级稳定性**：多重重连机制，确保交易连续性
- ✅ **完整交易功能**：开多、开空、平多、平空，支持今昨仓分离
- ✅ **智能时间管理**：自动识别交易时段，支持多品种
- ✅ **实时数据流**：tick 级数据转分钟 K 线，包含买卖价信息
- ✅ **灵活策略开发**：标准 Backtrader 策略框架，易于扩展
- ✅ **历史数据加载**：实盘过程中自动加载历史数据，支持策略初始化
- ✅ **成交记录保存**：自动保存所有成交记录，支持交易数据持久化

## 实盘特性

### 数据流特性
- **实时行情**：使用 TqKq 通道 + `wait_update` 拉取最新 tick 数据
- **分钟合成**：按分钟变更自动合成 K 线（OHLCV + 买卖价 + 持仓量）
- **日线聚合**：新增`Dailyfeed`支持夜盘21:00到次日15:00的K线聚合，符合期货市场交易习惯
- **买卖价数据**：实时提供 bid/ask 价格，支持高频策略
- **多品种支持**：支持商品期货、金融期货等多品种交易
- **历史数据加载**：实盘启动时自动加载最近一个月历史数据，用于策略初始化和技术指标计算
- **数据筛选优化**：历史数据自动筛选从21:00夜盘开始的数据，确保数据完整性

### 历史数据管理
- **自动加载**：实盘启动时自动加载历史K线数据（默认最近10000分钟）
- **阶段识别**：内置`history_phase`属性标识当前数据阶段（历史数据/实盘数据）
- **策略控制**：策略可通过判断`datafeed.history_phase`来跳过历史数据阶段，避免在历史数据上产生交易信号
- **无缝切换**：历史数据加载完成后自动切换到实盘数据流，确保交易连续性

### 连接与重连
- **智能重连**：
  - 固定时点重连：9:00、13:30、21:00 定时重建会话
  - 异常重连：交易时段内连接异常时自动重连
  - 每日重置：21:20 自动清空重连记录，优化夜盘交易体验
- **交易时间识别**：智能判断日盘/夜盘交易时段
- **假期识别**：结合网络日历判断交易日与假期

### 交易执行
- **四向交易**：完整支持开多、开空、平多、平空
- **智能平仓**：遵循先平今再平昨的规则，自动处理持仓分离
- **实时持仓**：提供详细的持仓信息查询（多仓、空仓、今仓、昨仓）
- **资金管理**：实时获取账户可用资金与总资金
- **订单管理**：支持订单查询与状态跟踪
- **成交记录**：自动保存所有成交记录，支持交易数据分析和回查
- **数据持久化**：新增CSV文件保存功能，自动记录交易、订单、持仓和账户数据

## 当前进度

✅ **已完成**
- **天勤连接（MyStore）**：完整的连接管理与重连机制
- **实时行情到 Backtrader 的 DataFeed 打通（Mydatafeed）**：支持 tick 数据转分钟 K 线
- **Broker 代理商功能完善**：
  - 完整的持仓管理（多仓/空仓，今仓/昨仓分离）
  - 四向交易功能：开多、开空、平多、平空
  - 智能平仓逻辑（先平今再平昨）
  - 资金账户管理（可用资金、总资金查询）
- **分钟级 K 线合成与推送**：实时 OHLCV + 买卖价数据
- **日线聚合功能**：新增`Dailyfeed`支持夜盘21:00到次日15:00的K线聚合
- **交易时间管理系统**：支持多品种交易时段识别
- **智能重连机制**：定时重连（9:00、13:30、21:00）+ 异常重连，优化夜盘重连时间
- **实盘示例策略**：双均线策略完整可运行
- **历史数据加载**：实盘启动时自动加载历史数据，支持技术指标初始化
- **历史数据阶段控制**：策略可识别并跳过历史数据阶段，避免历史数据触发交易信号
- **成交记录保存**：自动保存所有成交记录，支持交易数据持久化和后续分析
- **CSV数据持久化**：新增交易数据自动保存功能，包括订单、持仓、账户等信息

🔄 **进行中**
- 数据持久化与本地行情落盘
- 移仓换月功能开发
- 策略性能优化

📋 **待办**
- 日志与监控系统完善
- 更多策略示例与文档
- 异常处理与容错机制增强
- 性能优化与稳定性提升

## 使用示例

参考（双均线示例）：

```python
import backtrader as bt
from tianqin_backtrader.store import MyStore

# 简单双均线策略示例（支持多空双向交易）
# 逻辑：
# - 计算短期与长期移动均线
# - 短均线上穿长均线 -> 产生开多信号
# - 短均线下穿长均线 -> 产生开空信号
# - 反向信号出现时平仓并开反向仓位
class DualMovingAverage(bt.Strategy):
    params = dict(fast=5, slow=20, datafeed=None)

    def __init__(self):
        # 使用收盘价作为计算源
        self.dataclose = self.datas[0].close
        # 定义移动均线指标
        self.sma_fast = bt.ind.SMA(self.dataclose, period=self.p.fast)
        self.sma_slow = bt.ind.SMA(self.dataclose, period=self.p.slow)
        # 交叉指标：>0 上穿，<0 下穿，=0 持平
        self.crossover = bt.ind.CrossOver(self.sma_fast, self.sma_slow)

    def next(self):
        # 跳过历史数据阶段，避免在历史数据上产生交易信号
        if self.p.datafeed and self.p.datafeed.history_phase:
            return
            
        # 当前K线时间
        dt = self.datas[0].datetime.datetime(0)
        # 获取持仓信息
        pos = self.broker.get_account_position(self.data0._name)
        
        # 上穿信号 - 开多或平空开多
        if self.crossover > 0:
            if pos and pos.get('pos_short', 0) > 0:  # 有空仓，先平空
                print(f"[{dt}] 平空信号: close={self.dataclose[0]:.2f}")
                self.broker.buy_close(self.data0._name, pos['pos_short'], self.dataclose[0])
            print(f"[{dt}] 平空开多: close={self.dataclose[0]:.2f}")
            self.broker.buy_open(self.data0._name, 1, self.data0.ask_price[0])
            
        # 下穿信号 - 开空或平多开空
        elif self.crossover < 0:
            if pos and pos.get('pos_long', 0) > 0:  # 有多仓，先平多
                print(f"[{dt}] 平多信号: close={self.dataclose[0]:.2f}")
                self.broker.sell_close(self.data0._name, pos['pos_long'], self.dataclose[0])
            print(f"[{dt}] 平多开空: close={self.dataclose[0]:.2f}")
            self.broker.sell_open(self.data0._name, 1, self.bid_price[0])

# 创建引擎
cerebro = bt.Cerebro()
# 连接天勤（请在 MyStore 中配置您的登录信息）
store = MyStore(key='xxxxxx', value='xxxxxxx')
# 设置经纪商
broker = store.getbroker()
cerebro.setbroker(broker)
# 订阅合约（示例：上期所铜主力，请按需修改）
# 分钟线数据
data = store.getdata(instrument='SHFE.cu2512', lookback=True)  # lookback=True启用历史数据加载
# 日线数据（夜盘21:00到次日15:00聚合）
# daily_data = store.get_daily_data(instrument='SHFE.cu2512', lookback=True)
# 加载数据与策略
cerebro.adddata(data)
cerebro.addstrategy(DualMovingAverage, datafeed=data)  # 传入datafeed供策略判断历史数据阶段
# 运行
cerebro.run()
```

## 注意事项

- **账号配置**：账号 key/value 需替换为你自己的天勤账号信息
- **风险控制**：实盘前请在仿真环境充分验证，本项目仅做接入示例
- **网络容错**：已内置重连机制，但建议增加自定义的容错与重试逻辑
- **交易时段**：系统会自动判断交易时间，非交易时段策略不会执行交易
- **持仓管理**：支持今仓/昨仓分离，平仓时遵循先平今再平昨的规则
- **数据质量**：基于 tick 数据合成分钟线，确保网络稳定以获得完整数据

## 历史数据管理特性

- **自动历史数据加载**：实盘启动时自动加载最近10000分钟的历史K线数据
- **阶段识别机制**：datafeed内置`history_phase`属性，明确标识当前处于历史数据阶段还是实盘阶段  
- **策略级控制**：策略可通过判断`datafeed.history_phase`来跳过历史数据阶段，避免在历史数据上误触发交易信号
- **无缝切换**：历史数据加载完成后自动切换到实盘数据流，确保交易连续性
- **透明化处理**：用户策略只需简单判断即可实现历史数据阶段跳过，无需复杂处理

## 新增特性

- **双向交易**：完整支持开多、开空、平多、平空四向操作
- **智能平仓**：自动处理今昨仓分离，遵循交易所平仓规则
- **实时持仓**：提供详细的持仓查询，包括多仓、空仓、今仓、昨仓
- **资金查询**：实时获取账户可用资金与总资金
- **买卖价数据**：在 K 线数据中包含实时买卖价信息
- **交易时段管理**：支持多品种交易时段自动识别
- **异常处理**：完善的连接异常处理与自动重连机制
- **历史数据管理**：实盘启动时自动加载历史数据，支持策略初始化
- **阶段识别控制**：内置历史数据阶段识别，策略可跳过历史数据避免误交易
- **成交记录管理**：自动保存所有成交记录，支持交易数据持久化和回查分析
- **日线聚合功能**：新增`Dailyfeed`支持夜盘21:00到次日15:00的K线聚合，符合期货市场交易习惯
- **CSV数据持久化**：新增交易数据自动保存功能，包括订单、持仓、账户等信息
- **夜盘重连优化**：重连时间从00:00优化到21:20，更好适应夜盘交易时间
