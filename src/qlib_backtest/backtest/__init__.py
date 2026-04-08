"""
回测引擎模块：执行回测并计算性能指标
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """订单类型"""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    """订单数据类"""
    date: str
    stock_code: str
    order_type: OrderType
    price: float
    quantity: int
    commission: float = 0.0
    slippage: float = 0.0
    
    @property
    def cost(self) -> float:
        """订单成本"""
        return self.quantity * self.price * (1 + self.commission + abs(self.slippage))
    
    @property
    def cash_delta(self) -> float:
        """现金变化"""
        if self.order_type == OrderType.BUY:
            return -self.cost
        else:
            return self.quantity * self.price * (1 - self.commission)


@dataclass
class BacktestResult:
    """回测结果数据类"""
    total_return: float = 0.0
    annual_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    
    # 详细数据
    equity_curve: pd.DataFrame = field(default_factory=pd.DataFrame)
    orders: List[Order] = field(default_factory=list)
    trades: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'total_return': f"{self.total_return:.2%}",
            'annual_return': f"{self.annual_return:.2%}",
            'sharpe_ratio': f"{self.sharpe_ratio:.2f}",
            'max_drawdown': f"{self.max_drawdown:.2%}",
            'win_rate': f"{self.win_rate:.2%}",
            'profit_factor': f"{self.profit_factor:.2f}",
        }


class BacktestEngine:
    """
    回测引擎：执行策略回测
    """
    
    def __init__(
        self,
        initial_capital: float = 1000000.0,
        commission: float = 0.001,
        slippage: float = 0.0001,
        max_position_per_stock: float = 0.3,
    ):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资本
            commission: 佣金比例
            slippage: 滑点比例
            max_position_per_stock: 单个股票最大持仓比例
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.max_position_per_stock = max_position_per_stock
        
        self.portfolio = {}  # 持仓记录
        self.orders = []     # 订单记录
        self.trades = []     # 交易记录
        self.equity_curve = []  # 资金曲线
        
    def run_backtest(
        self,
        df: pd.DataFrame,
        signals: List,
    ) -> BacktestResult:
        """
        执行回测
        
        Args:
            df: 包含价格数据的DataFrame
            signals: 交易信号列表
            
        Returns:
            回测结果
        """
        logger.info("开始执行回测...")
        
        # 重置状态
        self.portfolio = {}
        self.orders = []
        self.trades = []
        self.equity_curve = []
        
        # 初始化
        current_cash = self.initial_capital
        current_date = None
        daily_values = []
        
        # 按日期和股票代码索引信号
        signal_dict = {}
        for signal in signals:
            key = (signal.date, signal.stock_code)
            signal_dict[key] = signal
        
        # 遍历数据
        dates = sorted(df['date'].unique()) if 'date' in df.columns else df.index.unique()
        
        for date in dates:
            current_date = date
            date_data = df[df['date'] == date] if 'date' in df.columns else df.loc[[date]]
            
            # 处理该日期的所有信号
            for _, row in date_data.iterrows():
                stock_code = row['stock_code']
                key = (date, stock_code)
                
                if key in signal_dict:
                    signal = signal_dict[key]
                    
                    if signal.signal_type == 'BUY':
                        current_cash = self._execute_buy_order(
                            stock_code=stock_code,
                            price=row['close'],
                            date=date,
                            current_cash=current_cash,
                        )
                    elif signal.signal_type == 'SELL':
                        current_cash = self._execute_sell_order(
                            stock_code=stock_code,
                            price=row['close'],
                            date=date,
                        )
            
            # 计算该日期的总资产
            position_value = self._calculate_position_value(date_data)
            total_value = current_cash + position_value
            
            daily_values.append({
                'date': date,
                'cash': current_cash,
                'position_value': position_value,
                'total_value': total_value,
            })
        
        # 生成结果
        self.equity_curve = pd.DataFrame(daily_values)
        result = self._calculate_metrics()
        result.orders = self.orders
        result.trades = self.trades
        result.equity_curve = self.equity_curve
        
        logger.info(f"回测完成。总收益率: {result.total_return:.2%}")
        return result
    
    def _execute_buy_order(
        self,
        stock_code: str,
        price: float,
        date: str,
        current_cash: float,
    ) -> float:
        """执行买入订单"""
        # 计算可买入数量
        max_amount = current_cash * self.max_position_per_stock
        quantity = int(max_amount / price)
        
        if quantity <= 0:
            return current_cash
        
        order = Order(
            date=date,
            stock_code=stock_code,
            order_type=OrderType.BUY,
            price=price,
            quantity=quantity,
            commission=self.commission,
            slippage=self.slippage,
        )
        
        self.orders.append(order)
        current_cash += order.cash_delta
        
        # 更新持仓
        if stock_code not in self.portfolio:
            self.portfolio[stock_code] = {'quantity': 0, 'cost': 0}
        
        self.portfolio[stock_code]['quantity'] += quantity
        self.portfolio[stock_code]['cost'] += order.cost
        
        logger.debug(f"买入 {stock_code} {quantity}股 @ {price}")
        
        return current_cash
    
    def _execute_sell_order(
        self,
        stock_code: str,
        price: float,
        date: str,
    ) -> float:
        """执行卖出订单"""
        if stock_code not in self.portfolio or self.portfolio[stock_code]['quantity'] <= 0:
            return 0
        
        quantity = self.portfolio[stock_code]['quantity']
        
        order = Order(
            date=date,
            stock_code=stock_code,
            order_type=OrderType.SELL,
            price=price,
            quantity=quantity,
            commission=self.commission,
            slippage=self.slippage,
        )
        
        self.orders.append(order)
        cash_delta = order.cash_delta
        
        # 计算盈亏
        cost = self.portfolio[stock_code]['cost']
        revenue = quantity * price * (1 - self.commission)
        pnl = revenue - cost
        
        self.trades.append({
            'stock_code': stock_code,
            'quantity': quantity,
            'buy_price': cost / quantity,
            'sell_price': price,
            'pnl': pnl,
            'date': date,
        })
        
        # 清空持仓
        self.portfolio[stock_code] = {'quantity': 0, 'cost': 0}
        
        logger.debug(f"卖出 {stock_code} {quantity}股 @ {price}")
        
        return cash_delta
    
    def _calculate_position_value(self, date_data: pd.DataFrame) -> float:
        """计算持仓总价值"""
        value = 0
        for stock_code, position in self.portfolio.items():
            if position['quantity'] > 0:
                # 获取该股票的最新价格
                stock_data = date_data[date_data['stock_code'] == stock_code]
                if not stock_data.empty:
                    price = stock_data['close'].iloc[-1]
                    value += position['quantity'] * price
        return value
    
    def _calculate_metrics(self) -> BacktestResult:
        """计算性能指标"""
        result = BacktestResult()
        
        if self.equity_curve.empty:
            return result
        
        # 总收益率
        initial_value = self.initial_capital
        final_value = self.equity_curve['total_value'].iloc[-1]
        result.total_return = (final_value - initial_value) / initial_value
        
        # 年化收益率 (假设252个交易日)
        days = (len(self.equity_curve) - 1) / 252 if len(self.equity_curve) > 1 else 1
        if days > 0:
            result.annual_return = (final_value / initial_value) ** (1 / days) - 1
        
        # 最大回撤
        equity_values = self.equity_curve['total_value'].values
        running_max = np.maximum.accumulate(equity_values)
        drawdown = (equity_values - running_max) / running_max
        result.max_drawdown = drawdown.min()
        
        # Sharpe比 (假设无风险利率为0)
        returns = self.equity_curve['total_value'].pct_change().dropna()
        if len(returns) > 0 and returns.std() > 0:
            result.sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
        
        # 胜率和盈利因子
        if self.trades:
            winning_trades = sum(1 for t in self.trades if t['pnl'] > 0)
            result.win_rate = winning_trades / len(self.trades)
            
            total_profit = sum(t['pnl'] for t in self.trades if t['pnl'] > 0)
            total_loss = abs(sum(t['pnl'] for t in self.trades if t['pnl'] < 0))
            
            result.profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        return result
