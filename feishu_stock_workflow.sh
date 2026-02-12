#!/bin/bash
# ============================================================
# 飞书股票分析工作流
# 在飞书群发送股票代码，自动调用分析并返回结果
# ============================================================

# 配置
PROJECT_DIR="/Users/liao/openclaw/daily_stock_analysis"
STOCK_LIST_FILE="$PROJECT_DIR/.env.stocks"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：提取股票代码
extract_stocks() {
    echo "$1" | grep -oE '\b[0-9]{6}\b|\b[A-Z]{2,5}\b|\bHK[0-9]{5}\b' | tr '[:lower:]' '[:upper:]' | sort -u
}

# 函数：分析单只股票
analyze_stock() {
    local stock=$1
    local timestamp=$(date +%s)
    
    echo "📊 正在分析: $stock..."
    
    # 运行分析
    cd "$PROJECT_DIR"
    STOCK_LIST=$stock python3 main.py > /tmp/stock_analysis_$timestamp.log 2>&1
    
    # 提取关键结果
    if grep -q "买入" /tmp/stock_analysis_$timestamp.log; then
        echo "🟢 $stock - 买入/看多"
    elif grep -q "观望" /tmp/stock_analysis_$timestamp.log; then
        echo "🟡 $stock - 观望/震荡"
    elif grep -q "卖出" /tmp/stock_analysis_$timestamp.log; then
        echo "🔴 $stock - 卖出/看空"
    else
        echo "⚪ $stock - 分析完成"
    fi
}

# 主函数
main() {
    local message="$1"
    
    # 提取股票代码
    local stocks=$(extract_stocks "$message")
    
    if [ -z "$stocks" ]; then
        echo "❌ 未检测到股票代码"
        echo "请发送格式: 600519, AAPL, hk00700"
        exit 1
    fi
    
    echo "📈 检测到股票: $stocks"
    echo ""
    
    # 分析每只股票
    for stock in $stocks; do
        analyze_stock "$stock"
        echo ""
        sleep 2  # 避免 API 限流
    done
    
    echo "✅ 分析完成!"
}

# 显示帮助
show_help() {
    cat << EOF
🦞 飞书股票分析工作流

使用方法:
    ./feishu_stock_workflow.sh <股票代码或消息>

示例:
    ./feishu_stock_workflow.sh "帮我分析 600519"
    ./feishu_stock_workflow.sh "AAPL TSLA"
    ./feichu_stock_workflow.sh "600519,hk00700,AAPL"

在飞书中使用时:
    发送消息包含股票代码即可自动分析

支持格式:
    - A股: 600519 (6位数字)
    - 港股: HK00700 (hk开头+5位数字)
    - 美股: AAPL (2-5位大写字母)

EOF
}

# 根据参数执行
case "${1:-help}" in
    help|--help|-h)
        show_help
        ;;
    *)
        main "$1"
        ;;
esac
