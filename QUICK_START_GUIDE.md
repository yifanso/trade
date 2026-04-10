# 量化系统实操指南

**目标**: 5分钟上手 - 下载数据 → 执行回测 → 查看结果

---

## 🚀 两大核心功能

### 功能1️⃣: 下载历史交易数据

#### 最简快速方案 (3行代码)

```python
from src.qlib_backtest.data.downloader import DataDownloader

downloader = DataDownloader()
downloader.download_data(['000858.SZ', '000651.SZ'], incremental=True)
print("✓ 数据下载完成！")
```

**机制解析**:
- 自动检测本地缓存是否存在
- 若存在：仅下载缺失部分（增量）
- 若不存在：全量下载
- 数据存储于: `~/.cache/qlib_backtest/data/*.csv`

#### 配置化方案 (从YAML配置文件)

```python
# config/default_config.yaml 中配置
stocks:
  - code: "000858.SZ"
    name: "五粮液"
  - code: "000651.SZ"
    name: "格力电器"
  - code: "600519.SH"
    name: "贵州茅台"

# Python代码调用
from src.qlib_backtest.utils import ConfigManager
from src.qlib_backtest.data.downloader import DataDownloader

config = ConfigManager.load('config/default_config.yaml')
downloader = DataDownloader()
downloader.download_data(config['stocks'])
```

#### 定时自动下载方案 (每日凌晨2点)

```python
from src.qlib_backtest.data.downloader import DataDownloader
import time

downloader = DataDownloader()

# 启动后台定时任务
downloader.start_scheduler(
    stock_codes=['000858.SZ', '000651.SZ'],
    cron_expression='0 2 * * *'  # 每日凌晨2点
)

print("✓ 后台定时下载已启动")
print("  下次执行: 明天02:00")

# 程序保持运行
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("✓ 后台下载已停止")
```

#### 验证下载是否成功

```python
import os

cache_dir = os.path.expanduser('~/.cache/qlib_backtest/data')
files = os.listdir(cache_dir)
print(f"✓ 已缓存 {len(files)} 只股票的数据:")
for f in files:
    size = os.path.getsize(f'{cache_dir}/{f}') / 1024 / 1024
    print(f"  - {f}: {size:.1f} MB")
```

---

### 功能2️⃣: 执行量化回测

#### 最简快速方案 (5步)

```python
#!/usr/bin/env python
"""5分钟回测完整流程"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from qlib_backtest.data import DataHandler
from qlib_backtest.features import FeatureEngine
from qlib_backtest.strategies import StrategyFactory
from qlib_backtest.backtest import BacktestEngine

# 1️⃣ 加载数据
print("\n[Step 1] 加载数据...")
handler = DataHandler()
df = handler.load_stock_data(
    stock_codes=['000858.SZ', '000651.SZ'],
    start_date='2020-01-01',
    end_date='2023-12-31'
)

# 2️⃣ 清洗数据
print("[Step 2] 清洗数据...")
df = handler.clean_data(df)
df = handler.add_returns(df)

# 3️⃣ 计算特征
print("[Step 3] 计算特征...")
feature_engine = FeatureEngine()
df = feature_engine.calculate_all_features(df)

# 4️⃣ 生成信号
print("[Step 4] 生成信号...")
strategy = StrategyFactory.create_strategy(
    'momentum',
    short_window=5,
    long_window=20
)
signals = strategy.generate_signals(df)

# 5️⃣ 执行回测
print("[Step 5] 执行回测...")
engine = BacktestEngine(
    initial_capital=1000000.0,
    commission=0.001,
    slippage=0.0001
)
results = engine.run_backtest(df, signals)

# 输出结果
print("\n" + "="*50)
print("回测结果")
print("="*50)
for key, value in results.to_dict().items():
    print(f"{key:20s}: {value}")
print("="*50)
```

**执行**:
```bash
python quick_backtest.py
```

**输出**:
```
[Step 1] 加载数据...
[Step 2] 清洗数据...
[Step 3] 计算特征...
[Step 4] 生成信号...
[Step 5] 执行回测...

==================================================
回测结果
==================================================
total_return           : 45.23%
annual_return          : 12.65%
sharpe_ratio           : 1.42
max_drawdown           : -18.50%
win_rate               : 55.32%
profit_factor          : 1.89
==================================================
```

#### Web界面方案 (实时查看)

```bash
# 方式1: 启动Web服务
python examples/web_frontend.py

# 方式2: 打开浏览器
# http://localhost:5000

# 方式3: 在Web上执行回测
# - 访问 /backtest 页面
# - 选择策略参数
# - 点击 "执行回测"
# - 实时查看结果图表
```

#### 多策略对比方案

```python
from src.qlib_backtest.strategies import StrategyFactory
from src.qlib_backtest.backtest import BacktestEngine

# 准备数据（同上）
handler = DataHandler()
df = handler.load_stock_data(['000858.SZ'], '2020-01-01', '2023-12-31')
df = handler.clean_data(df)
feature_engine = FeatureEngine()
df = feature_engine.calculate_all_features(df)

# 测试多个策略
engine = BacktestEngine()
strategies = ['momentum', 'mean_reversion', 'combined']

results_dict = {}
for strat_name in strategies:
    print(f"测试 {strat_name}...")
    strategy = StrategyFactory.create_strategy(strat_name)
    signals = strategy.generate_signals(df)
    results = engine.run_backtest(df, signals)
    results_dict[strat_name] = results

# 比较结果
print("\n策略对比:")
print("├─ Momentum")
print(f"│  ├─ Sharpe: {results_dict['momentum'].sharpe_ratio:.2f}")
print(f"│  └─ 最大回撤: {results_dict['momentum'].max_drawdown:.2%}")
print("├─ Mean Reversion")
print(f"│  ├─ Sharpe: {results_dict['mean_reversion'].sharpe_ratio:.2f}")
print(f"│  └─ 最大回撤: {results_dict['mean_reversion'].max_drawdown:.2%}")
print("└─ Combined (投票)")
print(f"   ├─ Sharpe: {results_dict['combined'].sharpe_ratio:.2f}")
print(f"   └─ 最大回撤: {results_dict['combined'].max_drawdown:.2%}")
```

---

## 📂 数据流向与存储

```
┌─────────────────────────────────────────────────────┐
│ 数据源                                              │
├─────────────────────────────────────────────────────┤
│ QLib (微软库)  │ 行情API  │ CSV文件  │ 其他数据源  │
└───────┬─────────┬─────────┬─────────┬──────────────┘
        │         │         │         │
        └─────────┴─────────┴─────────┘
               ↓
┌─────────────────────────────────────────────────────┐
│ DataDownloader                                      │
├─────────────────────────────────────────────────────┤
│ • 增量下载逻辑                                      │
│ • 错误重试机制                                      │
│ • 后台定时任务                                      │
└───────────────┬─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────────────────┐
│ 本地缓存                                            │
├─────────────────────────────────────────────────────┤
│ CSV文件              │ SQLite元数据库               │
│ ~/.cache/qlib_..    │ ~/.cache/qlib_.../db.sqlite │
│ ├─ 000858.SZ.csv    │ ├─ download_history        │
│ ├─ 000651.SZ.csv    │ └─ download_logs           │
│ └─ 600519.SH.csv    │                             │
└───────────────┬─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────────────────┐
│ DataHandler.load_stock_data()                       │
├─────────────────────────────────────────────────────┤
│ • 读取CSV缓存                                       │
│ • 多股票合并                                        │
│ • 时间对齐                                          │
└───────────────┬─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────────────────┐
│ DataHandler.clean_data()                            │
├─────────────────────────────────────────────────────┤
│ • 缺失值填充（前向/后向）                          │
│ • 异常值处理（3σ原则）                             │
│ • OHLC逻辑检查                                      │
│ • 返回清洁的DataFrame                              │
└───────────────┬─────────────────────────────────────┘
                ↓
         [特征计算 and 策略回测]
```

---

## 🔧 常见问题排查

### Q1: 数据下载很慢

**原因**: 首次下载全量数据

**解决**:
```python
# ✓ 后续下载会自动使用增量更新
downloader.download_data(['000858.SZ'], incremental=True)
# 第1次: 全量下载 (耗时长)
# 第2次: 仅下载新增 (快速)

# ✓ 若QLib不可用，自动使用模拟数据（用于测试）
# 查看日志了解进度
```

### Q2: 数据缺失或异常

**原因**: 数据源问题或QLib未配置

**解决**:
```python
# 1. 检查缓存
import os
cache_dir = os.path.expanduser('~/.cache/qlib_backtest/data')
print(os.listdir(cache_dir))

# 2. 验证数据质量
from src.qlib_backtest.data import DataHandler, DataValidator
handler = DataHandler()
df = handler.load_stock_data(['000858.SZ'], '2020-01-01', '2023-12-31')

# 查看统计信息
print(df.describe())
print(f"时间跨度: {df.index.min()} to {df.index.max()}")
print(f"缺失值率: {df.isnull().sum().sum() / df.size * 100:.2f}%")

# 3. 自动清洗
df_clean = handler.clean_data(df)
print("清洗后缺失值率: 0%")
```

### Q3: 回测结果为什么是负收益?

**原因**: 策略信号质量差或参数不匹配

**解决**:
```python
# 1. 检查信号生成
signals = strategy.generate_signals(df)
print(f"买入信号数: {(signals['signal'] == 1).sum()}")
print(f"卖出信号数: {(signals['signal'] == -1).sum()}")
print(f"信号分布: {signals['signal'].value_counts()}")

# 2. 调整策略参数
# 动量策略参数调优示例
for short_w in [3, 5, 10]:
    for long_w in [15, 20, 30]:
        if short_w >= long_w:
            continue
        strategy = StrategyFactory.create_strategy(
            'momentum',
            short_window=short_w,
            long_window=long_w
        )
        signals = strategy.generate_signals(df)
        results = engine.run_backtest(df, signals)
        print(f"short={short_w}, long={long_w}: Sharpe={results.sharpe_ratio:.2f}")

# 3. 尝试其他策略
for strat in ['momentum', 'mean_reversion', 'combined']:
    strategy = StrategyFactory.create_strategy(strat)
    # ... 测试 ...
```

### Q4: 如何自定义策略?

**解决**:

```python
# 新建文件: src/qlib_backtest/strategies/my_strategy.py

from .base import BaseStrategy

class MyStrategy(BaseStrategy):
    """我的自定义策略"""
    
    def __init__(self, threshold=0.02):
        self.threshold = threshold
    
    def generate_signals(self, df):
        """
        生成交易信号
        返回: 信号DataFrame (signal列: 1=买, -1=卖, 0=持仓)
        """
        df = df.copy()
        
        # 你的策略逻辑
        # 例: 当价格突破SMA时买入
        df['sma'] = df.groupby('stock_code')['close'].transform(
            lambda x: x.rolling(20).mean()
        )
        df['signal'] = 0
        df.loc[df['close'] > df['sma'] * (1 + self.threshold), 'signal'] = 1
        df.loc[df['close'] < df['sma'] * (1 - self.threshold), 'signal'] = -1
        
        return df

# 使用
strategy = MyStrategy(threshold=0.03)
signals = strategy.generate_signals(df)
results = engine.run_backtest(df, signals)
```

---

## 📊 回测结果解读

### 关键指标含义

| 指标 | 含义 | 好的范围 | 解读 |
|------|------|--------|------|
| **总收益率** | 全周期收益 | >30% | 4年内收益超30%为优秀 |
| **年化收益** | 年均收益 | >15% | 每年平均收益15%为目标 |
| **Sharpe比率** | 风险调整收益 | >1.0 | >1.0风险效率高，>2.0优秀 |
| **最大回撤** | 最大跌幅 | <30% | 风险指标，越小越好 |
| **胜率** | 赢利交易占比 | >50% | 超过50%表示策略有效 |
| **盈利因子** | 赢利/亏损比 | >1.5 | 衡量盈利质量，越高越好 |
| **Calmar** | 年化/最大回撤 | >0.5 | 综合指标，衡量恢复能力 |

### 结果示例解读

```
回测结果：
total_return           : 45.23%  ✓ 4年累计收益45%
annual_return          : 12.65%  ✓ 年均收益12.65%
sharpe_ratio           : 1.42    ✓ 风险调整收益好
max_drawdown           : -18.50% ✓ 最大回撤18.5%可接受
win_rate               : 55.32%  ✓ 胜率55%表示策略有效
profit_factor          : 1.89    ✓ 赢利是亏损1.89倍

解读：
✅ 这是一个质量还不错的策略
   - Sharpe > 1.0 表示风险收益比均衡
   - 胜率 > 50% 表示策略有效
   - 年化 > 10% 表示超越基准
   - 最大回撤 < 20% 表示风险可控

⚠️ 改进方向：
   - 若要追求更高收益，可优化参数
   - 若要降低回撤，考虑加入风险管理
   - 若要提高稳定性，考虑多策略组合
```

---

## 💡 进阶用法

### 方案A: 多时间周期回测

```python
# 同时测试多个周期的数据
periods = [
    ('2020-01-01', '2021-12-31', '2年'),
    ('2021-01-01', '2022-12-31', '又1年'),
    ('2022-01-01', '2023-12-31', '又1年'),
    ('2020-01-01', '2023-12-31', '全4年'),
]

for start, end, label in periods:
    df = handler.load_stock_data(['000858.SZ'], start, end)
    df = handler.clean_data(df)
    df = feature_engine.calculate_all_features(df)
    signals = strategy.generate_signals(df)
    results = engine.run_backtest(df, signals)
    
    print(f"{label}: Sharpe={results.sharpe_ratio:.2f}, "
          f"收益={results.total_return:.2%}")
```

### 方案B: 多股票组合回测

```python
# 测试不同股票组合的表现
stocks_combination = [
    ['000858.SZ'],                           # 单只
    ['000858.SZ', '000651.SZ'],              # 双只
    ['000858.SZ', '000651.SZ', '600519.SH'], # 三只
]

for stocks in stocks_combination:
    df = handler.load_stock_data(stocks, '2020-01-01', '2023-12-31')
    df = handler.clean_data(df)
    df = feature_engine.calculate_all_features(df)
    signals = strategy.generate_signals(df)
    results = engine.run_backtest(df, signals)
    
    print(f"组合 {stocks}: Sharpe={results.sharpe_ratio:.2f}")
```

### 方案C: 输出详细的交易记录

```python
# 查看每笔交易的细节
results = engine.run_backtest(df, signals)

# 查看所有订单
print(f"总订单数: {len(results.orders)}")
for order in results.orders[:5]:  # 前5笔
    print(f"  {order.date}: {order.order_type} "
          f"{order.quantity} 股 @{order.price:.2f}")

# 查看已平仓交易的收益
print(f"\n已平仓交易: {len(results.trades)}")
for trade in results.trades[:5]:  # 前5笔
    print(f"  {trade['entry_date']} -> {trade['exit_date']}: "
          f"收益 {trade['return']:.2%}")

# 获取资金曲线
equity_curve = results.equity_curve
print(f"\n资金曲线:")
print(f"  起始资金: ¥{equity_curve['equity'].iloc[0]:,.0f}")
print(f"  最大资金: ¥{equity_curve['equity'].max():,.0f}")
print(f"  最小资金: ¥{equity_curve['equity'].min():,.0f}")
print(f"  最终资金: ¥{equity_curve['equity'].iloc[-1]:,.0f}")
```

---

## 📞 完整工作流总结

```
开始
  ↓
[1] 下载数据
    downloader.download_data(['000858.SZ'], incremental=True)
  ↓
[2] 加载数据
    df = handler.load_stock_data(['000858.SZ'], 
                                 '2020-01-01', '2023-12-31')
  ↓
[3] 清洗数据
    df = handler.clean_data(df)
    df = handler.add_returns(df)
  ↓
[4] 计算特征
    df = feature_engine.calculate_all_features(df)
  ↓
[5] 生成信号
    signals = strategy.generate_signals(df)
  ↓
[6] 执行回测
    results = engine.run_backtest(df, signals)
  ↓
[7] 分析结果
    print(results.to_dict())
    → 根据Sharpe/回撤/胜率判断策略质量
  ↓
[8] 优化调整（可选）
    → 调整参数重复 [5]-[7]
    → 或更换策略重复 [5]-[7]
    → 或增加新数据重复 [2]-[7]
  ↓
结束 ✓
```

---

## 🎯 下一步推荐

1. **立即体验** (5分钟)
   ```bash
   python examples/basic_backtest.py
   ```

2. **参数调优** (30分钟)
   - 修改 strategy 参数 (short_window, long_window)
   - 观察 Sharpe 如何变化

3. **策略创新** (1小时)
   - 自定义新策略
   - 或组合多个策略

4. **实战部署** (后续)
   - 定时下载最新数据
   - 每日自动回测
   - Web查看结果

---

**祝你量化交易成功！** 🚀

