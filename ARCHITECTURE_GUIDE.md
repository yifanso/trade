# 量化交易系统完整架构指南

**版本**: 2.0 | **日期**: 2026-04-10 | **状态**: 生产优化版

---

## 📋 目录

1. [系统概览](#系统概览)
2. [架构模块映射](#架构模块映射)
3. [核心数据流](#核心数据流)
4. [各模块详解](#各模块详解)
5. [快速开始](#快速开始)
6. [最佳实践](#最佳实践)
7. [性能优化](#性能优化)
8. [扩展指南](#扩展指南)

---

## 系统概览

```
┌─────────────────────────────────────────────────────────────────┐
│                   量化交易系统架构 v2.0                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  数据管理层      │  ← 第1层：数据接入、清洗、存储
├─────────────────┤
│ • DataDownloader│  定期下载/增量更新
│ • DataHandler   │  数据加载/清洗/对齐
│ • DataCache     │  本地缓存及查询
│ • DataValidator │  数据质量检查
└──────────┬──────┘
           │
         数据源：QLib / 行情数据库 / CSV / API
           │
┌──────────▼──────┐
│  特征与因子层    │  ← 第2层：因子计算、特征工程
├─────────────────┤
│ • FeatureEngine │  40+技术指标
│ • CustomFactors │  自定义因子表达式
│ • FactorCache   │  因子结果缓存
│ • MLIntegration │  机器学习模型
└──────────┬──────┘
           │
┌──────────▼──────┐
│  策略研究层      │  ← 第3层：信号生成、多资产支持
├─────────────────┤
│ • StrategyBase  │  基础策略类
│ • Momentum      │  动量策略
│ • MeanReversion │  均值回归
│ • Combined      │  组合策略
│ • CustomStrategy│  自定义策略（框架）
└──────────┬──────┘
           │
┌──────────▼──────┐
│  回测评估层      │  ← 第4层：高保真模拟、性能计算
├─────────────────┤
│ • BacktestEngine│  逐日/逐笔回测
│ • PerfMetrics   │  完整绩效指标
│ • RiskMetrics   │  风险度量
│ • Visualization │  曲线图表
└──────────┬──────┘
           │
┌──────────▼──────┐
│  优化策略层      │  ← 第5层：参数优化、防过拟合
├─────────────────┤
│ • GridSearch    │  网格搜索
│ • GeneticAlgo   │  遗传算法
│ • WalkForward   │  推进分析
│ • CrossValid    │  交叉验证
└──────────┬──────┘
           │
┌──────────▼──────┐
│  风险管理层      │  ← 第6层：事前/事中/事后风控
├─────────────────┤
│ • PreRiskCheck  │  事前风控
│ • RuntimeMonitor│  实时监控
│ • Halting       │  自动止损
│ • Attribution   │  风险归因
└──────────┬──────┘
           │
┌──────────▼──────┐
│  策略执行层      │  ← 第7层：实盘执行、订单管理
├─────────────────┤
│ • OrderManager  │  订单生成/路由
│ • BrokerGateway │  多经纪商接口
│ • TradeExecutor │  交易执行
│ • LatencyMonitor│  延迟监控
└──────────┬──────┘
           │
┌──────────▼──────┐
│  报告与分析层    │  ← 第8层：绩效归因、自动报告
├─────────────────┤
│ • ReportGen     │  PDF/HTML报告
│ • Attribution   │  收益/风险归因
│ • Comparison    │  策略对比
│ • Alert         │  邮件/钉钉告警
└──────────┬──────┘
           │
┌──────────▼──────┐
│  运维监控层      │  ← 第9层：容器化、日志、告警
├─────────────────┤
│ • TaskScheduler │  APScheduler定时任务
│ • Logger        │  统一日志
│ • Monitor       │  健康检查
│ • Alert         │  实时告警
│ • Container     │  Docker支持
└──────────┬──────┘
           │
┌──────────▼──────┐
│  用户界面层      │  ← 第10层：Web仪表盘、API
├─────────────────┤
│ • WebDashboard  │  Flask实时仪表盘
│ • RESTful API   │  HTTP API接口
│ • WebSocket     │  实时推送
│ • CLI           │  命令行工具
└─────────────────┘
```

---

## 架构模块映射

基于用户需求的9大模块，现有代码覆盖情况：

| # | 需求模块 | 现有实现 | 完成度 | 优先级 |
|----|---------|--------|-------|-------|
| 1 | **数据管理** | DataHandler + DataDownloader + DataValidator | ✅ 80% | P0 |
| 2 | **策略研究与开发** | FeatureEngine + StrategyBase + 3策略模板 | ✅ 75% | P0 |
| 3 | **回测系统** | BacktestEngine + 完整指标 | ✅ 85% | P0 |
| 4 | **参数优化** | 仅有示例，未实现 | ⚠️ 10% | P1 |
| 5 | **风险管理** | 基础佣金/滑点，无高级风控 | ⚠️ 25% | P1 |
| 6 | **实盘交易** | 无，仅为模拟交易框架 | ❌ 5% | P2 |
| 7 | **绩效归因** | 基础指标，无深度分析 | ⚠️ 30% | P2 |
| 8 | **运维监控** | 基础日志，无容器化 | ⚠️ 30% | P2 |
| 9 | **辅助功能** | Web仪表盘已有，无策略库 | ⚠️ 40% | P3 |

---

## 核心数据流

### **流程1：数据下载到回测的完整链条** (用户需求核心)

```
┌─────────────────────────────────────────────────────────────┐
│ 轴1: 历史交易数据下载                                      │
└─────────────────────────────────────────────────────────────┘

1️⃣ 数据获取阶段
   ├─ DataDownloader.download_data()
   │  ├─ 检查上次下载日期
   │  ├─ 调用QLib API获取数据
   │  ├─ 存储到本地CSV（缓存）
   │  └─ 记录元数据到SQLite
   │
   ├─ 增量更新逻辑
   │  ├─ 若已存在: 仅下载新增区间
   │  └─ 若不存在: 全量下载
   │
   └─ 定时自动下载（可选）
      ├─ APScheduler定时触发
      └─ 每日/每周/每月更新

2️⃣ 数据清洗阶段
   ├─ DataHandler.load_stock_data()
   │  ├─ 读取CSV缓存
   │  ├─ 多股票数据合并
   │  └─ 时间对齐（统一索引）
   │
   ├─ DataHandler.clean_data()
   │  ├─ 缺失值填充（前向/后向）
   │  ├─ 异常值处理（3σ法则）
   │  ├─ OHLC逻辑检查修复
   │  └─ 复权调整（若有拆股/送股）
   │
   └─ DataValidator检查
      ├─ 时间序列连续性
      ├─ 价格合理范围
      └─ 成交量有效性

3️⃣ 特征计算阶段
   ├─ FeatureEngine.calculate_all_features()
   │  ├─ 技术指标（MA、RSI、MACD等）
   │  ├─ 趋势特征（EMA、Bollinger Band）
   │  ├─ 成交量特征（OBV、VWAP）
   │  ├─ 波动率特征（ATR、Volatility）
   │  └─ 自定义因子（CustomFactorsEngine）
   │
   └─ 因子结果缓存（可选）
      └─ 减少重复计算


┌─────────────────────────────────────────────────────────────┐
│ 轴2: 量化回测执行                                           │
└─────────────────────────────────────────────────────────────┘

4️⃣ 信号生成阶段
   ├─ Strategy.generate_signals()
   │  ├─ 单个策略生成信号
   │  │  ├─ Momentum: 动量判断
   │  │  ├─ MeanReversion: 偏离度判断
   │  │  └─ Custom: 自定义逻辑
   │  │
   │  └─ 多策略投票机制
   │     ├─ 权重加总
   │     ├─ 再平衡判断
   │     └─ 信号置信度

5️⃣ 回测执行阶段
   ├─ BacktestEngine.run_backtest()
   │  │
   │  ├─ 初始化
   │  │  ├─ 初始资金 = 1M
   │  │  ├─ 持仓 = {}
   │  │  └─ 现金 = 初始资金
   │  │
   │  ├─ 按日期迭代
   │  │  ├─ for each date in data.dates:
   │  │  │  ├─ 获取该日信号
   │  │  │  ├─ 生成订单（BUY/SELL）
   │  │  │  │  ├─ 判断操作类型
   │  │  │  │  ├─ 计算操作数量
   │  │  │  │  └─ 计算成本（含佣金/滑点）
   │  │  │  │
   │  │  │  ├─ 更新持仓
   │  │  │  │  ├─ portfolio[stock] += qty
   │  │  │  │  └─ cash -= cost
   │  │  │  │
   │  │  │  └─ 计算日资产
   │  │  │     ├─ 持仓市值 = Σ(持仓量 × 收盘价)
   │  │  │     └─ 总资产 = 现金 + 持仓市值
   │  │  │
   │  │  └─ 更新资金曲线
   │  │     └─ equity_curve: {date, equity, cash, ...}
   │  │
   │  └─ 平仓
   │     ├─ 回测结束时
   │     ├─ 卖出所有持仓
   │     └─ 计算最终盈亏
   │
   └─ 返回结果
      ├─ 资金曲线(equity_curve)
      ├─ 交易记录(orders)
      └─ 已平仓交易(trades)

6️⃣ 性能计算阶段
   ├─ PerfMetrics.calculate_all()
   │  ├─ 总收益率 = (final - initial) / initial
   │  ├─ 年化收益 = (1 + total_return)^(252/days) - 1
   │  ├─ Sharp比率 = (年均收益 - rf) / σ (rf=0)
   │  ├─ 最大回撤 = max drawdown during entire period
   │  ├─ 胜率 = 赢利交易数 / 总交易数
   │  ├─ 盈利因子 = 赢利总额 / 亏损总额
   │  ├─ Calmar = 年化收益 / 最大回撤
   │  └─ Sortino = 年化收益 / 下方波动率
   │
   └─ 风险指标
      ├─ VaR (95%) = Value at Risk
      ├─ CVaR = 条件风险价值
      └─ 最大连续亏损

7️⃣ 结果输出阶段
   ├─ 控制台输出
   │  ├─ 绩效指标表格
   │  └─ 交易记录摘要
   │
   ├─ 文件输出
   │  ├─ CSV: 完整交易/资金曲线
   │  ├─ JSON: 性能指标摘要
   │  └─ PNG: 净值/回撤曲线图
   │
   └─ Web仪表盘
      ├─ 实时查看回测结果
      ├─ 交互式图表
      └─ 对比分析
```

---

## 各模块详解

### **模块1: 数据管理** (优先级 P0)

#### 当前实现
- ✅ DataHandler: 加载/清洗/对齐
- ✅ DataDownloader: 定期下载+增量更新
- ✅ 缓存策略: CSV本地 + SQLite元数据

#### 需要补充
1. **数据质量检查** → `DataValidator`
2. **高效查询接口** → 支持日期范围、股票列表快速切片
3. **多源数据支持** → 除QLib外还支持CSV/API导入
4. **复权处理** → 除权除息调整

#### 使用示例
```python
# 下载数据
downloader = DataDownloader()
downloader.download_data(['000858.SZ'], incremental=True)

# 查询已下载数据
handler = DataHandler()
df = handler.load_stock_data(
    stock_codes=['000858.SZ'],
    start_date='2020-01-01',
    end_date='2023-12-31'
)

# 数据验证
validator = DataValidator()
quality_report = validator.check_quality(df)
print(f"缺失率: {quality_report['missing_pct']}%")
```

---

### **模块2: 策略研究与开发** (优先级 P0)

#### 当前实现
- ✅ FeatureEngine: 40+技术指标
- ✅ StrategyBase: 基础类
- ✅ 3个内置策略: Momentum/MeanReversion/Combined

#### 需要补充
1. **自定义因子表达式引擎** → 无代码定义因子
2. **多资产支持框架** → 期货/加密/外汇
3. **机器学习集成** → sklearn/XGBoost接口
4. **策略回测对标** → 与基准比较

#### 使用示例
```python
# 内置策略
strategy = StrategyFactory.create_strategy('momentum')
signals = strategy.generate_signals(df)

# 自定义策略
class MyStrategy(BaseStrategy):
    def generate_signals(self, df):
        # 自定义信号生成逻辑
        df['signal'] = ...
        return df

# ML集成（新增示例）
from sklearn.ensemble import RandomForestClassifier
ml_strategy = MLStrategy(model=RandomForestClassifier())
signals = ml_strategy.generate_signals(df)
```

---

### **模块3: 回测系统** (优先级 P0)

#### 当前实现
- ✅ BacktestEngine: 逐日回测
- ✅ 6个绩效指标: 年化/Sharpe/回撤等
- ✅ 完整交易记录

#### 需要补充
1. **高保真模拟增强**
   - 涨跌停限制
   - 停牌处理
   - 分红配股调整
   - 限价单未成交处理

2. **并行回测** → 多进程加速
3. **压力测试** → 历史压力事件重放
4. **敏感性分析** → 参数变化影响

#### 回测增强示例
```python
engine = BacktestEngine(
    initial_capital=1000000,
    commission=0.001,
    slippage=0.0001,
    handle_limit_up_down=True,      # 新增
    handle_suspension=True,          # 新增
    handle_dividend=True,            # 新增
)
results = engine.run_backtest(df, signals)
```

---

### **模块4: 参数优化** (优先级 P1)

#### 当前实现
- ❌ 无实现

#### 需要实现
1. **GridSearch** - 网格搜索全组合
2. **GeneticAlgorithm** - 遗传算法优化
3. **WalkForward** - 推进分析防过拟合
4. **CrossValidation** - k折交叉验证

#### 新增实现示例
```python
# 1. 网格搜索
param_grid = {
    'short_window': [3, 5, 10],
    'long_window': [15, 20, 30],
    'threshold': [0.01, 0.02, 0.05]
}
optimizer = GridSearchOptimizer(
    strategy='momentum',
    param_grid=param_grid,
    metric='sharpe_ratio',
    n_jobs=4  # 并行
)
results = optimizer.optimize(df)

# 2. 推进分析
optimizer = WalkForwardOptimizer(
    train_period=252,      # 1年训练
    test_period=63,        # 3月测试
    step_size=63
)
results = optimizer.optimize(df)

# 3. 结果
print(results)
# ┌─────────────────────────────────────┐
# │ 最优参数: {short_w: 5, long_w: 20} │
# │ Sharpe比率: 1.52                    │
# │ 样本外Sharpe: 1.38                  │
# │ 过拟合程度: 8.4% ✓ 接受             │
# └─────────────────────────────────────┘
```

---

### **模块5: 风险管理** (优先级 P1)

#### 当前实现
- ⚠️ 仅有佣金/滑点成本

#### 需要实现

**事前风控 (Pre-Trade Checks)**
```python
pre_checker = PreRiskCheck()
pre_checker.add_rule('max_leverage', max_value=2.0)
pre_checker.add_rule('max_position_size', max_value=0.3)
pre_checker.add_rule('sector_exposure', max_value=0.4)
pre_checker.add_rule('correlation_limit', max_corr=0.8)

if pre_checker.check(order) == 'REJECTED':
    print(f"订单被拒绝: {order}")
```

**事中风控 (Real-Time Monitoring)**
```python
runtime_monitor = RuntimeMonitor()
runtime_monitor.set_alert('daily_loss', -0.05)     # 日亏5%
runtime_monitor.set_alert('margin_level', 0.2)     # 保证金20%
runtime_monitor.set_alert('equity_drop', -0.1)     # 权益下降10%

while trading:
    alerts = runtime_monitor.check(portfolio)
    if alerts:
        executor.halt_trading()  # 自动停止
```

**事后分析 (Attribution)**
```python
attr_analyzer = RiskAttribution()
attr_report = attr_analyzer.analyze(
    portfolio=portfolio,
    returns=returns,
    factors=factor_exposures
)
print(attr_report)
# 收益分解:
#  资产配置贡献: +2.5%
#  选股贡献: +3.2%
#  风格/因子暴露: -0.8%
```

---

### **模块6-9: 高级功能** (优先级 P2-P3)

#### 6. 实盘交易执行
- 多经纪商API包装 (石头期货、同花顺等)
- 订单路由和拆单算法
- 实时延迟监控

#### 7. 绩效归因与报告
- Brinson收益归因模型
- Fama-French因子暴露分析
- 自动PDF/HTML报告生成

#### 8. 运维与监控
- Docker容器化 (Dockerfile + docker-compose.yml)
- Kubernetes支持
- 分布式任务调度 (Celery)

#### 9. 辅助功能
- 策略库版本管理 (Git集成)
- 策略快照和对比
- 实时仪表板 (WebSocket推送)

---

## 快速开始

### **场景A: 我想下载历史数据** (用户需求1)

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置下载参数 (config/default_config.yaml)
stocks:
  - 000858.SZ
  - 000651.SZ
  - 600519.SH

# 3. 执行下载
python -c "
from src.qlib_backtest.data.downloader import DataDownloader
d = DataDownloader()
d.download_data(['000858.SZ', '000651.SZ'], incremental=True)
print('✓ 数据下载完成')
"

# 4. 查看缓存位置
ls ~/.cache/qlib_backtest/data/
# 000858.SZ.csv  000651.SZ.csv
```

### **场景B: 我想执行量化回测** (用户需求2)

```bash
# 1. 确保数据已下载（见场景A）

# 2. 执行回测
python examples/basic_backtest.py

# 3. 查看结果
cat results/momentum_strategy_*.json | python -m json.tool

# 4. Web查看
python examples/web_frontend.py
# 打开: http://localhost:5000/download-manager
#      http://localhost:5000/backtest
```

### **场景C: 我想优化策略参数** (新增需求)

```bash
# 后续实现 (见模块4)
python examples/optimization_example.py --strategy momentum --metric sharpe_ratio
```

---

## 最佳实践

### 最佳实践 1: 数据始终要验证

```python
from src.qlib_backtest.data import DataHandler, DataValidator

handler = DataHandler()
df = handler.load_stock_data(['000858.SZ'], '2020-01-01', '2023-12-31')
df = handler.clean_data(df)

# ✓ 始终验证
validator = DataValidator()
report = validator.check_quality(df)
assert report['missing_pct'] < 1.0, "缺失率过高"
assert report['outlier_count'] < 10, "异常值过多"
print(f"✓ 数据质量检查通过: {report}")
```

### 最佳实践 2: 回测中分离训练/测试集

```python
# ✗ 错误做法：全数据回测然后优化参数（过拟合）
df_all = load_data('2020-01-01', '2023-12-31')
best_params = optimize_params(df_all)  # 错误！

# ✓ 正确做法：WalkForward或时间分割
df_train = load_data('2020-01-01', '2022-12-31')
df_test = load_data('2023-01-01', '2023-12-31')

# 在train上优化
best_params = optimize_params(df_train)

# 在test上验证
results = backtest(df_test, best_params)
print(f"样本外Sharpe: {results.sharpe_ratio}")
```

### 最佳实践 3: 始终关注关键风险指标

```python
results = backtest(df, signals)

# ✓ 必看指标
print(f"Sharpe比率 (>1.0好): {results.sharpe_ratio:.2f}")
print(f"最大回撤 (<30%好): {results.max_drawdown:.2%}")
print(f"年化收益 (>10%好): {results.annual_return:.2%}")
print(f"胜率 (>50%好): {results.win_rate:.2%}")

# ⚠️ 警告
if results.sharpe_ratio < 0.5:
    print("⚠️ Sharpe比率过低，策略信号质量差")
if results.max_drawdown > 0.5:
    print("⚠️ 最大回撤过大，风险过高")
if results.win_rate < 0.3:
    print("⚠️ 胜率过低，亏损交易太多")
```

---

## 性能优化

### 优化 1: 数据加载缓存

```python
# ✗ 低效: 每次都从磁盘读取
for i in range(100):
    df = DataHandler().load_stock_data(['000858.SZ'])

# ✓ 高效: 使用缓存
handler = DataHandler()
df = handler.load_stock_data(['000858.SZ'])
# 后续调用自动使用内存缓存（若已实现）
```

### 优化 2: 因子计算缓存

```python
# ✗ 低效: 重复计算相同因子
for params in param_combinations:
    df = feature_engine.calculate_all_features(df)

# ✓ 高效: 接口缓存（若支持）
feature_engine.enable_cache()
for params in param_combinations:
    df = feature_engine.calculate_all_features(df)  # 首次计算，后续读缓存
```

### 优化 3: 并行回测

```python
# ✗ 低效: 串行测试
results = []
for params in param_combinations:  # 1000组
    result = backtest(df, params)  # 每个5s
    results.append(result)
# 总耗时: 5000s = 1.4小时

# ✓ 高效: 并行测试（后续实现）
optimizer = GridSearchOptimizer(n_jobs=8)
results = optimizer.optimize(df, param_grid)
# 总耗时: 5000s / 8 ≈ 625s = 10分钟
```

---

## 扩展指南

### 如何添加新策略?

```python
# 1. 新建文件: src/qlib_backtest/strategies/my_strategy.py

from .base import BaseStrategy

class MyStrategy(BaseStrategy):
    """自定义策略"""
    
    def __init__(self, param1=10, param2=0.02):
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, df):
        """生成交易信号"""
        # 你的策略逻辑
        df['signal'] = ...
        return df

# 2. 注册: 在StrategyFactory中添加
# 3. 使用: strategy = StrategyFactory.create_strategy('my_strategy')
```

### 如何添加新因子?

```python
# 在 FeatureEngine 中添加方法

def calculate_my_factor(self, df):
    """计算自定义因子"""
    df['my_factor'] = df['close'].rolling(10).mean() / df['close']
    return df
```

### 如何集成新数据源?

```python
# 1. 创建新的DataProvider
class SinaDataProvider:
    def load_data(self, stock_code, start_date, end_date):
        # 调用新浪API
        return df

# 2. 在DataHandler中支持
handler = DataHandler(data_provider=SinaDataProvider())
```

---

## 总结

本架构设计覆盖了量化交易系统所需的9大核心模块。当前实现重点突出：

| 模块 | 完成度 | 下步优先|
|------|-------|--------|
| 数据管理 | ✅ 80% | 补充数据验证、复权 |
| 策略研究 | ✅ 75% | 支持ML模型、自定义因子 |
| 回测系统 | ✅ 85% | 涨跌停、停牌、分红 |
| 参数优化 | ⚠️ 10% | **实现GridSearch/WalkForward** |
| 风险管理 | ⚠️ 25% | **实现事前/事中/事后风控** |
| 实盘交易 | ❌ 5% | 长期规划，可选 |
| 绩效归因 | ⚠️ 30% | 补充因子分解、归因分析 |
| 运维监控 | ⚠️ 30% | Docker化、分布式调度 |
| 辅助功能 | ⚠️ 40% | 策略库管理、版本控制 |

---

**需要帮助？** 查看 examples/ 中的示例脚本或 README.md for详细说明

