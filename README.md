# Tianqin Quantitative x Backtrader Live Trading Integration

<div align="center">
  
[![中文](https://img.shields.io/badge/中文-README__zh.md-red)](README_zh.md)
[![English](https://img.shields.io/badge/English-README.md-green)](README.md)

*[English](README.md) | [中文](README_zh.md)*

</div>

Integrate Tianqin quantitative market data and trading accounts with Backtrader, supporting live trading and minute-level data synthesis using the Backtrader strategy framework.

- Technology Stack: Backtrader + TqSdk (TqApi/TqKq/TqAuth)
- Directory Structure:
  - tianqin_backtrader/
    - store.py: Account and market connection management (TqApi session, intelligent reconnection, data entry)
    - datafeed.py: Tick-based minute bar data source, implements Backtrader DataBase
    - datafeed_v2.py: Next-generation data feed system with precise minute bar synthesis and multi-level bid/ask data
    - broker.py: Complete trading execution system (supports four-way trading, intelligent position closing, position management)
    - session_calendar.py: Trading time judgment tool (supports multiple products, day/night session identification)
    - __init__.py: External exports
    - performance_tracker.py: Trading performance recorder (automatically saves trading data)
  - test.py: Debug example (supports long/short two-way trading)
  - test.ipynb: Jupyter notebook test file
  - figure/: Project related image resources

## Quick Start

### Environment Setup
Install python>=3.12, use pip to install related libraries

```bash
pip install backtrader tqsdk
```

### Account Configuration
Set your Tianqin account information in `test.py`:
```python
store = MyStore(key='your_tianqin_account', value='your_tianqin_password')
```

### Run Strategy

```bash
python test.py
```

### Jupyter Testing

```bash
jupyter notebook test.ipynb
```

### System Architecture

1. **Connection Management**: `MyStore` establishes stable connection with Tianqin, provides intelligent reconnection mechanism
2. **Data Flow**: `Mydatafeed` real-time listens to tick data, synthesizes OHLCV + bid/ask by minute
3. **Trading Execution**: `MyBroker` provides complete four-way trading functionality and position management
4. **Strategy Framework**: Standard Backtrader strategy, supports complex trading logic

### Core Features

- ✅ **Live Trading Stability**: Multiple reconnection mechanisms ensure trading continuity
- ✅ **Complete Trading Functions**: Long open, short open, long close, short close, supports today/yesterday position separation
- ✅ **Intelligent Time Management**: Automatically identifies trading sessions, supports multiple products
- ✅ **Real-time Data Flow**: Tick-level data converted to minute K-lines, includes bid/ask information
- ✅ **Flexible Strategy Development**: Standard Backtrader strategy framework, easy to extend
- ✅ **Historical Data Loading**: Automatically loads historical data during live trading, supports strategy initialization
- ✅ **Trade Record Saving**: Automatically saves all trade records, supports trading data persistence

## Live Trading Features

### Data Flow Features
- **Real-time Market Data**: Uses TqKq channel + `wait_update` to pull latest tick data
- **Minute Synthesis**: Automatically synthesizes K-lines by minute change (OHLCV + bid/ask + open interest)
- **Next-Generation Data Feed System (datafeed_v2)**:
  - **Precise Minute Bar Synthesis**: Accurate minute bar synthesis based on tick data with real OHLCV prices
  - **Multi-level Bid/Ask Data**: Support for bid_price1/ask_price1 and bid_price2/ask_price2 multi-level quotes
  - **Smart Data Caching**: Built-in price series caching to ensure minute bar data integrity and accuracy
  - **Tick-level Data Processing**: Real-time tick data collection with precise OHLCV aggregation by minute
- **Daily Aggregation**: New `Dailyfeed` supports K-line aggregation from night session 21:00 to next day 15:00,符合futures market trading habits
- **Bid/Ask Data**: Real-time provides bid/ask prices, supports high-frequency strategies
- **Multi-product Support**: Supports commodity futures, financial futures and other multi-product trading
- **Historical Data Loading**: Automatically loads recent one month of historical data at live trading startup, for strategy initialization and technical indicator calculation
- **Data Filtering Optimization**: Historical data automatically filters data starting from 21:00 night session, ensures data integrity

### Historical Data Management
- **Automatic Loading**: Automatically loads historical K-line data at live trading startup (default recent 10000 minutes)
- **Phase Identification**: Built-in `history_phase` attribute identifies current data phase (historical data/live data)
- **Strategy Control**: Strategy can skip historical data phase by checking `datafeed.history_phase`, avoids generating trading signals on historical data
- **Seamless Switching**: Automatically switches to live data stream after historical data loading completes, ensures trading continuity

### Connection & Reconnection
- **Intelligent Reconnection**:
  - Fixed time reconnection: 9:00, 13:30, 21:00定时重建会话
  - Exception reconnection: Automatically reconnects when connection异常during trading sessions
  - Daily reset: 21:20 automatically clears reconnection records, optimizes night session trading experience
- **Trading Time Identification**: Intelligently judges day/night trading sessions
- **Holiday Identification**: Combines web calendar to判断trading days and holidays

### Trading Execution
- **Four-way Trading**: Complete support for long open, short open, long close, short close
- **Intelligent Position Closing**: Follows close today then close yesterday rules, automatically handles position separation
- **Real-time Positions**: Provides detailed position information query (long, short, today, yesterday positions)
- **Fund Management**: Real-time获取account available funds and total funds
- **Order Management**: Supports order query and status tracking
- **Trade Records**: Automatically saves all trade records, supports trading data analysis and review
- **Data Persistence**: New CSV file saving function, automatically records trading, order, position and account data

## Current Progress

✅ **Completed**
- **Tianqin Connection (MyStore)**: Complete connection management and reconnection mechanism
- **Real-time Market Data to Backtrader DataFeed Integration (Mydatafeed)**: Supports tick data to minute K-line conversion
- **Next-Generation Data Feed System (datafeed_v2)**:
  - Precise minute bar synthesis and tick-level data processing
  - Multi-level bid/ask data support (bid_price1/ask_price1, bid_price2/ask_price2)
  - Smart data caching and price series management
- **Broker Agent Function完善**:
  - Complete position management (long/short positions, today/yesterday position separation)
  - Four-way trading functions: long open, short open, long close, short close
  - Intelligent position closing logic (close today first, then close yesterday)
  - Fund account management (available funds, total funds query)
- **Minute-level K-line Synthesis and Push**: Real-time OHLCV + bid/ask data
- **Daily Aggregation Function**: New `Dailyfeed` supports K-line aggregation from night session 21:00 to next day 15:00
- **Trading Time Management System**: Supports multi-product trading session identification
- **Intelligent Reconnection Mechanism**: Timed reconnection (9:00, 13:30, 21:00) + exception reconnection, optimizes night session reconnection time
- **Live Trading Example Strategy**: Dual moving average strategy complete and runnable
- **Historical Data Loading**: Automatically loads historical data at live trading startup, supports technical indicator initialization
- **Historical Data Phase Control**: Strategy can identify and skip historical data phase, avoids triggering trading signals on historical data
- **Trade Record Saving**: Automatically saves all trade records, supports trading data persistence and subsequent analysis
- **CSV Data Persistence**: New trading data automatic saving function, including orders, positions, account and other information

🔄 **In Progress**
- Data persistence and local market data storage
- Position transfer and contract rollover function development
- Strategy performance optimization

📋 **Todo**
- Log and monitoring system完善
- More strategy examples and documentation
- Exception handling and fault tolerance mechanism enhancement
- Performance optimization and stability improvement

## Usage Example

Reference (Dual Moving Average Example):

```python
import backtrader as bt
from tianqin_backtrader.store import MyStore

# Simple dual moving average strategy example (supports long/short two-way trading)
# Logic:
# - Calculate short-term and long-term moving averages
# - Short MA crosses above long MA -> generates long open signal
# - Short MA crosses below long MA -> generates short open signal
# - When reverse signal appears, close position and open reverse position
class DualMovingAverage(bt.Strategy):
    params = dict(fast=5, slow=20, datafeed=None)

    def __init__(self):
        # Use closing price as calculation source
        self.dataclose = self.datas[0].close
        # Define moving average indicators
        self.sma_fast = bt.ind.SMA(self.dataclose, period=self.p.fast)
        self.sma_slow = bt.ind.SMA(self.dataclose, period=self.p.slow)
        # Crossover indicator: >0 upward cross, <0 downward cross, =0 flat
        self.crossover = bt.ind.CrossOver(self.sma_fast, self.sma_slow)

    def next(self):
        # Skip historical data phase to avoid generating trading signals on historical data
        if self.p.datafeed and self.p.datafeed.history_phase:
            return
            
        # Current K-line time
        dt = self.datas[0].datetime.datetime(0)
        # Get position information
        pos = self.broker.get_account_position(self.data0._name)
        
        # Upward cross signal - long open or close short then long
        if self.crossover > 0:
            if pos and pos.get('pos_short', 0) > 0:  # Have short position, close short first
                print(f"[{dt}] Close short signal: close={self.dataclose[0]:.2f}")
                self.broker.buy_close(self.data0._name, pos['pos_short'], self.dataclose[0])
            print(f"[{dt}] Close short open long: close={self.dataclose[0]:.2f}")
            self.broker.buy_open(self.data0._name, 1, self.data0.ask_price[0])
            
        # Downward cross signal - short open or close long then short
        elif self.crossover < 0:
            if pos and pos.get('pos_long', 0) > 0:  # Have long position, close long first
                print(f"[{dt}] Close long signal: close={self.dataclose[0]:.2f}")
                self.broker.sell_close(self.data0._name, pos['pos_long'], self.dataclose[0])
            print(f"[{dt}] Close long open short: close={self.dataclose[0]:.2f}")
            self.broker.sell_open(self.data0._name, 1, self.bid_price[0])

# Create engine
cerebro = bt.Cerebro()
# Connect to Tianqin (Please configure your login info in MyStore)
store = MyStore(key='xxxxxx', value='xxxxxxx')
# Set broker
broker = store.getbroker()
cerebro.setbroker(broker)
# Subscribe to contract (Example: SHFE copper main contract, modify as needed)
# Minute line data
data = store.getdata(instrument='SHFE.cu2512', lookback=True)  # lookback=True enables historical data loading
# Daily line data (night session 21:00 to next day 15:00 aggregation)
# daily_data = store.get_daily_data(instrument='SHFE.cu2512', lookback=True)
# Load data and strategy
cerebro.adddata(data)
cerebro.addstrategy(DualMovingAverage, datafeed=data)  # Pass datafeed for strategy to judge historical data phase
# Run
cerebro.run()
```

## Notes

- **Account Configuration**: Account key/value needs to be replaced with your own Tianqin account information
- **Risk Control**: Please fully verify in simulation environment before live trading, this project is only for integration example
- **Network Fault Tolerance**: Reconnection mechanism is built-in, but it is recommended to add custom fault tolerance and retry logic
- **Trading Sessions**: System will automatically judge trading time, strategy will not execute trades during non-trading sessions
- **Position Management**: Supports today/yesterday position separation, follows close today first then close yesterday rule when closing positions
- **Data Quality**: Based on tick data to synthesize minute lines, ensure network stability to get complete data

## Historical Data Management Features

- **Automatic Historical Data Loading**: Automatically loads recent 10000 minutes of historical K-line data when live trading starts
- **Phase Identification Mechanism**: datafeed has built-in `history_phase` attribute that clearly identifies whether current stage is historical data or live data
- **Strategy-level Control**: Strategy can skip historical data stage by checking `datafeed.history_phase`, avoids mistakenly triggering trading signals on historical data
- **Seamless Switching**: Automatically switches to live data stream after historical data loading is complete, ensures trading continuity
- **Transparent Processing**: User strategy only needs simple judgment to achieve historical data stage skipping, no complex processing required

## New Features

- **Two-way Trading**: Complete support for long open, short open, long close, short close four-way operations
- **Intelligent Position Closing**: Automatically handles today/yesterday position separation, follows exchange closing rules
- **Real-time Positions**: Provides detailed position queries, including long, short, today, yesterday positions
- **Fund Query**: Real-time gets account available funds and total funds
- **Bid/Ask Data**: Includes real-time bid/ask information in K-line data
- **Trading Session Management**: Supports automatic identification of multi-product trading sessions
- **Exception Handling**: Complete connection exception handling and automatic reconnection mechanism
- **Historical Data Management**: Automatically loads historical data at live trading startup, supports strategy initialization
- **Phase Identification Control**: Built-in historical data phase identification, strategy can skip historical data to avoid mistaken trading
- **Trade Record Management**: Automatically saves all trade records, supports trading data persistence and review analysis
- **Daily Aggregation Function**: New `Dailyfeed` supports K-line aggregation from night session 21:00 to next day 15:00,符合futures market trading habits
- **CSV Data Persistence**: New trading data automatic saving function, including orders, positions, account and other information
- **Night Session Reconnection Optimization**: Reconnection time optimized from 00:00 to 21:20, better adapts to night session trading time
- **Next-Generation Data Feed System (datafeed_v2)**:
  - **Mydatafeed_v2**: Supports more precise minute bar synthesis
  - **TickDataFeed**: Real-time tick data processing
  - **Multi-level Market Data**: Support for bid_price1/ask_price1 and bid_price2/ask_price2
  - **Smart Caching Mechanism**: Built-in price series caching to ensure data integrity