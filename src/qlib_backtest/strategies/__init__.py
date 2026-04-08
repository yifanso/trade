"""
策略模块：定义和实现各种交易策略
"""

import logging
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    """交易信号数据类"""
    date: str
    stock_code: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0-1之间的置信度
    price: float
    quantity: Optional[int] = None


class BaseStrategy(ABC):
    """
    基础策略类：所有策略应继承此类
    """
    
    def __init__(self, name: str):
        """
        初始化策略
        
        Args:
            name: 策略名称
        """
        self.name = name
        self.parameters = {}
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        生成交易信号
        
        Args:
            df: 包含特征的数据DataFrame
            
        Returns:
            交易信号列表
        """
        pass
    
    def set_parameters(self, **kwargs):
        """设置策略参数"""
        self.parameters.update(kwargs)
        logger.info(f"策略 {self.name} 参数已更新: {kwargs}")


class MomentumStrategy(BaseStrategy):
    """
    动量策略：基于价格动量生成交易信号
    
    特征:
    - 买入信号: 当价格突破上升趋势时
    - 卖出信号: 当价格突破下降趋势时
    """
    
    def __init__(self):
        super().__init__("MomentumStrategy")
        self.parameters = {
            'short_window': 5,      # 短期窗口
            'long_window': 20,      # 长期窗口
            'threshold': 0.02,      # 动量阈值
        }
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """生成动量策略信号"""
        signals = []
        
        if 'close' not in df.columns or 'stock_code' not in df.columns:
            return signals
        
        short_w = self.parameters['short_window']
        long_w = self.parameters['long_window']
        threshold = self.parameters['threshold']
        
        # 计算短期和长期移动平均
        df_copy = df.copy()
        df_copy['sma_short'] = df_copy.groupby('stock_code')['close'].transform(
            lambda x: x.rolling(short_w).mean()
        )
        df_copy['sma_long'] = df_copy.groupby('stock_code')['close'].transform(
            lambda x: x.rolling(long_w).mean()
        )
        
        # 计算动量
        df_copy['momentum'] = (df_copy['sma_short'] - df_copy['sma_long']) / df_copy['sma_long']
        
        # 生成信号
        for idx, row in df_copy.iterrows():
            if pd.isna(row['momentum']) or pd.isna(row['close']):
                continue
            
            if row['momentum'] > threshold:
                signal_type = 'BUY'
                confidence = min(1.0, abs(row['momentum']) / threshold)
            elif row['momentum'] < -threshold:
                signal_type = 'SELL'
                confidence = min(1.0, abs(row['momentum']) / threshold)
            else:
                signal_type = 'HOLD'
                confidence = 0.5
            
            signals.append(Signal(
                date=str(row['date']) if 'date' in row else str(idx),
                stock_code=row['stock_code'],
                signal_type=signal_type,
                confidence=confidence,
                price=row['close'],
            ))
        
        logger.info(f"MomentumStrategy生成 {len(signals)} 条信号")
        return signals


class MeanReversionStrategy(BaseStrategy):
    """
    均值回归策略：基于价格偏离均值的程度生成信号
    
    特征:
    - 买入信号: 当价格低于均值较多时
    - 卖出信号: 当价格高于均值较多时
    """
    
    def __init__(self):
        super().__init__("MeanReversionStrategy")
        self.parameters = {
            'window': 20,              # 移动平均窗口
            'std_multiple': 2,         # 标准差倍数
        }
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """生成均值回归策略信号"""
        signals = []
        
        if 'close' not in df.columns or 'stock_code' not in df.columns:
            return signals
        
        window = self.parameters['window']
        std_mult = self.parameters['std_multiple']
        
        df_copy = df.copy()
        df_copy['sma'] = df_copy.groupby('stock_code')['close'].transform(
            lambda x: x.rolling(window).mean()
        )
        df_copy['std'] = df_copy.groupby('stock_code')['close'].transform(
            lambda x: x.rolling(window).std()
        )
        df_copy['upper_band'] = df_copy['sma'] + std_mult * df_copy['std']
        df_copy['lower_band'] = df_copy['sma'] - std_mult * df_copy['std']
        
        # 生成信号
        for idx, row in df_copy.iterrows():
            if pd.isna(row['sma']) or pd.isna(row['close']):
                continue
            
            price_to_mean = (row['close'] - row['sma']) / row['sma']
            
            if row['close'] < row['lower_band']:
                signal_type = 'BUY'
                confidence = min(1.0, abs(price_to_mean) / (std_mult * 0.01))
            elif row['close'] > row['upper_band']:
                signal_type = 'SELL'
                confidence = min(1.0, abs(price_to_mean) / (std_mult * 0.01))
            else:
                signal_type = 'HOLD'
                confidence = 0.5
            
            signals.append(Signal(
                date=str(row['date']) if 'date' in row else str(idx),
                stock_code=row['stock_code'],
                signal_type=signal_type,
                confidence=confidence,
                price=row['close'],
            ))
        
        logger.info(f"MeanReversionStrategy生成 {len(signals)} 条信号")
        return signals


class CombinedStrategy(BaseStrategy):
    """
    组合策略：结合多个子策略的信号
    """
    
    def __init__(self, strategies: Optional[List[BaseStrategy]] = None):
        super().__init__("CombinedStrategy")
        self.sub_strategies = strategies or []
        self.parameters = {
            'voting_threshold': 0.5,  # 投票阈值
        }
    
    def add_strategy(self, strategy: BaseStrategy):
        """添加子策略"""
        self.sub_strategies.append(strategy)
    
    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        生成组合策略信号：多策略投票
        """
        if not self.sub_strategies:
            logger.warning("组合策略中没有子策略")
            return []
        
        # 收集所有子策略的信号
        all_signals = {}
        for strategy in self.sub_strategies:
            signals = strategy.generate_signals(df)
            for signal in signals:
                key = (signal.date, signal.stock_code)
                if key not in all_signals:
                    all_signals[key] = {'BUY': 0, 'SELL': 0, 'HOLD': 0, 'signals': []}
                all_signals[key][signal.signal_type] += 1
                all_signals[key]['signals'].append(signal)
        
        # 进行投票
        combined_signals = []
        voting_threshold = self.parameters['voting_threshold']
        
        for (date, code), signal_data in all_signals.items():
            signals_list = signal_data['signals']
            if not signals_list:
                continue
            
            first_signal = signals_list[0]
            total = len(self.sub_strategies)
            
            buy_ratio = signal_data['BUY'] / total
            sell_ratio = signal_data['SELL'] / total
            
            if buy_ratio > voting_threshold:
                final_signal = 'BUY'
                confidence = buy_ratio
            elif sell_ratio > voting_threshold:
                final_signal = 'SELL'
                confidence = sell_ratio
            else:
                final_signal = 'HOLD'
                confidence = 0.5
            
            combined_signals.append(Signal(
                date=date,
                stock_code=code,
                signal_type=final_signal,
                confidence=confidence,
                price=first_signal.price,
            ))
        
        logger.info(f"CombinedStrategy生成 {len(combined_signals)} 条信号")
        return combined_signals


class StrategyFactory:
    """
    策略工厂：创建和管理策略对象
    """
    
    _registry: Dict[str, type] = {
        'momentum': MomentumStrategy,
        'mean_reversion': MeanReversionStrategy,
    }
    
    @classmethod
    def create_strategy(cls, strategy_name: str, **kwargs) -> BaseStrategy:
        """
        创建策略对象
        
        Args:
            strategy_name: 策略名称
            **kwargs: 策略参数
            
        Returns:
            策略对象
        """
        if strategy_name not in cls._registry:
            raise ValueError(f"未知的策略: {strategy_name}")
        
        strategy = cls._registry[strategy_name]()
        if kwargs:
            strategy.set_parameters(**kwargs)
        
        return strategy
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """注册自定义策略"""
        cls._registry[name] = strategy_class
    
    @classmethod
    def list_strategies(cls) -> List[str]:
        """列出所有可用策略"""
        return list(cls._registry.keys())
