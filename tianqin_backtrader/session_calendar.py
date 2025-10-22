import datetime as dt
import requests
from lxml import etree
import datetime

"""
但是这样依旧只能判断交易时间，没法判断交易日, 所以我们要结合wait_update来判断
"""

# 交易时段映射表
CLASS_SESSIONS = {
    "RB": [("09:00", "10:15"), ("10:30", "11:30"), ("13:30", "15:00"), ("21:00", "23:00")],
    "AU": [("09:00", "10:15"), ("10:30", "11:30"), ("13:30", "15:00"), ("21:00", "02:30")],
    "AG": [("09:00", "10:15"), ("10:30", "11:30"), ("13:30", "15:00"), ("21:00", "02:30")],
    "CU": [("09:00", "10:15"), ("10:30", "11:30"), ("13:30", "15:00"), ("21:00", "01:00")],
    "AL": [("09:00", "10:15"), ("10:30", "11:30"), ("13:30", "15:00"), ("21:00", "01:00")],
    "ZN": [("09:00", "10:15"), ("10:30", "11:30"), ("13:30", "15:00"), ("21:00", "01:00")],
    "NI": [("09:00", "10:15"), ("10:30", "11:30"), ("13:30", "15:00"), ("21:00", "01:00")],
    "TA": [("09:00", "10:15"), ("10:30", "11:30"), ("13:30", "15:00"), ("21:00", "23:30")],
    "MA": [("09:00", "10:15"), ("10:30", "11:30"), ("13:30", "15:00"), ("21:00", "23:30")],
    "RU": [("09:00", "10:15"), ("10:30", "11:30"), ("13:30", "15:00"), ("21:00", "23:00")],
    "BU": [("09:00", "10:15"), ("10:30", "11:30"), ("13:30", "15:00"), ("21:00", "23:00")],
    "IF": [("09:30", "11:30"), ("13:00", "15:00")],
    "IH": [("09:30", "11:30"), ("13:00", "15:00")],
    "IC": [("09:30", "11:30"), ("13:00", "15:00")],
}

def is_trading_night():
    # 判断夜盘是否交易
    url = "http://www.gtjaqh.com/pc/calendar"
    params = {"date": (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d").replace('-', '')}
    r = requests.get(url, params=params, verify=True)
    html = etree.HTML(r.text)
    cond0 = True if len(html.xpath('//table'))!=0 else False
    return cond0

def is_trading_daily():
    # 判断日盘是否交易
    url = "http://www.gtjaqh.com/pc/calendar"
    params = {"date": datetime.datetime.now().strftime("%Y-%m-%d").replace('-', '')}
    r = requests.get(url, params=params, verify=True)
    html = etree.HTML(r.text)
    cond0 = True if len(html.xpath('//table'))!=0 else False
    return cond0

def is_trading_time(symbol, current_time=None):
    """
    判断当前时间是否在指定期货品种的交易时间段内。

    :param symbol: 期货品种代码
    :param current_time: 当前时间，默认为None，表示使用当前系统时间
    :return: True如果在交易时间内，否则False
    """
    symbol = symbol.split('.')[-1][:2].upper()
    if current_time is None:
        current_time = dt.datetime.now().time()
    
    # 获取当前品种的交易时间段
    sessions = CLASS_SESSIONS.get(symbol)
    if sessions is None:
        raise ValueError(f"未知的期货品种代码: {symbol}")
    
    # 遍历每个交易时间段
    for start_str, end_str in sessions:
        start_time = dt.datetime.strptime(start_str, "%H:%M").time()
        end_time = dt.datetime.strptime(end_str, "%H:%M").time()
        
        # 处理跨夜交易时间段
        if start_time > end_time:
            if current_time >= start_time or current_time <= end_time:
                return True
        else:
            if start_time <= current_time <= end_time:
                return True
    
    return False

# 示例用法
if __name__ == "__main__":
    symbol = "SHFE.cu2512"  # 示例期货品种代码
    if is_trading_time(symbol):
        print(f"当前时间在{symbol}的交易时间段内")
    else:
        print(f"当前时间不在{symbol}的交易时间段内")