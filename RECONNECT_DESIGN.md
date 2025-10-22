# 天勤 backtrader 重连与交易时段设计方案

- 目标
  - 在 store 中实现稳健的重连机制
  - datafeed 在 _load 中仅在交易时段内合成分钟K，非交易时段返回 None
  - 处理盘中断线、开盘/夜盘切换、收盘后无数据等

- 交易时段建模
  - 使用“合约品种/交易所 -> 日内交易时段段列表”的映射
  - 参考 figure/期货时间.jpg，总结常见时段：
    - 日盘：09:00-10:15, 10:30-11:30, 13:30-15:00（示例）
    - 夜盘：21:00-23:00 或 21:00-23:30 或 21:00-02:30 等（品种不同）
  - 夜盘跨天：结束时间可能次日，需规范化到 datetime 区间（跨天加1天）
  - API：is_trading_now(symbol, now) -> bool；next_session_boundary(symbol, now) -> datetime

- store 重连策略
  - 触发条件
    - wait_update 超时
    - 主动检测到不在交易时段且长时间无数据
    - 开盘边界到来前/后短暂重连
  - 策略
    - 指数退避重试：1s, 2s, 4s... 上限比如 30s；最多 N 次后延长休眠至下一个交易时段
    - 盘中：快速重试，失败则重建 TqApi
    - 非交易时段：不持续重试，等待 next_session_boundary - now
  - 关键点
    - 重连前安全关闭 self.tianqin.close()
    - 重连后刷新订阅（如需要）
    - 记录最后一次成功心跳时间，用于判断“假活”连接
    - 在 __del__/stop 中优雅关闭

- datafeed 行为（_load）
  - 若 not is_trading_now(dataname, now)：return None
  - 在交易时段：
    - 通过 store.tianqin.get_quote + wait_update(deadline=now+10s)
    - 超时：return None（并让 store 的后台/上层按策略处理重连）
    - 组装分钟K：分钟切换时输出一根bar并清空缓存；否则累计tick返回 None
  - 考虑开盘首分钟：先缓存首个tick，等分钟跳变再输出
  - 收盘最后一分钟：可在离场边界时强制 flush 最后分钟（可选）

- 状态与日志
  - store 维护：
    - last_ok_ts：最后成功 wait_update 的时间
    - backoff_secs：当前退避秒
  - 日志级别建议：INFO（连接/重连/会话切换）、WARN（超时）、ERROR（重连失败）
  - 统计：当日重连次数，最后一次错误

- 示例代码（示意，不改动现有文件）

```python
# session_calendar.py (示意)
import datetime as dt

CLASS_SESSIONS = {
    # 示例：品种大类 -> [("09:00","10:15"),("10:30","11:30"),("13:30","15:00"),("21:00","23:00")]
    "RB": [("09:00","10:15"),("10:30","11:30"),("13:30","15:00"),("21:00","23:00")],
    "AU": [("09:00","10:15"),("10:30","11:30"),("13:30","15:00"),("21:00","02:30")],
}

def _parse_hm(hm):
    h,m = map(int, hm.split(":"))
    return h,m

def resolve_intervals(symbol, now):
    cls = symbol[:2].upper()
    spans = CLASS_SESSIONS.get(cls, [])
    date = now.date()
    out = []
    for s,e in spans:
        sh,sm = _parse_hm(s); eh,em = _parse_hm(e)
        start = dt.datetime.combine(date, dt.time(sh,sm))
        end = dt.datetime.combine(date, dt.time(eh,em))
        if end <= start:
            end += dt.timedelta(days=1)
        out.append((start, end))
    return out

def is_trading_now(symbol, now=None):
    now = now or dt.datetime.now()
    for s,e in resolve_intervals(symbol, now):
        if s <= now < e:
            return True
    return False

def next_session_boundary(symbol, now=None):
    now = now or dt.datetime.now()
    bounds = []
    for s,e in resolve_intervals(symbol, now):
        bounds += [s,e]
    later = [b for b in bounds if b > now]
    return min(later) if later else resolve_intervals(symbol, now+dt.timedelta(days=1))[0][0]
```

```python
# store_reconnect.py (示意)
import time, datetime as dt
from tqsdk import TqApi, TqKq, TqAuth

class Reconnector:
    def __init__(self, key, value):
        self.key = key; self.value = value
        self.api = None
        self.backoff = 1
        self.last_ok = None

    def connect(self):
        if self.api:
            try: self.api.close()
            except: pass
        self.api = TqApi(TqKq(), auth=TqAuth(self.key, self.value))
        self.backoff = 1
        self.last_ok = dt.datetime.now()

    def wait(self, deadline):
        ok = self.api.wait_update(deadline=deadline)
        if ok:
            self.last_ok = dt.datetime.now()
            self.backoff = 1
        return ok

    def on_timeout(self):
        time.sleep(self.backoff)
        self.backoff = min(self.backoff*2, 30)
        self.connect()

    def healthy(self, max_idle=30):
        if not self.last_ok: return False
        return (dt.datetime.now() - self.last_ok).total_seconds() <= max_idle
```

```python
# store.py 集成片段（示意）
from .session_calendar import is_trading_now, next_session_boundary
from .store_reconnect import Reconnector
import time, datetime

class MyStore:
    def __init__(self, key, value):
        self.key = key; self.value = value
        self.rc = Reconnector(key, value)
        self.rc.connect()

    def retry(self, symbol):
        now = datetime.datetime.now()
        if is_trading_now(symbol, now):
            ok = self.rc.wait(deadline=time.time()+5)
            if not ok:
                self.rc.on_timeout()
        else:
            boundary = next_session_boundary(symbol, now)
            sleep_s = max(0, (boundary - now).total_seconds())
            time.sleep(min(sleep_s, 60))
            self.rc.connect()

    @property
    def tianqin(self):
        return self.rc.api
```

```python
# datafeed.py 集成片段（示意）
import datetime, time
from .session_calendar import is_trading_now

def _load(self):
    now = datetime.datetime.now()
    if not is_trading_now(self.p.dataname, now):
        return None
    tick = self.p.store.tianqin.get_quote(self.p.dataname)
    ok = self.p.store.tianqin.wait_update(deadline=time.time()+10)
    if not ok:
        return None
    # 分钟切换时输出bar；否则累计tick
```

- 边界与细节
  - 夜盘跨日：next_session_boundary 处理+1天
  - 夏令时/节假日：后续可接入交易所日历；暂用工作日+时段近似
  - 多合约：为每个 symbol 选择对应时段模板
  - 防抖：避免一分钟内重复重连

- 后续可扩展
  - 从配置文件加载各品种时段
  - 记录数据落盘（datafeed TODO）
  - 在 Cerebro 外层定时调用 store.retry()
