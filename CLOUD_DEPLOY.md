# 🚀 GitHub Actions 云端部署指南

## 步骤 1：Fork 项目

1. 访问：https://github.com/Tcitllc8/daily_stock_analysis
2. 点击 **Fork** 按钮

## 步骤 2：配置 Secrets

进入你的 Fork 仓库：

1. **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**

添加以下 Secrets：

| Secret Name | 值 |
|-------------|-----|
| `GEMINI_API_KEY` | AIzaSyC7BOvloI-f2fSeYVX_RyoLfK3XXOJMvNw |
| `TAVILY_API_KEY` | tvly-dev-NvRKMrvdEmOYY5yU8Xsk2aSxpM7xW3Y7 |
| `FEISHU_APP_ID` | cli_a9f48c9a15f81cc6 |
| `FEISHU_APP_SECRET` | ZZBkyG6sLghb1Dj9AoFIVeCrZWqXsRTo |
| `FEISHU_RECEIVER_ID` | ou_52983ba775f0e29daeec4c9b679229fa |
| `ITICK_TOKEN` | ff4bba56e5874fe7884f03fab0ab942b13f64e2f49964200957ceefa5180f606 |
| `TUSHARE_TOKEN` | 你的 Tushare Token |

## 步骤 3：运行

### 方式 1：自动运行
- 每天 09:30 自动分析（工作日）

### 方式 2：手动触发
1. 进入 **Actions** 标签
2. 选择 **Daily Stock Analysis**
3. 点击 **Run workflow**
4. 输入股票代码（如：`600519 AAPL hk00700`）

## 步骤 4：查看结果

- **Actions** 标签 → 查看运行日志
- 飞书会收到分析结果推送

## ☁️ 云端优势

| 优势 | 说明 |
|------|------|
| 免费 | 每月 2000 分钟 |
| 全球节点 | 无网络限制 |
| 自动运行 | 定时任务 |
| 零运维 | 无需服务器 |

## 📊 数据源优先级（云端可用）

1. **ITaick** - 港股/美股（毫秒级）
2. **Tushare** - A股（需要积分）
3. **AkShare** - A股（稳定）
4. **eFinance** - A股（备用）

## ⚠️ 注意事项

- GitHub Actions 是公开仓库，请勿上传敏感信息
- 所有密钥请使用 Secrets
- 定时任务可能因 GitHub 维护有 1-2 分钟延迟
