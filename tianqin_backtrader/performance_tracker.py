import json
import datetime
import os
from typing import Dict, List, Optional

class PerformanceTracker:
    """交易绩效记录管理器"""
    
    def __init__(self, strategy_name: str, data_dir: str = "performance_data", 
                 auto_save_interval: int = 60):
        self.strategy_name = strategy_name
        self.data_dir = data_dir
        self.auto_save_interval = auto_save_interval  # 自动保存间隔（秒）
        self.current_date = datetime.date.today()
        
        # 创建数据目录
        os.makedirs(data_dir, exist_ok=True)
        
        # 当日数据缓存
        self.daily_orders: List[Dict] = []
        self.daily_positions: Dict = {}
        self.daily_account_values: List[Dict] = []
        
        # 自动保存控制
        self.last_auto_save = datetime.datetime.now()
        self.save_counter = 0  # 保存次数计数器
        
        # 加载历史数据
        self._load_daily_data()
    
    def _get_daily_filename(self, date: datetime.date = None) -> str:
        """获取日数据文件名"""
        if date is None:
            date = self.current_date
        return os.path.join(self.data_dir, f"{self.strategy_name}_{date.strftime('%Y%m%d')}.json")
    
    def _load_daily_data(self):
        """加载当日已有数据"""
        filename = self._get_daily_filename()
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.daily_orders = data.get('orders', [])
                    self.daily_positions = data.get('positions', {})
                    self.daily_account_values = data.get('account_values', [])
            except Exception as e:
                print(f"加载日数据失败: {e}")
    
    def _save_daily_data(self):
        """保存当日数据"""
        filename = self._get_daily_filename()
        data = {
            'date': self.current_date.isoformat(),
            'strategy': self.strategy_name,
            'orders': self.daily_orders,
            'positions': self.daily_positions,
            'account_values': self.daily_account_values,
            'summary': self._calculate_daily_summary()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存日数据失败: {e}")
    
    def record_order(self, order_type: str, instrument: str, size: int, 
                    price: float, datetime: datetime.datetime, 
                    order_id: str = None, status: str = "completed"):
        """记录订单"""
        order_record = {
            'timestamp': datetime.isoformat(),
            'type': order_type,
            'instrument': instrument,
            'size': size,
            'price': price,
            'value': abs(size * price),
            'order_id': order_id,
            'status': status
        }
        
        self.daily_orders.append(order_record)
        print(f"📊 记录订单: {order_type} {instrument} {size}手 @ {price}")
        
        # 检查自动保存
        self.check_auto_save()
    
    def record_position(self, instrument: str, position_data: Dict, datetime: datetime.datetime):
        """记录持仓"""
        self.daily_positions[instrument] = {
            'timestamp': datetime.isoformat(),
            'instrument': instrument,
            'pos_long': position_data.get('pos_long', 0),
            'pos_short': position_data.get('pos_short', 0),
            'pos_long_today': position_data.get('pos_long_today', 0),
            'pos_short_today': position_data.get('pos_short_today', 0),
            'pos_long_his': position_data.get('pos_long_his', 0),
            'pos_short_his': position_data.get('pos_short_his', 0),
            'open_price_long': position_data.get('open_price_long', 0),
            'open_price_short': position_data.get('open_price_short', 0),
            'float_profit_long': position_data.get('float_profit_long', 0),
            'float_profit_short': position_data.get('float_profit_short', 0)
        }
        
        # 检查自动保存
        self.check_auto_save()
    
    def record_account_value(self, cash: float, total_value: float, 
                           datetime: datetime.datetime, instrument: str = None):
        """记录账户净值"""
        account_record = {
            'timestamp': datetime.isoformat(),
            'cash': cash,
            'total_value': total_value,
            'net_value': total_value - cash if instrument else total_value,
            'instrument': instrument
        }
        
        self.daily_account_values.append(account_record)
        
        # 限制记录数量，避免数据过大（每5分钟记录一次）
        if len(self.daily_account_values) > 288:  # 24小时 * 12 (5分钟间隔)
            self.daily_account_values = self.daily_account_values[-288:]
        
        # 检查自动保存
        self.check_auto_save()
    
    def _calculate_daily_summary(self) -> Dict:
        """计算日汇总数据"""
        if not self.daily_orders:
            return {'status': 'no_trading'}
        
        # 订单统计
        total_orders = len(self.daily_orders)
        buy_orders = [o for o in self.daily_orders if 'buy' in o['type'].lower()]
        sell_orders = [o for o in self.daily_orders if 'sell' in o['type'].lower()]
        
        # 计算总成交额
        total_turnover = sum(o['value'] for o in self.daily_orders)
        
        # 持仓变化
        net_position_change = sum(
            o['size'] if 'buy' in o['type'].lower() else -o['size'] 
            for o in self.daily_orders
        )
        
        # 账户净值变化
        if len(self.daily_account_values) >= 2:
            initial_value = self.daily_account_values[0]['total_value']
            final_value = self.daily_account_values[-1]['total_value']
            pnl = final_value - initial_value
            pnl_pct = (pnl / initial_value) * 100 if initial_value > 0 else 0
        else:
            pnl = 0
            pnl_pct = 0
        
        return {
            'total_orders': total_orders,
            'buy_orders': len(buy_orders),
            'sell_orders': len(sell_orders),
            'total_turnover': total_turnover,
            'net_position_change': net_position_change,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'latest_cash': self.daily_account_values[-1]['cash'] if self.daily_account_values else 0,
            'latest_total_value': self.daily_account_values[-1]['total_value'] if self.daily_account_values else 0
        }
    
    def get_today_performance(self) -> Dict:
        """获取今日绩效"""
        return {
            'orders': self.daily_orders,
            'positions': self.daily_positions,
            'account_values': self.daily_account_values,
            'summary': self._calculate_daily_summary()
        }
    
    def print_today_summary(self):
        """打印今日汇总"""
        summary = self._calculate_daily_summary()
        
        if summary.get('status') == 'no_trading':
            print("📊 今日无交易")
            return
        
        print(f"\n📊 {self.current_date} 交易汇总")
        print(f"订单总数: {summary['total_orders']} (买: {summary['buy_orders']}, 卖: {summary['sell_orders']})")
        print(f"总成交额: {summary['total_turnover']:,.2f}")
        print(f"净持仓变化: {summary['net_position_change']}")
        print(f"当日盈亏: {summary['pnl']:,.2f} ({summary['pnl_pct']:.2f}%)")
        print(f"当前资金: {summary['latest_cash']:,.2f}")
        print(f"当前总值: {summary['latest_total_value']:,.2f}")
        print("-" * 50)
    
    def switch_to_new_day(self):
        """切换到新的一天"""
        # 打印前一天的汇总
        self.print_today_summary()
        
        # 切换到新日期
        self.current_date = datetime.date.today()
        
        # 重置当日数据
        self.daily_orders = []
        self.daily_positions = {}
        self.daily_account_values = []
        
        # 加载新一天的数据（如果存在）
        self._load_daily_data()
    
    def check_auto_save(self):
        """检查是否需要自动保存"""
        now = datetime.datetime.now()
        if (now - self.last_auto_save).total_seconds() >= self.auto_save_interval:
            self._save_daily_data()
            self.last_auto_save = now
            self.save_counter += 1
            
            # 每10次保存打印一次提示
            if self.save_counter % 10 == 0:
                print(f"📊 自动保存绩效数据 ({self.save_counter}次)")
    
    def check_date_change(self):
        """检查是否到了新的一天"""
        today = datetime.date.today()
        if today != self.current_date:
            self.switch_to_new_day()