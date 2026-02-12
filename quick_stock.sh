#!/bin/bash
# ============================================================
# 超快速股票查询 - 1秒返回
# 使用东财免费接口
# ============================================================

STOCK="${1:-}"

if [ -z "$STOCK" ]; then
    echo "🦞 超快速股票查询"
    echo ""
    echo "用法: ./quick_stock.sh 600519"
    echo "      ./quick_stock.sh AAPL"
    exit 0
fi

# A股
if [[ "$STOCK" =~ ^[0-9]{6}$ ]]; then
    echo "📈 A股: $STOCK"
    curl -s "https://push2.eastmoney.com/api/qt/stock/get?fltt=2&fields=f2,f3,f4,f8,f12,f13,f14,f15,f16,f17,f18,f20,f21,f24,f25,f45,f48&secid=1.${STOCK}" 2>/dev/null | \
    python3 -c "
import sys,json
try:
    data=json.load(sys.stdin)
    d=data.get('data',{}).get('f57',{})
    print(f\"  💰 价格: {d.get('f2','?')}\")
    print(f\"  📊 涨跌: {d.get('f3','?')}%\")
    print(f\"  �成交量: {d.get('f8','?')}\")
except: print('  ⚠️ 获取失败')
" 2>/dev/null || echo "  ⚠️ 网络错误"

# 美股
elif [[ "$STOCK" =~ ^[A-Z]{1,5}$ ]]; then
    echo "📈 美股: $STOCK"
    curl -s "https://query1.finance.yahoo.com/v8/finance/chart/${STOCK}?interval=1m" 2>/dev/null | \
    python3 -c "
import sys,json
try:
    data=json.load(sys.stdin)
    d=data.get('chart',{}).get('result',[{}])
    if d:
        meta=d[0].get('meta',{})
        print(f\"  💰 价格: {meta.get('regularMarketPrice','?')}\")
        print(f\"  📊 涨跌: {meta.get('regularMarketChangePercent','?')}%\")
except: print('  ⚠️ 获取失败')
" 2>/dev/null || echo "  ⚠️ 网络错误"

else
    echo "⚠️ 无效格式: $STOCK"
fi
