#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITaick 快速股票分析 - 1秒返回结果
"""

import os
import sys
import json
import re
import requests

# 配置
TOKEN = os.getenv("ITICK_TOKEN", "ff4bba56e5874fe7884f03fab0ab942b13f64e2f49964200957ceefa5180f606")

def get_quote(region, code):
    """获取股票报价"""
    url = f"https://api.itick.org/stock/quote?region={region}&code={code}"
    headers = {"token": TOKEN}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def simple_analyze(data):
    """简单分析（基于涨跌幅）"""
    if not data or 'data' not in data:
        return None
    
    d = data['data']
    change = d.get('chp', 0)
    
    if change > 5:
        decision = "🟢 强烈买入"
        score = 90
    elif change > 2:
        decision = "🟢 买入"
        score = 80
    elif change > 0:
        decision = "🟡 持有"
        score = 60
    elif change > -2:
        decision = "🟡 观望"
        score = 50
    elif change > -5:
        decision = "🟠 谨慎"
        score = 40
    else:
        decision = "🔴 卖出"
        score = 30
    
    return {
        'price': d.get('p'),
        'change': change,
        'decision': decision,
        'score': score
    }

def get_region(stock):
    """判断市场"""
    stock = stock.upper()
    if re.match(r'^\d{6}$', stock):
        return "SZ" if stock.startswith('0') or stock.startswith('3') else "SH"
    elif stock.startswith('HK') or len(stock) == 5:
        return "HK"
    else:
        return "US"

def main():
    stocks = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not stocks:
        print("""
🦊 ITaick 快速分析 (1秒返回)

用法: python3 itaick_quick.py AAPL 600519 hk00700

支持:
- A股: 600519 (上海/深圳)
- 港股: hk00700 或 00700
- 美股: AAPL

特点:
- 毫秒级延迟
- 实时数据
- 无需 AI 分析
        """)
        return
    
    print("📊 快速分析\n")
    
    for stock in stocks[:5]:
        # 清理股票代码
        clean_stock = stock.upper().replace('HK', '')
        
        # 获取市场
        region = get_region(clean_stock)
        
        # 获取数据
        data = get_quote(region, clean_stock)
        
        if 'error' in data:
            print(f"❌ {stock}: {data['error']}\n")
            continue
        
        result = simple_analyze(data)
        
        if result:
            print(f"📈 {stock}")
            print(f"  💰 价格: {result['price']}")
            print(f"  📊 涨跌: {result['change']:+.2f}%")
            print(f"  🎯 {result['decision']} | 评分: {result['score']}\n")
        else:
            print(f"⚠️ {stock}: 无数据\n")

if __name__ == '__main__':
    main()
