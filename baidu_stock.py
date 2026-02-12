#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度股市通 A股实时行情
免费、稳定
"""

import os
import sys
import json
import requests

def get_baidu_stock(stock_code):
    """获取百度股市通数据"""
    # 百度股市通 API
    url = f"https://gupiao.baidu.com/api/stock/getinfo?stock_code={stock_code}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://gupiao.baidu.com/"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('errorMsg') == 'SUCCESS':
            return data['stockInfo']
        else:
            return None
    except Exception as e:
        return {"error": str(e)}

def analyze(stock):
    """分析股票"""
    data = get_baidu_stock(stock)
    
    if not data or 'error' in data:
        print(f"❌ {stock}: 获取失败")
        return
    
    print(f"""
📈 **{stock}** 百度股市通

💰 当前价格: {data.get('currentPrice', '?')}
📊 涨跌: {data.get('priceChange', '?')}%
📈 昨收: {data.get('preClose', '?')}
📉 开盘: {data.get('open', '?')}
📈 最高: {data.get('high', '?')}
📉 最低: {data.get('low', '?')}
📦 成交量: {data.get('volume', '?')}

⏰ {data.get('time', '?')}
""")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("🦊 百度股市通 A股查询")
        print("用法: python3 baidu_stock.py 300418")
    else:
        analyze(sys.argv[1])
