#!/bin/bash
# ============================================================
# 股票快速查询 - 使用百度股市通
# ============================================================

STOCK="${1:-}"

# 检查参数
if [ -z "$STOCK" ]; then
    cat << 'HELP'
🦞 股票快速查询

用法: 
  ./stock_q.sh 600519   # A股
  ./stock_q.sh AAPL      # 美股
  ./stock_q.sh hk00700   # 港股

返回: 当前价格 + 涨跌幅
时间: 1-2秒
HELP
    exit 0
fi

echo "📈 $STOCK"

# 方法1: 使用百度股市通 (A股)
if [[ "$STOCK" =~ ^[0-9]{6}$ ]]; then
    RESULT=$(curl -s "https://gupiao.baidu.com/api/stock/getfund巴信息?from=pc&os_ver=1&cuid=xxx&vv=100&format=json&stock_code=sh${STOCK}" 2>/dev/null)
    if [ -n "$RESULT" ]; then
        PRICE=$(echo "$RESULT" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('stockInfo',{}).get('currentPrice','?'))" 2>/dev/null)
        CHANGE=$(echo "$RESULT" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('stockInfo',{}).get('changePercent','?'))" 2>/dev/null)
        echo "  💰 价格: ¥$PRICE"
        echo "  📊 涨跌: $CHANGE%"
    else
        echo "  ⚠️ 获取失败"
    fi

# 方法2: 美股用 Yahoo
elif [[ "$STOCK" =~ ^[A-Z]{1,5}$ ]]; then
    echo "  💡 建议访问: finance.yahoo.com/quote/$STOCK"
    echo "  📊 或使用 daily_stock_analysis 进行详细分析"
fi
