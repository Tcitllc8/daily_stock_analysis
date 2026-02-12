#!/usr/bin/env python3
"""
快速股票分析 - 只返回基本行情数据，无需 AI 分析
"""

import os
import sys
import json
import subprocess
import re

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

def analyze_a_stock(stock_code):
    """快速分析单只股票（只获取基本数据）"""
    stock = stock_code.upper().replace('HK', '')
    
    result = {
        'stock': stock_code,
        'time': __import__('datetime').datetime.now().strftime('%H:%M:%S')
    }
    
    try:
        # A股
        if re.match(r'^\d{6}$', stock_code):
            if AKSHARE_AVAILABLE:
                try:
                    df = ak.stock_zh_a_spot_em()
                    row = df[df['代码'] == stock]
                    if not row.empty:
                        data = row.iloc[0]
                        result.update({
                            'name': data.get('名称', '?'),
                            'price': data.get('最新价', 0),
                            'change': data.get('涨跌幅', 0),
                            'volume': data.get('成交量', 0),
                            'turnover': data.get('成交额', 0),
                        })
                except Exception as e:
                    result['error'] = str(e)
        
        # 美股
        elif re.match(r'^[A-Z]{1,5}$', stock_code):
            if YFINANCE_AVAILABLE:
                try:
                    ticker = yf.Ticker(stock_code)
                    info = ticker.fast_info
                    result.update({
                        'price': info.last_price,
                        'change': (info.last_price - info.previous_close) / info.previous_close * 100,
                    })
                except Exception as e:
                    result['error'] = str(e)
        
        # 港股
        elif stock_code.upper().startswith('HK') or stock_code.startswith('hk'):
            result['note'] = '港股需要 TuShare 或其他数据源'
    
    except Exception as e:
        result['error'] = str(e)
    
    return result


def main():
    if len(sys.argv) < 2:
        print("""
🦞 快速股票分析（只返回基本行情）

用法:
    python3 quick_analyze.py 600519
    python3 quick_analyze.py AAPL
    python3 quick_analyze.py 600519 AAPL

特点:
    - 1-3秒返回结果
    - 无需 AI 分析
    - 基本行情数据
        """)
        return
    
    stocks = sys.argv[1:]
    
    print(f"📊 快速分析 {len(stocks)} 只股票\n")
    
    for stock in stocks[:5]:  # 最多5只
        print(f"📈 {stock}...")
        result = analyze_a_stock(stock)
        
        if 'price' in result:
            print(f"  💰 价格: {result['price']}")
            if 'change' in result:
                change = result['change']
                emoji = '🟢' if change > 0 else '🔴' if change < 0 else '⚪'
                print(f"  {emoji} 涨跌幅: {change:+.2f}%")
        else:
            print(f"  ⚠️ {result.get('error', '获取失败')}")
        print()


if __name__ == '__main__':
    main()
