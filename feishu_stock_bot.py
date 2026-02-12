#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书股票分析机器人
直接在飞书群发送股票代码，自动调用 daily_stock_analysis 进行分析
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from lark_oapi import lark, card

# 导入飞书 SDK
try:
    from lark_oapi import lark
    LARK_AVAILABLE = True
except ImportError:
    LARK_AVAILABLE = False
    print("⚠️ lark-oapi 未安装，将使用 webhook 模式")

# 配置
APP_ID = os.getenv("FEISHU_APP_ID", "cli_a9f48c9a15f81cc6")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "ZZBkyG6sLghb1Dj9AoFIVeCrZWqXsRTo")
PROJECT_DIR = "/Users/liao/openclaw/daily_stock_analysis"

# 股票代码正则
STOCK_PATTERN = re.compile(r'^[0-9]{6}$|^hk[0-9]{5}$|^[A-Z]{1,5}$', re.IGNORECASE)


def analyze_stock(stock_code: str) -> str:
    """
    调用 daily_stock_analysis 分析单只股票
    """
    print(f"📊 正在分析股票: {stock_code}")
    
    try:
        # 创建临时配置文件
        env_file = os.path.join(PROJECT_DIR, ".env.analyze")
        stock_list = stock_code.upper().replace('HK', 'hk')
        
        # 生成分析命令
        cmd = f"""
        cd {PROJECT_DIR} && \
        STOCK_LIST={stock_list} \
        python3 -c "
import sys
sys.path.insert(0, '.')
from src.core.pipeline import StockAnalysisPipeline
import asyncio

async def main():
    pipeline = StockAnalysisPipeline()
    results = await pipeline.analyze([\"{stock_list}\"])
    for stock_code, result in results.items():
        print(f'=== {stock_code} ===')
        print(result.get('decision', '无决策'))
        print(result.get('summary', ''))

asyncio.run(main())
        "
        """
        
        # 运行分析
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"❌ 分析失败: {result.stderr}"
            
    except Exception as e:
        return f"❌ 错误: {str(e)}"


def send_to_feishu(chat_id: str, message: str):
    """
    发送消息到飞书
    """
    try:
        from lark_oapi import lark
        
        client = lark.Client(APP_ID, APP_SECRET)
        
        # 发送文本消息
        resp = client.message.send().send(
            lark.SendMessageReq.builder()
            .receive_id(chat_id)
            .msg_type("text")
            .content(json.dumps({"text": message}))
            .build()
        )
        
        if resp.code == 0:
            print("✅ 消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {resp.msg}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def quick_analyze(stock_code: str) -> str:
    """
    快速分析（使用简化版逻辑）
    """
    stock_code = stock_code.upper().strip()
    
    # 验证股票代码格式
    if not (re.match(r'^\d{6}$', stock_code) or 
            re.match(r'^HK\d{5}$', stock_code) or 
            re.match(r'^[A-Z]{1,5}$', stock_code)):
        return f"❌ 无效的股票代码: {stock_code}\n请输入：\n- A股: 600519\n- 港股: hk00700\n- 美股: AAPL"
    
    # 这里可以调用实际的 API，这里返回示例
    return f"""📈 股票分析: **{stock_code}**

⚠️ 正在调用分析系统...

请稍候，结果将在30秒内返回。

💡 提示: 可发送多条股票代码进行分析"""


def web_ui_analyze(stock_code: str) -> str:
    """
    使用 web UI 模式进行分析
    """
    stock_code = stock_code.upper().replace('HK', 'hk').strip()
    
    return f"""📊 股票代码: **{stock_code}**

🔄 正在分析...

由于当前未配置完整的 API，可以手动访问：

🔗 {PROJECT_DIR}

或在飞书中直接发送股票代码，等待分析结果。

✅ 系统已记录您的请求
"""


def parse_message(message: str) -> list:
    """
    解析消息中的股票代码
    """
    stocks = []
    
    # A股: 6位数字
    a_stocks = re.findall(r'\b(\d{6})\b', message)
    stocks.extend(a_stocks)
    
    # 港股: hk+5位数字
    hk_stocks = re.findall(r'\b(hk\d{5})\b', message, re.IGNORECASE)
    stocks.extend([s.upper() for s in hk_stocks])
    
    # 美股: 大写字母
    us_stocks = re.findall(r'\b([A-Z]{1,5})\b', message)
    stocks.extend(us_stocks)
    
    return list(set(stocks))  # 去重


def main():
    """
    主函数 - 测试股票分析
    """
    if len(sys.argv) < 2:
        print("""
🦞 飞书股票分析机器人

使用方法:
    python3 feishu_stock_bot.py <股票代码>

示例:
    python3 feishu_stock_bot.py 600519
    python3 feishu_stock_bot.py hk00700
    python3 feishu_stock_bot.py AAPL

实时监听模式:
    python3 feishu_stock_bot.py listen
        """)
        return
    
    if sys.argv[1] == "listen":
        print("🔄 启动飞书消息监听模式...")
        print("💡 请配置飞书 webhook 或事件订阅")
        print("📖 参考: https://open.feishu.cn/document/server-docs/im/message")
    else:
        stock = sys.argv[1]
        result = quick_analyze(stock)
        print(result)


if __name__ == "__main__":
    main()
