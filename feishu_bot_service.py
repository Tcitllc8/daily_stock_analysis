#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书股票分析 Bot 服务
监听飞书群消息，自动分析股票
"""

import os
import sys
import json
import re
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from lark_oapi import lark, card

# 配置
APP_ID = os.getenv("FEISHU_APP_ID", "cli_a9f48c9a15f81cc6")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "ZZBkyG6sLghb1Dj9AoFIVeCrZWqXsRTo")
PROJECT_DIR = "/Users/liao/openclaw/daily_stock_analysis"
PORT = 8080

# 飞书客户端
client = lark.Client(APP_ID, APP_SECRET)


def extract_stock_codes(text: str) -> list:
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


def analyze_single_stock(stock_code: str) -> str:
    """分析单只股票"""
    stock = stock_code.upper().replace('HK', 'hk')
    
    try:
        # 构建命令
        cmd = f'''
        cd {PROJECT_DIR} && \
        STOCK_LIST={stock} python3 main.py 2>&1 | grep -A 20 "=== {stock} ===" | head -30
        '''
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            output = result.stdout
            # 提取关键信息
            if "买入" in output or "看多" in output:
                return f"**{stock}**: 🟢 买入/看多"
            elif "观望" in output or "震荡" in output:
                return f"**{stock}**: 🟡 观望/震荡"
            elif "卖出" in output or "看空" in output:
                return f"**{stock}**: 🔴 卖出/看空"
            else:
                return f"**{stock}**: 分析完成"
        else:
            return f"**{stock}**: ❌ 分析失败"
            
    except Exception as e:
        return f"**{stock}**: ❌ 错误 - {str(e)}"


def send_message(receive_id: str, message: str):
    """发送消息到飞书"""
    try:
        resp = client.message.send().send(
            lark.SendMessageReq.builder()
            .receive_id(receive_id)
            .msg_type("text")
            .content(json.dumps({"text": message}))
            .build()
        )
        
        if resp.code == 0:
            return True
        else:
            print(f"发送失败: {resp.msg}")
            return False
    except Exception as e:
        print(f"错误: {e}")
        return False


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def do_GET(self):
        """处理 GET 请求"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'''
        <html>
        <head><title>飞书股票分析 Bot</title></head>
        <body>
        <h1>🦞 飞书股票分析 Bot 运行中</h1>
        <p>状态: ✅ 正常</p>
        <p>功能: 监听飞书消息，自动分析股票代码</p>
        <p>使用: 在飞书群发送股票代码 (如: 600519, AAPL, hk00700)</p>
        </body>
        </html>
        ''')
    
    def do_POST(self):
        """处理 POST 请求 (飞书 webhook)"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # 解析飞书事件
            data = json.loads(post_data.decode('utf-8'))
            
            # 验证 URL
            if self.path == '/webhook':
                # 处理消息事件
                if 'challenge' in data:
                    # URL 验证事件
                    response = {'challenge': data['challenge']}
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # 处理实际消息
                event = data.get('event', {})
                message = event.get('message', {})
                text_content = message.get('text', '')
                receive_id = event.get('receive_id', '')
                
                # 提取股票代码
                stocks = extract_stock_codes(text_content)
                
                if stocks:
                    # 分析股票
                    results = []
                    for stock in stocks[:5]:  # 最多分析5只
                        result = analyze_single_stock(stock)
                        results.append(result)
                    
                    # 发送结果
                    response_text = f"📊 股票分析结果:\n\n" + "\n".join(results)
                    response_text += f"\n\n⏰ 分析时间: {datetime.now().strftime('%H:%M:%S')}"
                    
                    send_message(receive_id, response_text)
                
                # 确认收到
                self.send_response(200)
                self.end_headers()
                
        except Exception as e:
            print(f"处理请求错误: {e}")
            self.send_response(500)
            self.end_headers()


def run_server():
    """运行 HTTP 服务器"""
    server = HTTPServer(('0.0.0.0', PORT), RequestHandler)
    print(f"🚀 飞书股票分析 Bot 已启动")
    print(f"📡 监听端口: {PORT}")
    print(f"🔗 Webhook URL: http://your-server:{PORT}/webhook")
    print(f"\n💡 在飞书机器人中配置 Webhook 地址")
    server.serve_forever()


def test_analysis():
    """测试股票分析"""
    test_stocks = ['600519', 'AAPL', 'hk00700']
    
    print("🧪 测试股票分析...")
    
    for stock in test_stocks:
        print(f"\n📊 分析 {stock}...")
        result = analyze_single_stock(stock)
        print(result)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_analysis()
    else:
        run_server()
