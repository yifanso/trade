# QLib量化回测框架使用指南

## 目录

1. [快速入门](#快速入门)
2. [详细使用说明](#详细使用说明)
3. [高级功能](#高级功能)
4. [故障排除](#故障排除)

## 快速入门

### 三步启动运行

```bash
# 第1步：安装依赖
pip install -r requirements.txt

# 第2步：运行示例
python examples/basic_backtest.py

# 第3步：查看结果
ls results/
```

## 详细使用说明

### 1. 数据加载

#### 使用QLib数据源

```python
from src.qlib_backtest.data import DataHandler

# 创建数据处理器
handler = DataHandler(
    qlib_data_path="~/.qlib/qlib_data",
    cache_dir="~/.cache/qlib_backtest"
)

# 加载数据
df = handler.load_stock_data(
    stock_codes=["000001.SZ", "600000.SH"],  # A股代码
    start_date="2020-01-01",
    end_date="2023-12-31",
    freq="day"  # 日频
)
```

#### 使用本地CSV数据

```python
import pandas as pd

# 从CSV加载
df = pd.read_csv("stock_data.csv")

# 需要包含以下列：date, stock_code, open, high, low, close, volume
# 或使用处理器的方法
df = handler.load_stock_data(...)  # 自动处理缺失数据
```

### 2. 数据清洗

```python
# 处理缺失值、异常值
df = handler.clean_data(df)

# 添加收益率列
df = handler.add_returns(df)

# 重新采样（改变时间频率）
df_weekly = handler.resample_data(df, freq="1W")
```

### 3. 特征计算

```python
from src.qlib_backtest.features import FeatureEngine

engine = FeatureEngine()

# 一键计算所有特征
df = engine.calculate_all_features(
    df,
    feature_config={
        'momentum': {'windows': [5, 10, 20]},
        'volatility': {'windows': [10, 20]},
        'trend': {'windows': [5, 10, 20]},
    }
)

# 特征会包括：
# - RSI, MACD, Momentum（动量指标）
# - 标准差、布林带（波动率指标）
# - SMA, EMA, 价格相对位置（趋势指标）
```

#### 可用的技术指标

| 指标类型 | 具体指标 | 说明 |
|---------|---------|------|
| **动量** | RSI | 相对强弱指数，衡量买卖力度 |
| | MACD | 指数移动平均线，判断价格走势 |
| | Momentum | 动量，衡量价格变化速度 |
| **波动率** | Std | 标准差，衡量价格波动程度 |
| | Bollinger Bands | 布林带，判断价格极值 |
| **趋势** | SMA | 简单移动平均线 |
| | EMA | 指数移动平均线 |
| | Price_to_SMA | 价格相对于均线的位置 |
| **成交量** | Average Volume | 平均成交量 |
| | Volume Ratio | 成交量比率 |

### 4. 策略开发

#### 使用预制策略

```python
from src.qlib_backtest.strategies import StrategyFactory

# 创建Momentum策略
strategy = StrategyFactory.create_strategy(
    'momentum',
    short_window=5,     # 短期窗口
    long_window=20,     # 长期窗口
    threshold=0.02,     # 信号阈值
)

# 或创建Mean Reversion策略
strategy = StrategyFactory.create_strategy(
    'mean_reversion',
    window=20,          # 窗口大小
    std_multiple=2,     # 标准差倍数
)

# 生成交易信号
signals = strategy.generate_signals(df)
```

#### 理解交易信号

交易信号包含以下信息：

```python
Signal(
    date="2023-01-01",          # 信号日期
    stock_code="000001.SZ",     # 股票代码
    signal_type="BUY",          # BUY, SELL, HOLD
    confidence=0.85,             # 置信度 0-1
    price=100.50,               # 当前价格
)
```

#### 自定义策略

```python
from src.qlib_backtest.strategies import BaseStrategy, Signal

class MyCustomStrategy(BaseStrategy):
    """我的自定义策略"""
    
    def __init__(self):
        super().__init__("MyCustomStrategy")
        self.parameters = {
            'param1': 10,
            'param2': 20,
        }
    
    def generate_signals(self, df):
        """生成交易信号"""
        signals = []
        
        for idx, row in df.iterrows():
            # 你的交易逻辑
            if row['close'] > row['sma_20']:
                signal_type = 'BUY'
                confidence = 0.7
            else:
                signal_type = 'SELL'
                confidence = 0.5
            
            signals.append(Signal(
                date=row['date'],
                stock_code=row['stock_code'],
                signal_type=signal_type,
                confidence=confidence,
                price=row['close'],
            ))
        
        return signals

# 使用自定义策略
strategy = MyCustomStrategy()
signals = strategy.generate_signals(df)
```

### 5. 回测执行

```python
from src.qlib_backtest.backtest import BacktestEngine

# 创建回测引擎
engine = BacktestEngine(
    initial_capital=1000000.0,      # 初始资本（100万）
    commission=0.001,                # 佣金0.1%
    slippage=0.0001,                 # 滑点0.01%
    max_position_per_stock=0.3,      # 单股最大持仓30%
)

# 执行回测
results = engine.run_backtest(df, signals)
```

#### 回测结果分析

```python
# 查看概览
print(results.to_dict())
# 输出：
# {
#     'total_return': '25.34%',
#     'annual_return': '7.81%',
#     'sharpe_ratio': '1.23',
#     'max_drawdown': '-15.42%',
#     'win_rate': '52.34%',
#     'profit_factor': '1.45'
# }

# 详细数据
print(f"交易次数: {len(results.trades)}")
print(f"资金曲线长度: {len(results.equity_curve)}")

# 访问资金曲线
equity_df = results.equity_curve
# 包含列: date, cash, position_value, total_value

# 访问交易记录
for trade in results.trades[:5]:
    print(trade)
    # 包含: stock_code, quantity, buy_price, sell_price, pnl, date
```

## 高级功能

### 1. 多策略组合

```python
from src.qlib_backtest.strategies import (
    MomentumStrategy,
    MeanReversionStrategy,
    CombinedStrategy,
)

# 创建两个策略
momentum = MomentumStrategy()
mean_rev = MeanReversionStrategy()

# 组合策略
combined = CombinedStrategy()
combined.add_strategy(momentum)
combined.add_strategy(mean_rev)
combined.set_parameters(voting_threshold=0.5)

# 生成组合信号（投票机制）
signals = combined.generate_signals(df)
```

### 2. 参数优化

```python
from itertools import product

# 定义参数范围
param_grid = {
    'short_window': [5, 10, 15],
    'long_window': [20, 30, 40],
    'threshold': [0.01, 0.02, 0.03],
}

best_sharpe = -float('inf')
best_params = None

for short_w, long_w, threshold in product(
    param_grid['short_window'],
    param_grid['long_window'],
    param_grid['threshold']
):
    strategy = StrategyFactory.create_strategy(
        'momentum',
        short_window=short_w,
        long_window=long_w,
        threshold=threshold,
    )
    signals = strategy.generate_signals(df)
    results = engine.run_backtest(df, signals)
    
    if results.sharpe_ratio > best_sharpe:
        best_sharpe = results.sharpe_ratio
        best_params = {
            'short_window': short_w,
            'long_window': long_w,
            'threshold': threshold,
        }

print(f"最优参数: {best_params}")
print(f"最优Sharpe: {best_sharpe}")
```

参考 `examples/optimization_example.py` 获取完整示例。

### 3. 结果导出

```python
from src.qlib_backtest.utils import ResultsExporter

exporter = ResultsExporter("./my_results")

# 导出结果（包括汇总、资金曲线、交易记录）
exporter.export_results(results, "my_strategy")

# 导出文件列表：
# - my_strategy_YYYYMMDD_HHMMSS_summary.json
# - my_strategy_YYYYMMDD_HHMMSS_equity.csv
# - my_strategy_YYYYMMDD_HHMMSS_trades.csv
```

### 4. 性能深度分析

```python
from src.qlib_backtest.utils import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()

# 计算额外指标
metrics = analyzer.analyze_strategy(results.equity_curve)

print(f"年化波动率: {metrics['annual_volatility']:.2%}")
print(f"Calmar比率: {metrics['calmar_ratio']:.2f}")
print(f"Sortino比率: {metrics['sortino_ratio']:.2f}")
```

## 故障排除

### 问题1：无法导入模块

**症状**：`ModuleNotFoundError: No module named 'qlib_backtest'`

**解决**：
```bash
# 将项目路径添加到PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/trade/src"

# 或在Python脚本中
import sys
sys.path.insert(0, '/path/to/trade/src')
```

### 问题2：QLib数据加载失败

**症状**：`Warning: QLib未安装或无法导入，使用模拟数据`

**解决**：
```bash
# 安装QLib
pip install qlib==0.9.16

# 或更新安装
pip install --upgrade qlib
```

### 问题3：内存不足

**症状**：加载大量数据时内存溢出

**解决**：
```python
# 分段加载
stocks = ["000001.SZ", "000002.SZ", ...]  # 很多股票

for stock in stocks[:10]:  # 每次只加载10个
    df = handler.load_stock_data(
        stock_codes=[stock],
        start_date="2020-01-01",
        end_date="2023-12-31",
    )
    # 处理数据...
```

### 问题4：回测速度缓慢

**症状**：大量股票或长时间段的回测运行很慢

**优化建议**：
```python
# 1. 减少股票数量
stocks = stocks[:5]  # 只测试前5个

# 2. 缩短时间段进行快速测试
start_date = "2023-01-01"
end_date = "2023-12-31"

# 3. 简化特征计算
df = engine.calculate_all_features(
    df,
    feature_config={
        'momentum': {'windows': [10, 20]},
        # 只保留必需的特征
    }
)
```

### 问题5：交易信号过多或过少

**症状**：信号数量不合理

**调整参数**：
```python
# 信号过少，降低阈值
strategy.set_parameters(threshold=0.01)  # 从0.02降低到0.01

# 信号过多，提高阈值
strategy.set_parameters(threshold=0.03)  # 从0.02提高到0.03
```

## 最佳实践总结

### ✅ 推荐做法

1. **始终验证数据**
   ```python
   print(df.head())
   print(df.info())
   print(df.describe())
   ```

2. **分步调试**
   ```python
   # 逐步运行，检查中间结果
   df = handler.load_stock_data(...)
   logger.info(f"加载数据：{len(df)} 行")
   
   df = feature_engine.calculate_all_features(df)
   logger.info(f"特征列数：{df.shape[1]}")
   ```

3. **参数的合理范围**
   - short_window: 3-10
   - long_window: 20-60
   - threshold: 0.01-0.05

4. **使用模拟数据测试**
   ```python
   # 在优化前用模拟数据测试框架
   df = handler._generate_mock_data(
       ["000001.SZ"],
       "2023-01-01",
       "2023-12-31"
   )
   ```

### ❌ 避免的做法

1. **避免过度优化**
   - 不要用整个数据集优化参数
   - 应该使用交叉验证

2. **避免前向偏差**
   - 确保只使用历史数据生成信号
   - 不要使用未来的价格信息

3. **避免忽视交易成本**
   - 设置合理的佣金和滑点
   - 这直接影响策略盈利能力

4. **避免忽略风险管理**
   - 设置止损
   - 限制单个头寸的大小

## 联系和支持

如有问题，请查阅：
- 项目文档：README.md
- 示例文件：examples/
- QLib官方文档：https://qlib.readthedocs.io/
