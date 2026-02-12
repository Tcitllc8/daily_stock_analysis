#!/usr/bin/env python3
"""
OpenClaw 股票分析工具
直接集成到 OpenClaw，可在飞书直接使用
"""

import os
import sys
import re
import subprocess
import json
from datetime import datetime

# 配置
PROJECT_DIR = "/Users/liao/openclaw/daily_stock_analysis"

def extract_stocks(text):
    """从文本中提取股票代码"""
    stocks = []
    
    # A股: 6位数字
    a_stocks = re.findall(r'\b(\d{6})\b', text)
    stocks.extend(a_stocks)
    
    # 港股: hk+5位数字
    hk_stocks = re.findall(r'\b(hk\d{5})\b', text, re.IGNORECASE)
    stocks.extend([s.upper() for s in hk_stocks])
    
    # 美股: 2-5位大写字母
    us_stocks = re.findall(r'\b([A-Z]{2,5})\b', text)
    stocks.extend(us_stocks)
    
    return list(set(stocks))


def analyze_stock(stock_code):
    """分析单只股票"""
    stock = stock_code.upper().replace('HK', 'hk')
    
    try:
        # 设置环境并运行
        env = os.environ.copy()
        env['STOCK_LIST'] = stock
        
        result = subprocess.run(
            [sys.executable, 'main.py'],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            env=env
        )
        
        # 提取结果
        output = result.stdout + result.stderr
        
        if '成功: 1' in output or '分析完成' in output:
            # 提取评分
            score_match = re.search(r'评分\s*:?\s*(\d+)', output)
            score = score_match.group(1) if score_match else '?'
            
            # 提取决策
            if '买入' in output or '看多' in output:
                decision = '🟢 买入/看多'
            elif '观望' in output or '震荡' in output:
                decision = '🟡 观望/震荡'
            elif '卖出' in output or '看空' in output:
                decision = '🔴 卖出/看空'
            else:
                decision = '⚪ 分析完成'
            
            return {
                'stock': stock,
                'decision': decision,
                'score': score,
                'status': 'success'
            }
        else:
            return {
                'stock': stock,
                'decision': '⚠️ 分析失败',
                'score': '?',
                'status': 'failed'
            }
            
    except Exception as e:
        return {
            'stock': stock,
            'decision': f'❌ 错误: {str(e)}',
            'score': '?',
            'status': 'error'
        }


def main():
    """主函数 - 分析输入中的股票代码"""
    if len(sys.argv) < 2:
        print("""
🦞 股票分析工具

用法: 
    python3 stock_tool.py "600519"
    python3 stock_tool.py "AAPL TSLA hk00700"

在飞书中使用时，直接发送股票代码即可
        """)
        return
    
    # 解析输入
    input_text = ' '.join(sys.argv[1:])
    stocks = extract_stocks(input_text)
    
    if not stocks:
        print("❌ 未检测到股票代码")
        print("请发送: 600519, AAPL, hk00700")
        return
    
    # 分析每只股票
    results = []
    for stock in stocks[:5]:  # 最多5只
        result = analyze_stock(stock)
        results.append(result)
    
    # 输出结果（JSON 格式供 OpenClaw 使用）
    output = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'count': len(results),
        'results': results
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
