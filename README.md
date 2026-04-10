# QLib 股票量化和回测框架

一个基于微软QLib库的完整股票量化交易和回测解决方案，提供从数据加载、特征工程、策略开发到回测分析的全套工具。

## 项目特性

✅ **完整的数据管理**
- 集成微软QLib库的强大数据处理能力
- 自动数据清洗和特征提取
- 支持多股票多周期数据加载
- ⭐ **新增：定期自动下载数据** - 定时从QLib更新交易数据

✅ **灵活的特征工程**
- 技术指标计算（RSI、MACD、动量等）
- 趋势特征（SMA、EMA、布林带等）
- 成交量特征和波动率特征
- 特征归一化和选择

✅ **完善的策略框架**
- 基础策略类 (BaseStrategy)
- 预制策略：Momentum、Mean Reversion
- 策略组合和投票机制
- 策略工厂模式便于扩展

✅ **强大的回测引擎**
- 逐日期逐股票执行交易
- 精确的成本计算（佣金、滑点）
- 完整的交易记录和持仓管理
- 详细的性能指标计算

✅ **深度性能分析**
- 总收益率、年化收益率
- Sharp比率、最大回撤
- 胜率、盈利因子
- Calmar比率、Sortino比率

## 项目结构

```
trade/
├── README.md                          # 本文件
├── requirements.txt                   # 依赖包列表
├── config/                            # 配置文件目录
│   └── default_config.yaml           # 默认配置
├── src/
│   └── qlib_backtest/                # 核心库
│       ├── __init__.py
│       ├── data/                     # 数据处理模块
│       │   └── __init__.py           # DataHandler类
│       ├── features/                 # 特征工程模块
│       │   └── __init__.py           # FeatureEngine类
│       ├── strategies/               # 策略模块
│       │   └── __init__.py           # 各种策略类
│       ├── backtest/                 # 回测引擎
│       │   └── __init__.py           # BacktestEngine类
│       └── utils/                    # 工具函数
│           └── __init__.py           # 日志、配置、导出等
├── examples/                          # 示例脚本
│   ├── basic_backtest.py             # 基础回测示例
│   └── advanced_backtest.py          # 高级回测示例
└── results/                           # 回测结果输出目录
```

## 安装和配置

### 前置条件

- Python 3.8+
- pip 或 conda

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd trade
   ```

2. **创建虚拟环境** (可选但推荐)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **下载QLib数据** (可选)
   ```python
   import qlib
   from qlib import init
   
   # 初始化QLib并下载中国市场数据
   qlib_data_path = "~/.qlib/qlib_data"
   # 首次使用时会自动下载
   ```

## 快速开始

### 基础使用示例

```python
from src.qlib_backtest.data import DataHandler
from src.qlib_backtest.features import FeatureEngine
from src.qlib_backtest.strategies import StrategyFactory
from src.qlib_backtest.backtest import BacktestEngine

# 1. 加载数据
data_handler = DataHandler()
df = data_handler.load_stock_data(
    stock_codes=["000001.SZ", "600000.SH"],
    start_date="2020-01-01",
    end_date="2023-12-31",
)

# 2. 特征工程
feature_engine = FeatureEngine()
df = feature_engine.calculate_all_features(df)

# 3. 生成策略信号
strategy = StrategyFactory.create_strategy(
    'momentum',
    short_window=5,
    long_window=20,
)
signals = strategy.generate_signals(df)

# 4. 执行回测
backtest_engine = BacktestEngine(initial_capital=1000000.0)
results = backtest_engine.run_backtest(df, signals)

# 5. 查看结果
print(results.to_dict())
```

### 运行示例脚本

```bash
# 基础示例
python examples/basic_backtest.py

# 高级示例（包含组合策略）
python examples/advanced_backtest.py

# 启动前端页面
python examples/web_frontend.py

# 快速入门数据定期下载 (推荐)
python examples/quick_data_download.py
```

## ⭐ 新功能：定期数据下载

自动定期从QLib下载和更新交易数据，无需手动操作！

### 快速开始

```python
from src.qlib_backtest.data.downloader import DataDownloader

# 创建下载器
downloader = DataDownloader()

# 启动定时任务（每个工作日下午4点更新）
downloader.start_scheduler(
    stock_codes=["000858.SZ", "000651.SZ"],
    cron_expression="0 16 * * 1-5",  # 工作日下午4点
    incremental=True,  # 只下载新的数据
)

print("✓ 定时下载已启动！数据会在后台自动更新")
```

### 主要特性

✨ **定时自动下载** - 支持Cron表达式，灵活配置更新时间  
✨ **增量更新** - 智能检测上次下载时间，只更新新数据  
✨ **批量处理** - 支持监控多个股票  
✨ **完整日志** - SQLite数据库记录所有操作  
✨ **后台运行** - 独立线程，不阻塞主程序  

### 详细文档

👉 [完整数据下载指南](DATA_DOWNLOAD_GUIDE.md) - 详细API和高级用法

### 常见用法

```python
from src.qlib_backtest.data.downloader import DataDownloader, DataUpdateManager

# 方法1: 单次下载
downloader = DataDownloader()
results = downloader.download_data("000858.SZ", start_date="2024-01-01")

# 方法2: 增量更新（自动检测上次日期）
downloader.download_data("000858.SZ", incremental=True)

# 方法3: 使用管理器（推荐）
manager = DataUpdateManager(downloader)
manager.add_stocks(["000858.SZ", "000651.SZ"])
manager.start_monitoring(cron_expression="0 16 * * 1-5")

# 方法4: 查看状态
stats = downloader.get_download_statistics()
print(f"已下载 {stats['unique_stocks']} 只股票，成功率 {stats['successful']}/{stats['total_downloads']}")
```

### Cron表达式示例

| 表达式 | 含义 |
|-------|------|
| `0 16 * * 1-5` | 每个工作日下午4点（股市收盘后）✓ 推荐 |
| `0 9 * * *` | 每天上午9点 |
| `0 9,15 * * *` | 每天上午9点和下午3点 |
| `*/30 * * * *` | 每30分钟 |

👉 更详细内容见 [数据下载完整指南](DATA_DOWNLOAD_GUIDE.md)

## 前端页面

项目包含一个简单的 Flask 前端：

- `http://localhost:5000/`：回测结果仪表盘
- `http://localhost:5000/download`：股票数据下载页面
- `http://localhost:5000/backtest`：量化回测执行页面

### 下载股票数据
1. 访问 `http://localhost:5000/download`
2. 输入股票代码、开始日期、结束日期
3. 选择频率后点击“下载 CSV”

### 执行回测
1. 访问 `http://localhost:5000/backtest`
2. 输入股票代码、日期范围
3. 选择策略并调整参数
4. 点击“执行回测”并查看回测指标

> 如果未安装 QLib，系统会回退到模拟数据生成，以便快速验证页面功能。

## 核心模块说明

### DataHandler（数据处理）

```python
from src.qlib_backtest.data import DataHandler

handler = DataHandler()

# 加载数据
df = handler.load_stock_data(
    stock_codes=["000001.SZ"],
    start_date="2020-01-01",
    end_date="2023-12-31",
    freq="day"  # 频率: day, week, month
)

# 清洗数据
df = handler.clean_data(df)

# 添加收益率
df = handler.add_returns(df)

# 重新采样
df = handler.resample_data(df, freq="1W")  # 转换为周数据
```

### FeatureEngine（特征工程）

```python
from src.qlib_backtest.features import FeatureEngine

engine = FeatureEngine()

# 计算所有特征
df = engine.calculate_all_features(
    df,
    feature_config={
        'momentum': {'windows': [5, 10, 20]},
        'volatility': {'windows': [10, 20]},
        'trend': {'windows': [5, 10, 20]},
        'volume': {'windows': [5, 20]},
    }
)

# 特征归一化
df = engine.normalize_features(df, method='zscore')

# 特征选择
top_features = engine.select_features(df, target='daily_return', top_k=10)
```

### 策略框架

#### 使用预制策略

```python
from src.qlib_backtest.strategies import StrategyFactory

# 动量策略
strategy = StrategyFactory.create_strategy(
    'momentum',
    short_window=5,
    long_window=20,
    threshold=0.02,
)

# 均值回归策略
strategy = StrategyFactory.create_strategy(
    'mean_reversion',
    window=20,
    std_multiple=2,
)

signals = strategy.generate_signals(df)
```

#### 自定义策略

```python
from src.qlib_backtest.strategies import BaseStrategy, Signal

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("MyStrategy")
    
    def generate_signals(self, df):
        signals = []
        # 在这里实现你的交易逻辑
        # ...
        return signals

# 使用自定义策略
my_strategy = MyStrategy()
signals = my_strategy.generate_signals(df)
```

### BacktestEngine（回测引擎）

```python
from src.qlib_backtest.backtest import BacktestEngine

engine = BacktestEngine(
    initial_capital=1000000.0,  # 初始资本
    commission=0.001,            # 佣金比例
    slippage=0.0001,             # 滑点比例
)

# 执行回测
results = engine.run_backtest(df, signals)

# 查看结果
print(f"总收益率: {results.total_return:.2%}")
print(f"Sharp比率: {results.sharpe_ratio:.2f}")
print(f"最大回撤: {results.max_drawdown:.2%}")

# 导出结果
results.equity_curve.to_csv("equity_curve.csv")
```

## 配置文件说明

编辑 `config/default_config.yaml` 进行配置：

```yaml
# 数据配置
data:
  stocks: ["000001.SZ", "600000.SH"]
  start_date: "2020-01-01"
  end_date: "2023-12-31"

# 策略配置
strategy:
  type: "momentum"
  parameters:
    short_window: 5
    long_window: 20

# 回测配置
backtest:
  initial_capital: 1000000.0
  commission: 0.001
  max_position_per_stock: 0.3
```

## 性能指标解释

| 指标 | 描述 | 计算方式 |
|------|------|---------|
| **Total Return** | 总收益率 | (期末资产 - 期初资产) / 期初资产 |
| **Annual Return** | 年化收益率 | (期末资产 / 期初资产)^(1/年数) - 1 |
| **Sharpe Ratio** | Sharp比率 | 平均日收益 / 日收益标准差 × √252 |
| **Max Drawdown** | 最大回撤 | 最大历史高点到最低点的下跌幅度 |
| **Win Rate** | 胜率 | 盈利交易数 / 总交易数 |
| **Profit Factor** | 盈利因子 | 总盈利 / 总亏损 |

## 常见问题

### Q: 如何使用自己的数据？
A: 可以直接传入DataFrame到 `calculate_all_features()` 方法：
```python
df = pd.read_csv("your_data.csv")
df = feature_engine.calculate_all_features(df)
```

### Q: 如何改变回测参数？
A: 创建 BacktestEngine 时指定参数，或修改 `config/default_config.yaml`：
```python
engine = BacktestEngine(
    initial_capital=5000000.0,  # 改为500万
    commission=0.002,            # 改为0.2%佣金
)
```

### Q: 支持哪些股票市场？
A: 目前支持：
- 中国A股 (SZ/SH 代码)
- 可扩展至其他市场

### Q: 如何组合多个策略？
A: 使用 CombinedStrategy：
```python
from src.qlib_backtest.strategies import CombinedStrategy

combined = CombinedStrategy()
combined.add_strategy(momentum_strategy)
combined.add_strategy(mean_reversion_strategy)
signals = combined.generate_signals(df)
```

## 扩展开发

### 添加新的技术指标

在 `src/qlib_backtest/features/__init__.py` 中添加：

```python
def _add_custom_indicator(self, df, window):
    """自定义指标"""
    df['my_indicator'] = df.groupby('stock_code')['close'].transform(
        lambda x: x.rolling(window).some_operation()
    )
    return df
```

### 开发自定义策略

```python
from src.qlib_backtest.strategies import BaseStrategy, Signal

class CustomStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("CustomStrategy")
    
    def generate_signals(self, df):
        signals = []
        # 你的策略逻辑
        return signals
```

## 最佳实践

1. **始终进行数据清洗**
   - 处理缺失值
   - 检查数据质量
   - 去除异常值

2. **使用足够的历史数据**
   - 建议至少1年的数据用于参数优化
   - 避免过度优化

3. **实现严格的风险管理**
   - 设置止损
   - 控制持仓大小
   - 分散投资

4. **持续监控和优化**
   - 定期回测
   - 监控实时表现
   - 及时调整参数

## 许可证

MIT License

## 联系和支持

如有问题或建议，欢迎提交 Issue 或 Pull Request。

## 参考资源

- [Microsoft QLib 文档](https://qlib.readthedocs.io/)
- [Pandas 文档](https://pandas.pydata.org/)
- [Numpy 文档](https://numpy.org/)

---

**免责声明**: 本框架仅供教育和研究用途，不构成任何投资建议。使用本框架进行实盘交易需自行承担风险。