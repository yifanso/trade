"""
特征工程模块：生成用于策略的技术指标和特征
"""

import logging
import numpy as np
import pandas as pd
from typing import Union, List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class FeatureEngine:
    """
    特征引擎：计算技术指标和其他特征
    """
    
    def __init__(self):
        """初始化特征引擎"""
        self.features = {}
    
    def calculate_all_features(
        self,
        df: pd.DataFrame,
        feature_config: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        计算所有特征
        
        Args:
            df: 输入数据DataFrame
            feature_config: 特征配置字典
            
        Returns:
            包含所有特征的DataFrame
        """
        df = df.copy()
        
        # 默认特征配置
        if feature_config is None:
            feature_config = {
                'momentum': {'windows': [5, 10, 20]},
                'volatility': {'windows': [10, 20]},
                'trend': {'windows': [5, 10, 20]},
                'volume': {'windows': [5, 20]},
            }
        
        # 计算各类特征
        for feature_type, params in feature_config.items():
            if feature_type == 'momentum':
                df = self._add_momentum_features(df, params.get('windows', [5, 10, 20]))
            elif feature_type == 'volatility':
                df = self._add_volatility_features(df, params.get('windows', [10, 20]))
            elif feature_type == 'trend':
                df = self._add_trend_features(df, params.get('windows', [5, 10, 20]))
            elif feature_type == 'volume':
                df = self._add_volume_features(df, params.get('windows', [5, 20]))
        
        logger.info(f"特征计算完成，生成 {len(df.columns)} 列")
        return df
    
    def _add_momentum_features(
        self,
        df: pd.DataFrame,
        windows: List[int],
    ) -> pd.DataFrame:
        """添加动量特征"""
        df = df.copy()
        
        if 'close' not in df.columns:
            return df
        
        for window in windows:
            # RSI - 相对强弱指数
            df[f'rsi_{window}'] = self._calculate_rsi(df, 'close', window)
            
            # MACD - 指数移动平均线
            df[f'macd_{window}'] = self._calculate_macd(df, 'close', window)
            
            # Momentum
            df[f'momentum_{window}'] = self._calculate_momentum(df, 'close', window)
        
        return df
    
    def _add_volatility_features(
        self,
        df: pd.DataFrame,
        windows: List[int],
    ) -> pd.DataFrame:
        """添加波动率特征"""
        df = df.copy()
        
        if 'close' not in df.columns:
            return df
        
        for window in windows:
            # 标准差 (简单波动率)
            df[f'std_{window}'] = df.groupby('stock_code')['close'].transform(
                lambda x: x.rolling(window).std()
            )
            
            # 布林带上下界
            sma = df.groupby('stock_code')['close'].transform(
                lambda x: x.rolling(window).mean()
            )
            std = df[f'std_{window}']
            df[f'bb_upper_{window}'] = sma + 2 * std
            df[f'bb_lower_{window}'] = sma - 2 * std
        
        return df
    
    def _add_trend_features(
        self,
        df: pd.DataFrame,
        windows: List[int],
    ) -> pd.DataFrame:
        """添加趋势特征"""
        df = df.copy()
        
        if 'close' not in df.columns:
            return df
        
        for window in windows:
            # 简单移动平均线 (SMA)
            df[f'sma_{window}'] = df.groupby('stock_code')['close'].transform(
                lambda x: x.rolling(window).mean()
            )
            
            # 指数移动平均线 (EMA)
            df[f'ema_{window}'] = df.groupby('stock_code')['close'].transform(
                lambda x: x.ewm(span=window, adjust=False).mean()
            )
            
            # 价格相对于SMA的位置
            sma = df[f'sma_{window}']
            df[f'price_to_sma_{window}'] = df['close'] / sma - 1
        
        return df
    
    def _add_volume_features(
        self,
        df: pd.DataFrame,
        windows: List[int],
    ) -> pd.DataFrame:
        """添加成交量特征"""
        df = df.copy()
        
        if 'volume' not in df.columns:
            return df
        
        for window in windows:
            # 平均成交量
            df[f'avg_volume_{window}'] = df.groupby('stock_code')['volume'].transform(
                lambda x: x.rolling(window).mean()
            )
            
            # 成交量相对强度
            df[f'volume_ratio_{window}'] = df['volume'] / df[f'avg_volume_{window}']
        
        return df
    
    @staticmethod
    def _calculate_rsi(
        df: pd.DataFrame,
        column: str,
        window: int,
        smoothing: int = 3,
    ) -> pd.Series:
        """
        计算RSI指标
        
        Args:
            df: 数据DataFrame
            column: 要计算的列名
            window: 窗口大小
            smoothing: 平滑周期
            
        Returns:
            RSI Series
        """
        delta = df.groupby('stock_code')[column].diff()
        
        gain = delta.copy()
        loss = delta.copy()
        
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        loss = abs(loss)
        
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def _calculate_macd(
        df: pd.DataFrame,
        column: str,
        window: int,
    ) -> pd.Series:
        """
        计算MACD指标
        
        Args:
            df: 数据DataFrame
            column: 列名
            window: 窗口大小
            
        Returns:
            MACD Series
        """
        exp1 = df.groupby('stock_code')[column].transform(
            lambda x: x.ewm(span=12, adjust=False).mean()
        )
        exp2 = df.groupby('stock_code')[column].transform(
            lambda x: x.ewm(span=26, adjust=False).mean()
        )
        macd = exp1 - exp2
        
        return macd
    
    @staticmethod
    def _calculate_momentum(
        df: pd.DataFrame,
        column: str,
        window: int,
    ) -> pd.Series:
        """
        计算动量指标
        
        Args:
            df: 数据DataFrame
            column: 列名
            window: 窗口大小
            
        Returns:
            Momentum Series
        """
        momentum = df.groupby('stock_code')[column].diff(window)
        
        return momentum
    
    def normalize_features(
        self,
        df: pd.DataFrame,
        feature_columns: Optional[List[str]] = None,
        method: str = 'zscore',
    ) -> pd.DataFrame:
        """
        特征归一化
        
        Args:
            df: 含有特征的DataFrame
            feature_columns: 要归一化的列名列表，默认为全部数值列
            method: 归一化方法 ('zscore' 或 'minmax')
            
        Returns:
            归一化后的DataFrame
        """
        df = df.copy()
        
        if feature_columns is None:
            feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in feature_columns:
            if col not in df.columns:
                continue
            
            if method == 'zscore':
                mean = df[col].mean()
                std = df[col].std()
                df[f'{col}_norm'] = (df[col] - mean) / (std + 1e-8)
            elif method == 'minmax':
                min_val = df[col].min()
                max_val = df[col].max()
                df[f'{col}_norm'] = (df[col] - min_val) / (max_val - min_val + 1e-8)
        
        return df
    
    def select_features(
        self,
        df: pd.DataFrame,
        target: str,
        method: str = 'correlation',
        top_k: int = 10,
    ) -> List[str]:
        """
        特征选择
        
        Args:
            df: 包含特征和目标的DataFrame
            target: 目标列名
            method: 选择方法 ('correlation' 或 'importance')
            top_k: 选择Top K个特征
            
        Returns:
            选中的特征列表
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if target not in df.columns:
            logger.warning(f"目标列 {target} 不存在")
            return numeric_cols[:top_k]
        
        if method == 'correlation':
            correlations = df[numeric_cols].corrwith(df[target]).abs()
            top_features = correlations.nlargest(top_k).index.tolist()
        else:
            # 简单的差异性度量
            variations = df[numeric_cols].var()
            top_features = variations.nlargest(top_k).index.tolist()
        
        return [f for f in top_features if f != target]
