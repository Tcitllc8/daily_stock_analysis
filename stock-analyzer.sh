#!/bin/bash
# ============================================================
# OpenClaw 股票分析工具
# 用法: 在飞书直接发送股票代码，自动分析
# ============================================================

set -e

# 配置
PROJECT_DIR="/Users/liao/openclaw/daily_stock_analysis"
LOG_FILE="/tmp/stock_analysis.log"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_message() {
    echo -e "${BLUE}[🦞 Stock Analyzer]${NC} $1"
}

# 提取股票代码
extract_stocks() {
    echo "$1" | grep -oE '\b[0-9]{6}\b|\b[A-Z]{2,5}\b|\bHK[0-9]{5}\b' | tr '[:lower:]' '[:upper:]' | sort -u
}

# 分析股票
analyze() {
    local stock="$1"
    local timestamp=$(date +%s)
    
    echo_message "📊 正在分析: $stock..."
    
    # 设置股票代码并运行
    cd "$PROJECT_DIR"
    export STOCK_LIST=$stock
    
    # 运行分析
    timeout 120 python3 main.py > "/tmp/stock_${timestamp}.log" 2>&1 || true
    
    # 提取结果
    if grep -q "成功: 1" "/tmp/stock_${timestamp}.log"; then
        # 提取评分
        local score=$(grep -oP "评分 \K\d+" "/tmp/stock_${timestamp}.log" | head -1 || echo "?")
        
        # 提取决策
        if grep -q "买入" "/tmp/stock_${timestamp}.log"; then
            echo "🟢 $stock | 买入 | 评分: $score"
        elif grep -q "观望" "/tmp/stock_${timestamp}.log"; then
            echo "🟡 $stock | 观望 | 评分: $score"
        elif grep -q "卖出" "/tmp/stock_${timestamp}.log"; then
            echo "🔴 $stock | 卖出 | 评分: $score"
        else
            echo "⚪ $stock | 分析完成 | 评分: $score"
        fi
    else
        echo "⚠️ $stock | 分析失败"
    fi
}

# 主入口
main() {
    if [ -z "${1:-}" ]; then
        echo "🦞 股票分析工具"
        echo ""
        echo "用法:"
        echo "  ./stock-analyzer.sh 600519"
        echo "  ./stock-analyzer.sh AAPL TSLA"
        echo "  ./stock-analyzer.sh hk00700"
        echo ""
        echo "在飞书中使用时，直接发送股票代码即可"
        exit 0
    fi
    
    local input="$*"
    local stocks=$(extract_stocks "$input")
    
    if [ -z "$stocks" ]; then
        echo "❌ 未检测到股票代码"
        echo "请发送: 600519, AAPL, hk00700"
        exit 1
    fi
    
    echo_message "检测到股票: $stocks"
    echo ""
    
    for stock in $stocks; do
        analyze "$stock"
        echo ""
    done
    
    echo_message "✅ 分析完成!"
}

main "$@"
