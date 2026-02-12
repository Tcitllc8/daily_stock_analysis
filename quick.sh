#!/bin/bash
# ============================================================
# 超快速股票查询 - 使用新浪接口
# ============================================================

STOCK="${1:-}"

if [ -z "$STOCK" ]; then
    echo "🦞 超快速股票查询 (1秒返回)"
    echo ""
    echo "用法: ./quick.sh 600519"
    echo "      ./quick.sh AAPL"
    exit 0
fi

echo "📊 $STOCK"

# 美股 - Yahoo Finance
if [[ "$STOCK" =~ ^[A-Z]{1,5}$ ]]; then
    DATA=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/${STOCK}?interval=1m" 2>/dev/null)
    PRICE=$(echo "$DATA" | python3 -c "import sys,json;d=json.load(sys.stdin);r=d.get('chart',{}).get('result',[{}]);print(r[0].get('meta',{}).get('regularMarketPrice','?'))" 2>/dev/null)
    CHANGE=$(echo "$DATA" | python3 -c "import sys,json;d=json.load(sys.stdin);r=d.get('chart',{}).get('result',[{}]);print(r[0].get('meta',{}).get('regularMarketChangePercent','?'))" 2>/dev/null)
    echo "  💰 价格: $PRICE"
    echo "  📈 涨跌: $CHANGE%"

# A股 - 新浪
elif [[ "$STOCK" =~ ^[0-9]{6}$ ]]; then
    DATA=$(curl -s "https://hq.sinajs.cn/list=s_${STOCK}" 2>/dev/null)
    if echo "$DATA" | grep -q "no data"; then
        echo "  ⚠️ 无此股票"
    else
        NAME=$(echo "$DATA" | cut -d',' -f1 | cut -d'=' -f2)
        PRICE=$(echo "$DATA" | cut -d',' -f3)
        CHANGE=$(echo "$DATA" | cut -d',' -f32)
        echo "  🏷️ 名称: $NAME"
        echo "  💰 价格: ¥$PRICE"
        echo "  📈 涨跌: $CHANGE%"
    fi
else
    echo "  ⚠️ 格式无效"
fi
