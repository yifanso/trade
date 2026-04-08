"""
实用工具模块：记录、配置管理等辅助功能
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


def setup_logging(
    log_dir: str = "./logs",
    level: int = logging.INFO,
) -> None:
    """
    设置日志系统
    
    Args:
        log_dir: 日志目录
        level: 日志级别
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ]
    )


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config = {}
        if config_file:
            self.load_config(config_file)
    
    def load_config(self, config_file: str) -> None:
        """加载配置文件"""
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.endswith('.json'):
                self.config = json.load(f)
            elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                self.config = yaml.safe_load(f)
            else:
                raise ValueError("不支持的配置文件格式")
        
        logging.info(f"配置已加载: {config_file}")
    
    def save_config(self, config_file: str) -> None:
        """保存配置文件"""
        Path(config_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            if config_file.endswith('.json'):
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return self.config.copy()


class ResultsExporter:
    """回测结果导出器"""
    
    def __init__(self, output_dir: str = "./results"):
        """
        初始化导出器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def export_results(
        self,
        backtest_result,
        strategy_name: str,
    ) -> None:
        """
        导出回测结果
        
        Args:
            backtest_result: 回测结果对象
            strategy_name: 策略名称
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{strategy_name}_{timestamp}"
        
        # 导出汇总
        summary = backtest_result.to_dict()
        summary_file = os.path.join(self.output_dir, f"{base_name}_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # 导出资金曲线
        if not backtest_result.equity_curve.empty:
            equity_file = os.path.join(self.output_dir, f"{base_name}_equity.csv")
            backtest_result.equity_curve.to_csv(equity_file, index=False)
        
        # 导出交易记录
        if backtest_result.trades:
            trades_df = pd.DataFrame(backtest_result.trades)
            trades_file = os.path.join(self.output_dir, f"{base_name}_trades.csv")
            trades_df.to_csv(trades_file, index=False)
        
        logging.info(f"结果已导出到: {self.output_dir}")
        return base_name


import pandas as pd


class PerformanceAnalyzer:
    """性能分析器"""
    
    @staticmethod
    def analyze_strategy(
        equity_curve: pd.DataFrame,
        benchmark_returns: Optional[pd.Series] = None,
    ) -> Dict[str, float]:
        """
        分析策略性能
        
        Args:
            equity_curve: 资金曲线数据
            benchmark_returns: 基准收益率序列
            
        Returns:
            性能指标字典
        """
        metrics = {}
        
        if equity_curve.empty:
            return metrics
        
        # 计算收益率
        returns = equity_curve['total_value'].pct_change().dropna()
        
        metrics['annual_volatility'] = returns.std() * np.sqrt(252)
        metrics['daily_sharpe'] = returns.mean() / returns.std() if returns.std() > 0 else 0
        metrics['calmar_ratio'] = _calculate_calmar_ratio(equity_curve['total_value'])
        metrics['sortino_ratio'] = _calculate_sortino_ratio(returns)
        
        # 按月的收益率
        if 'date' in equity_curve.columns:
            equity_curve['date'] = pd.to_datetime(equity_curve['date'])
            monthly_returns = equity_curve.set_index('date')['total_value'].resample('M').last().pct_change()
            metrics['positive_months'] = (monthly_returns > 0).sum() / len(monthly_returns) if len(monthly_returns) > 0 else 0
        
        return metrics


def _calculate_calmar_ratio(equity: pd.Series) -> float:
    """计算Calmar比率"""
    returns = equity.pct_change().dropna()
    annual_return = (equity.iloc[-1] / equity.iloc[0]) ** (252 / len(equity)) - 1
    
    running_max = equity.expanding().max()
    drawdown = (equity - running_max) / running_max
    max_drawdown = drawdown.min()
    
    return annual_return / abs(max_drawdown) if max_drawdown < 0 else 0


def _calculate_sortino_ratio(returns: pd.Series) -> float:
    """计算Sortino比率"""
    downside_returns = returns[returns < 0]
    if len(downside_returns) == 0:
        return 0
    
    downside_std = downside_returns.std()
    return returns.mean() / downside_std * np.sqrt(252) if downside_std > 0 else 0


import numpy as np
