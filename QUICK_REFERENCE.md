# 快速参考 - 量化交易系统 v2.0

## 🚀 最常用的3个命令

```bash
# 1️⃣ 下载数据 (3行代码)
python -c "from src.qlib_backtest.data.downloader import DataDownloader as D; D().download_data(['000858.SZ'], incremental=True)"

# 2️⃣ 执行回测 (1条命令)
python examples/complete_workflow.py

# 3️⃣ Web查看 (1条命令)
python examples/web_frontend.py
# 打开: http://localhost:5000
```

---

## 📚 优先级阅读顺序

| 顺序 | 文档 | 时间 | 内容 |
|------|------|------|------|
| 1️⃣ | **QUICK_START_GUIDE.md** | 5分钟 | 快速上手，2个核心功能 |
| 2️⃣ | **SYSTEM_REDESIGN_SUMMARY.md** | 10分钟 | 重构总结，功能完成度 |
| 3️⃣ | **ARCHITECTURE_GUIDE.md** | 30分钟 | 完整架构，9大模块详解 |

---

## 🎯 我想做什么？

### ✅ 下载历史交易数据

```python
from qlib_backtest.data.downloader import DataDownloader

downloader = DataDownloader()
downloads = downloader.download_data(['000858.SZ', '000651.SZ'], incremental=True)
# 数据保存在: ~/.cache/qlib_backtest/data/
```

**参考**: QUICK_START_GUIDE.md - "功能1️⃣ 下载历史交易数据"

---

### ✅ 执行量化回测

```python
from qlib_backtest.data import DataHandler, FeatureEngine
from qlib_backtest.strategies import StrategyFactory
from qlib_backtest.backtest import BacktestEngine

# 1. 加载数据
handler = DataHandler()
df = handler.load_stock_data(['000858.SZ'], '2020-01-01', '2023-12-31')
df = handler.clean_data(df)

# 2. 特征计算
engine = FeatureEngine()
df = engine.calculate_all_features(df)

# 3. 生成信号
strategy = StrategyFactory.create_strategy('momentum')
signals = strategy.generate_signals(df)

# 4. 执行回测
backtest = BacktestEngine(initial_capital=1000000)
results = backtest.run_backtest(df, signals)

# 5. 查看结果
print(f"年化收益: {results.annual_return:.2%}")
print(f"Sharpe: {results.sharpe_ratio:.2f}")
print(f"最大回撤: {results.max_drawdown:.2%}")
```

**参考**: QUICK_START_GUIDE.md - "功能2️⃣ 执行量化回测"

---

### ✅ 自定义新策略

```python
from qlib_backtest.strategies import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("MyStrategy")
    
    def generate_signals(self, df):
        # 你的策略逻辑
        df = df.copy()
        # ... 计算信号 ...
        return df

# 使用
strategy = MyStrategy()
signals = strategy.generate_signals(df)
```

**参考**: QUICK_START_GUIDE.md - "Q4: 如何自定义策略?"

---

### ✅ 定时自动下载数据

```python
from qlib_backtest.data.downloader import DataDownloader

downloader = DataDownloader()
downloader.start_scheduler(
    stock_codes=['000858.SZ', '000651.SZ'],
    cron_expression='0 2 * * *'  # 每日凌晨2点
)

# 程序保持运行
import time
while True:
    time.sleep(60)
```

**参考**: QUICK_START_GUIDE.md - "定时自动下载方案"

---

### ✅ 对比多个策略

```python
engine = BacktestEngine()
strategies = ['momentum', 'mean_reversion']

for strat_name in strategies:
    strategy = StrategyFactory.create_strategy(strat_name)
    signals = strategy.generate_signals(df)
    results = engine.run_backtest(df, signals)
    print(f"{strat_name}: Sharpe={results.sharpe_ratio:.2f}")
```

**参考**: QUICK_START_GUIDE.md - "多策略对比方案"

---

## 📊 关键概念

### DataFlow (数据流)
```
下载 → 加载 → 清洗 → 特征 → 信号 → 回测 → 分析
  ↓      ↓      ↓      ↓      ↓      ↓      ↓
DL    DataH    Clean  Feat   Strat BT    Metrics
```

### 关键Metrics (绩效指标)

| 指标 | 含义 | 好的范围 |
|------|------|--------|
| **年化收益** | 年均收益率 | >10% |
| **Sharpe** | 风险调整收益 | >1.0 |
| **最大回撤** | 最大跌幅 | <30% |
| **胜率** | 赢利交易占比 | >50% |
| **年波动率** | 收益稳定性 | <25% |

### 缓存位置

| 类型 | 位置 |
|------|------|
| 数据 | `~/.cache/qlib_backtest/data/` |
| 元数据 | `~/.cache/qlib_backtest/download_history.db` |
| 回测结果 | `./results/` |
| 日志 | `./logs/` |

---

## ⚠️ 常见问题

**Q: 数据下载慢？**
- A: 首次全量~5s正常。后续增量<1s。

**Q: 回测都是0收益？**
- A: 检查信号数量，调整参数，或降低成本设置。

**Q: 支持哪些资产？**
- A: 目前A股。期货/加密需扩展接口。

**Q: 如何定制策略？**
- A: 参考QUICK_START_GUIDE中的自定义策略章节。

**Q: 生产部署如何做？**
- A: 参考ARCHITECTURE_GUIDE第8章。

---

## 📞 文档导航

- **新手** → QUICK_START_GUIDE.md
- **架构师** → ARCHITECTURE_GUIDE.md
- **PM/决策** → SYSTEM_REDESIGN_SUMMARY.md
- **开发者** → 源代码 + examples/

---

## 🔗 快速链接

| 链接 | 类型 |
|------|------|
| QUICK_START_GUIDE.md | 📖 快速开始 |
| ARCHITECTURE_GUIDE.md | 📘 架构设计 |
| SYSTEM_REDESIGN_SUMMARY.md | 📄 重构总结 |
| examples/complete_workflow.py | 💻 完整示例 |
| examples/web_frontend.py | 🌐 Web应用 |

---

最后更新: 2026-04-10 | 版本: 2.0
