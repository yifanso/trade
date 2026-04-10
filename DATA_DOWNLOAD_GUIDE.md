## QLib 数据定期下载功能

本文档介绍如何使用新增的**数据定期下载功能**，实现从QLib主动定期下载和更新交易数据。

## 功能概览

### 核心特性

✅ **定时自动下载** - 支持Cron表达式配置灵活的下载时间  
✅ **增量更新** - 智能检测上次下载时间，只更新最新数据  
✅ **批量处理** - 支持同时监控多个股票  
✅ **缓存管理** - 本地缓存机制加速数据访问  
✅ **完整日志** - SQLite数据库记录所有下载操作  
✅ **后台运行** - 独立线程运行，不阻塞主程序  
✅ **错误处理** - 完善的异常处理和重试机制  

## 安装

首先安装必要的依赖包：

```bash
# 安装apscheduler用于定时任务
pip install apscheduler>=3.10.0

# 或者直接安装所有依赖
pip install -r requirements.txt
```

## 快速开始

### 1. 基础使用 - 单次下载

```python
from src.qlib_backtest.data.downloader import DataDownloader

# 创建下载器
downloader = DataDownloader()

# 下载数据
results = downloader.download_data(
    stock_codes="000858.SZ",  # 五粮液
    start_date="2024-01-01",
    end_date="2024-12-31",
    incremental=False,  # 不使用增量更新
)

# 查看结果
for code, df in results.items():
    print(f"股票: {code}, 记录数: {len(df)}")
    print(df.head())
```

### 2. 增量更新 - 智能更新最新数据

```python
# 第一次下载
downloader.download_data(
    stock_codes="000858.SZ",
    start_date="2024-01-01",
    incremental=False,  # 首次下载
)

# 稍后再更新（会自动从上次日期继续下载）
downloader.download_data(
    stock_codes="000858.SZ",
    incremental=True,  # 使用增量更新
)
```

### 3. 定时自动下载

```python
# 启动定时任务
downloader.start_scheduler(
    stock_codes=["000858.SZ", "000651.SZ"],
    cron_expression="0 16 * * 1-5",  # 每个工作日下午4点
    incremental=True,  # 启用增量更新
)

# 程序会在后台运行，定期自动下载数据
# ...

# 停止任务
downloader.stop_scheduler()
```

### 4. 批量管理 - 使用更新管理器

```python
from src.qlib_backtest.data.downloader import DataUpdateManager

downloader = DataDownloader()
manager = DataUpdateManager(downloader)

# 添加监控股票
manager.add_stocks(["000858.SZ", "000651.SZ", "600519.SH"])

# 启动监控
manager.start_monitoring(cron_expression="0 16 * * 1-5")

# 手动触发一次更新
results = manager.manual_update()

# 查看监控列表
stocks = manager.get_watch_list()

# 停止监控
manager.stop_monitoring()
```

## API 参考

### DataDownloader 类

#### 初始化

```python
downloader = DataDownloader(
    qlib_data_path=None,      # QLib数据路径，默认 ~/.qlib/qlib_data
    data_cache_dir=None,       # 数据缓存目录，默认 ~/.cache/qlib_backtest/data
    db_path=None,              # 数据库路径，默认 ~/.cache/qlib_backtest/download_history.db
)
```

#### download_data() - 下载数据

```python
results = downloader.download_data(
    stock_codes,          # 股票代码或列表，如 "000858.SZ" 或 ["000858.SZ", "000651.SZ"]
    start_date=None,      # 开始日期，格式 "YYYY-MM-DD"
    end_date=None,        # 结束日期，默认为今天
    freq="day",           # 数据频率，"day"/"week"/"month"
    incremental=True,     # 是否启用增量更新
)

# 返回值: {stock_code: DataFrame} 的字典
# 每个DataFrame包含列: date, code, open, close, high, low, volume 等
```

#### start_scheduler() - 启动定时任务

```python
success = downloader.start_scheduler(
    stock_codes,                          # 股票代码列表
    cron_expression="0 16 * * 1-5",     # Cron表达式
    start_date=None,                      # 开始日期（可选）
    **kwargs                              # 其他参数传递给download_data
)
```

#### 其他常用方法

```python
# 停止定时任务
downloader.stop_scheduler()

# 获取下载器状态
status = downloader.get_download_status()
# 返回: {'running': bool, 'scheduler_active': bool, 'recent_downloads': [...]}

# 获取下载统计
stats = downloader.get_download_statistics()
# 返回: {'unique_stocks': int, 'total_downloads': int, 'successful': int, ...}

# 获取上次下载日期
last_date = downloader.get_last_download_date("000858.SZ")
```

### DataUpdateManager 类

```python
manager = DataUpdateManager(downloader)

# 添加监控股票
manager.add_stocks(["000858.SZ", "000651.SZ"])

# 移除监控股票
manager.remove_stocks("000858.SZ")

# 获取监控列表
watch_list = manager.get_watch_list()

# 启动监控
manager.start_monitoring(cron_expression="0 16 * * 1-5")

# 停止监控
manager.stop_monitoring()

# 手动更新
results = manager.manual_update()
```

## Cron表达式

Cron表达式用于指定定时任务的执行时间，格式为：

```
minute hour day month weekday
```

各字段含义：
- **minute** (0-59): 分钟
- **hour** (0-23): 小时
- **day** (1-31): 日期
- **month** (1-12): 月份
- **weekday** (0-6): 周几，0=周日，1-5=周一到周五，6=周六

### 常用Cron表达式

| 表达式 | 含义 |
|-------|------|
| `0 16 * * 1-5` | 每个工作日下午4点（股市收盘后） |
| `0 9 * * *` | 每天上午9点 |
| `0 9,15 * * *` | 每天上午9点和下午3点 |
| `*/30 * * * *` | 每30分钟 |
| `0 0 * * *` | 每天午夜 |
| `0 0 * * 0` | 每周日午夜 |
| `0 0 1 * *` | 每月第一天 |
| `0 6 1-7 * 1` | 每月第一个周一早上6点 |

### 对于QLib股票数据的建议

- **工作日数据更新**: `0 16 * * 1-5` - 股市收盘后更新
- **每日数据**: `0 9 * * *` - 每天上午9点
- **高频更新**: `*/30 8-16 * * 1-5` - 只在工作时间每30分钟更新

## 示例

### 示例1: 监控热门股票

```python
from src.qlib_backtest.data.downloader import DataDownloader

downloader = DataDownloader()

# 热门股票
stocks = ["000858.SZ", "000651.SZ", "600519.SH"]

# 启动监控，每个工作日下午4点自动更新
downloader.start_scheduler(
    stock_codes=stocks,
    cron_expression="0 16 * * 1-5",
    incremental=True,
)

print("定时下载已启动，按 Ctrl+C 停止")
import time
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    downloader.stop_scheduler()
    print("已停止")
```

### 示例2: 批量初始化历史数据

```python
# 一次性下载大量历史数据
stocks = [f"{code}.SZ" for code in range(1, 100)]

results = downloader.download_data(
    stock_codes=stocks,
    start_date="2020-01-01",
    end_date="2024-12-31",
    incremental=False,
)

successful = sum(1 for df in results.values() if df is not None)
print(f"成功下载 {successful}/{len(stocks)} 只股票")
```

### 示例3: 获取下载统计

```python
# 显示下载统计信息
stats = downloader.get_download_statistics()

print(f"监控股票数: {stats['unique_stocks']}")
print(f"总下载次数: {stats['total_downloads']}")
print(f"成功: {stats['successful']}, 失败: {stats['failed']}")
print(f"平均耗时: {stats['avg_duration_seconds']:.2f}秒")
print(f"最后更新时间: {stats['last_download']}")
```

## 数据存储

### 缓存位置

| 类型 | 路径 |
|------|------|
| 股票数据 | `~/.cache/qlib_backtest/data/{stock_code}_data.csv` |
| 下载历史 | `~/.cache/qlib_backtest/download_history.db` |

### 查看缓存数据

```python
import pandas as pd

# 直接读取缓存文件
df = pd.read_csv("~/.cache/qlib_backtest/data/000858_SZ_data.csv")
print(df.tail(10))
```

### 查询下载历史

```python
import sqlite3

db_path = "~/.cache/qlib_backtest/download_history.db"
conn = sqlite3.connect(db_path)

# 查看最近的下载
query = "SELECT * FROM download_logs ORDER BY timestamp DESC LIMIT 10"
logs = pd.read_sql_query(query, conn)
print(logs)

# 查看股票的下载状态
query = "SELECT stock_code, last_download_date, status FROM download_history"
status = pd.read_sql_query(query, conn)
print(status)
```

## 错误处理

### 常见问题

**问题1: QLib未安装**
```
QLib未安装，请执行: pip install qlib
```

**解决**: 
```bash
pip install qlib==0.0.2.dev20
```

**问题2: APScheduler未安装**
```
APScheduler未安装，请执行: pip install apscheduler
```

**解决**:
```bash
pip install apscheduler>=3.10.0
```

**问题3: 数据为空**
- 检查股票代码格式是否正确（如 "000858.SZ"）
- 确认日期范围内有数据
- 查看日志了解详细错误信息

### 日志设置

```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('qlib_backtest.data.downloader')

# 查看详细日志
downloader = DataDownloader()
downloader.download_data(["000858.SZ"], incremental=True)
```

## 性能优化

### 批量下载优化

```python
# 批量下载多个股票（推荐）
stocks = ["000858.SZ", "000651.SZ", "600519.SH"]
downloader.download_data(stocks, incremental=True)

# 避免逐个下载
for stock in stocks:
    downloader.download_data(stock)  # 不推荐
```

### 增量更新优化

```python
# 启用增量更新显著提高性能
# 第一次下载可能需要较长时间，之后只更新新数据

downloader.download_data("000858.SZ", incremental=True)
```

### 缓存利用

```python
# 数据会自动缓存在本地
# 再次调用相同股票时会使用缓存
# 直接使用缓存避免重复下载

cached_df = downloader._load_cached_data("000858.SZ")
```

## 与回测系统集成

### 自动更新回测数据

```python
from src.qlib_backtest.backtest import BacktestEngine
from src.qlib_backtest.data.downloader import DataDownloader

# 创建下载器
downloader = DataDownloader()

# 启动定时更新
downloader.start_scheduler(
    stock_codes=["000858.SZ", "000651.SZ"],
    cron_expression="0 16 * * 1-5",
    incremental=True,
)

# 回测时自动使用最新数据
engine = BacktestEngine()
# 数据会使用本地最新缓存
```

## 实际应用场景

### 场景1: 实时研究监控

```python
# 每30分钟更新热门股票数据
manager.start_monitoring(cron_expression="*/30 * * * *")
```

### 场景2: 每日定期更新

```python
# 每天下午4点更新数据（股市收盘后）
downloader.start_scheduler(
    stock_codes=stock_list,
    cron_expression="0 16 * * 1-5",  # 只在工作日
    incremental=True,
)
```

### 场景3: 定期回测更新

```python
# 每周运行一次回测前自动更新数据
downloader.start_scheduler(
    stock_codes=stock_list,
    cron_expression="0 0 * * 0",  # 每周日午夜
    incremental=True,
)
```

## 运行示例

```bash
# 运行示例脚本
python examples/data_download_example.py

# 交互式选择要运行的示例
# 1. 单次下载
# 2. 增量更新
# 3. 批量下载
# 4. 定时下载
# 5. 使用管理器
# 6. 自定义调度
```

## 总结

数据定期下载功能提供了：

✅ **灵活的下载控制** - 一次性、增量、定时等多种方式  
✅ **自动化管理** - 后台定时运行，无需人工干预  
✅ **完整的追踪** - 数据库记录所有操作和统计信息  
✅ **与系统集成** - 与回测系统无缝配合  

使用本功能，您可以轻松构建一个自动化的量化交易数据获取系统！
