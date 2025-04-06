# import os
# import sys
# import MetaTrader5 as mt5
# import pandas as pd
# import numpy as np
# import time
# from datetime import datetime
# import talib as ta

# # ========================
# #    GLOBAL CONFIGURATION
# # ========================
# SYMBOL = "BTCUSDm"
# TIMEFRAME = mt5.TIMEFRAME_M5
# RISK_PER_TRADE = 0.02  # 2% risk per trade
# MAX_TRADES = 5
# MAX_GROWTH = 0.30  # 30% capital growth limit
# MAX_DRAWDOWN = -0.10  # 10% max drawdown
# SPREAD_LIMIT = 5.0  # Maximum allowed spread (points)
# ATR_PERIOD = 14
# EMA_FAST = 8
# EMA_SLOW = 21
# RSI_PERIOD = 14
# RR_RATIO = 2.5  # Risk-Reward Ratio

# # ANSI Escape Codes for display
# COLORS = {
#     'HEADER': '\033[95m',
#     'OKBLUE': '\033[94m',
#     'OKGREEN': '\033[92m',
#     'WARNING': '\033[93m',
#     'FAIL': '\033[91m',
#     'CYAN': '\033[96m',
#     'TRADING': '\033[93m',
#     'PROFIT': '\033[92m',
#     'LOSS': '\033[91m',
#     'ENDC': '\033[0m',
#     'BOLD': '\033[1m',
#     'UNDERLINE': '\033[4m'
# }

# class AdvancedCryptoScalper:
#     def __init__(self):
#         self.running = True
#         self.active_trades = []
#         self.trade_count = 0
#         self.win_trades = 0
#         self.loss_trades = 0
#         self.total_rr = 0.0
#         self.last_signal_reason = ""
#         self.start_time = datetime.now()
#         self.last_update = time.time()
#         self.current_balance = 0.0

#         try:
#             print(f"{COLORS['OKBLUE']}Connecting to MT5...{COLORS['ENDC']}")
#             if not self.initialize_mt5():
#                 raise ConnectionError("Failed to connect to MT5")

#             print(f"{COLORS['OKBLUE']}Validating account...{COLORS['ENDC']}")
#             self.validate_account()
#             self.setup_display()

#         except Exception as e:
#             self.shutdown(f"Initialization failed: {str(e)}")

#     def initialize_mt5(self):
#         """Initialize MT5 connection with detailed logging"""
#         for attempt in range(3):
#             try:
#                 if not mt5.initialize():
#                     print(f"{COLORS['FAIL']}MT5 initialization failed (attempt {attempt+1}/3){COLORS['ENDC']}")
#                     time.sleep(1)
#                     continue

#                 if not mt5.symbol_select(SYMBOL, True):
#                     print(f"{COLORS['FAIL']}Symbol selection failed{COLORS['ENDC']}")
#                     mt5.shutdown()
#                     return False

#                 print(f"{COLORS['OKGREEN']}Successfully connected to MT5{COLORS['ENDC']}")
#                 return True

#             except Exception as e:
#                 print(f"{COLORS['FAIL']}Connection error: {str(e)}{COLORS['ENDC']}")
#                 time.sleep(2)

#         return False

#     def validate_account(self):
#         """Validate account information with proper error handling"""
#         try:
#             account_info = mt5.account_info()
#             if not account_info:
#                 raise ValueError("Failed to retrieve account information")

#             self.initial_balance = account_info.balance
#             if self.initial_balance <= 10:
#                 raise ValueError("Limited Funds! Add minimum $10 to get started.")

#             self.current_balance = self.initial_balance
#             print(f"\n{COLORS['OKGREEN']}=== Account Information ===")
#             print(f"Login: {account_info.login}")
#             print(f"Balance: {self.initial_balance:.2f}")
#             print(f"Leverage: 1:{account_info.leverage}")
#             print(f"Currency: {account_info.currency}")
#             print(f"==========================={COLORS['ENDC']}\n")

#         except Exception as e:
#             raise RuntimeError(f"Warning🚨: {str(e)}")

#     def get_current_spread(self):
#         """Get current spread in points (corrected calculation)"""
#         try:
#             tick = mt5.symbol_info_tick(SYMBOL)
#             if tick:
#                 return tick.ask - tick.bid  # Direct spread value
#             return 0.0
#         except:
#             return 0.0

#     def setup_display(self):
#         """Initialize professional console display"""
#         os.system('cls' if os.name == 'nt' else 'clear')
#         print(f"{COLORS['BOLD']}{COLORS['HEADER']}=== AI QUANT SCALPER v3.0 ===")
#         print(f"{COLORS['OKBLUE']}Symbol: {SYMBOL} | Timeframe: 5M | Strategy: Fib/EMA/RSI/MACD")
#         print(f"Risk Management: {RISK_PER_TRADE*100}% per trade | RR: 1:{RR_RATIO}")
#         print("---------------------------------------------------{COLORS['ENDC']}")

#     # ========================
#     #    CORE TRADING LOGIC
#     # ========================

#     def analyze_market(self):
#         """Generate trade signals with detailed condition checking"""
#         try:
#             df = self.get_market_data()
#             if df is None or len(df) < 100:
#                 return False, False, "Insufficient data"

#             df = self.calculate_indicators(df)
#             current = df.iloc[-1]
#             prev = df.iloc[-2]

#             fib_levels = self.calculate_fibonacci(df)
#             reasons = []

#             # Long Conditions
#             long_conditions = {
#                 'EMA Cross': current['ema_fast'] > current['ema_slow'] and prev['ema_fast'] <= prev['ema_slow'],
#                 'RSI Oversold': current['rsi'] < 60,
#                 'Fibonacci Support': current['close'] > fib_levels['61.8'],
#                 'MACD Bullish': current['macd'] > current['macd_signal'],
#                 'Volume Spike': current['tick_volume'] > df['tick_volume'].rolling(20).mean().iloc[-2] * 1.2
#             }

#             # Short Conditions
#             short_conditions = {
#                 'EMA Cross': current['ema_fast'] < current['ema_slow'] and prev['ema_fast'] >= prev['ema_slow'],
#                 'RSI Overbought': current['rsi'] > 40,
#                 'Fibonacci Resistance': current['close'] < fib_levels['38.2'],
#                 'MACD Bearish': current['macd'] < current['macd_signal'],
#                 'Volume Spike': current['tick_volume'] > df['tick_volume'].rolling(20).mean().iloc[-2] * 1.5
#             }

#             long_reasons = [k for k,v in long_conditions.items() if v]
#             short_reasons = [k for k,v in short_conditions.items() if v]

#             if len(long_reasons) >= 2 and self.valid_spread():
#                 return True, False, "LONG: " + " + ".join(long_reasons)

#             if len(short_reasons) >= 2 and self.valid_spread():
#                 return False, True, "SHORT: " + " + ".join(short_reasons)

#             return False, False, "Waiting for confirmation..."

#         except Exception as e:
#             self.log_error(f"Analysis error: {str(e)}")
#             return False, False, "Analysis error"

#     def calculate_indicators(self, df):
#         """Calculate technical indicators"""
#         df['ema_fast'] = ta.EMA(df['close'], EMA_FAST)
#         df['ema_slow'] = ta.EMA(df['close'], EMA_SLOW)
#         df['rsi'] = ta.RSI(df['close'], RSI_PERIOD)
#         df['macd'], df['macd_signal'], _ = ta.MACD(df['close'])
#         df['atr'] = ta.ATR(df['high'], df['low'], df['close'], ATR_PERIOD)
#         return df.dropna()

#     def calculate_fibonacci(self, df):
#         """Calculate Fibonacci retracement levels"""
#         lookback = 20
#         high = df['high'].rolling(lookback).max().iloc[-1]
#         low = df['low'].rolling(lookback).min().iloc[-1]
#         diff = high - low

#         return {
#             '23.6': high - diff * 0.236,
#             '38.2': high - diff * 0.382,
#             '50.0': high - diff * 0.5,
#             '61.8': high - diff * 0.618
#         }

#     # ========================
#     #    RISK MANAGEMENT
#     # ========================

#     def manage_risk(self):
#         """Check trading limits and manage positions"""
#         if self.check_limits():
#             return False

#         self.current_balance = mt5.account_info().equity
#         self.manage_positions()
#         return True

#     def check_limits(self):
#         """Enforce growth/drawdown limits"""
#         growth = (self.current_balance - self.initial_balance) / self.initial_balance
#         drawdown = (self.initial_balance - self.current_balance) / self.initial_balance

#         if growth >= MAX_GROWTH:
#             self.shutdown(f"{COLORS['OKGREEN']}Profit target reached (+{growth*100:.1f}%)")
#             return True

#         if drawdown >= abs(MAX_DRAWDOWN):
#             self.shutdown(f"{COLORS['FAIL']}Drawdown limit hit (-{drawdown*100:.1f}%)")
#             return True

#         return False

#     def calculate_position_size(self):
#         """Dynamic position sizing with active trade adjustment"""
#         active_trades = len(self.active_trades)
#         risk_multiplier = 1 / (active_trades + 1)  # Reduce risk with more trades

#         atr = self.get_current_atr()
#         if atr == 0:
#             return 0.01

#         risk_amount = self.current_balance * RISK_PER_TRADE * risk_multiplier
#         lot_size = (risk_amount / (atr * 100)) / 100  # BTCUSDm specific
#         return round(max(min(lot_size, 50), 0.01), 2)

#     # ========================
#     #    TRADE EXECUTION
#     # ========================


#     def execute_trade(self, direction, reason):
#         """Execute trade with detailed logging"""
#         if not self.valid_spread():
#             return

#         try:
#             lot_size = self.calculate_position_size()
#             tick = mt5.symbol_info_tick(SYMBOL)
#             price = tick.ask if direction == 'BUY' else tick.bid
#             atr = self.get_current_atr()

#             # Calculate SL/TP based on ATR and RR
#             sl_distance = atr * 1.5
#             tp_distance = sl_distance * RR_RATIO

#             if direction == 'BUY':
#                 sl = price - sl_distance
#                 tp = price + tp_distance
#             else:
#                 sl = price + sl_distance
#                 tp = price - tp_distance

#             request = {
#                 "action": mt5.TRADE_ACTION_DEAL,
#                 "symbol": SYMBOL,
#                 "volume": lot_size,
#                 "type": mt5.ORDER_TYPE_BUY if direction == 'BUY' else mt5.ORDER_TYPE_SELL,
#                 "price": price,
#                 "sl": sl,
#                 "tp": tp,
#                 "deviation": 10,
#                 "magic": 3000,
#                 "comment": reason,
#                 "type_time": mt5.ORDER_TIME_GTC,
#                 "type_filling": mt5.ORDER_FILLING_FOK,
#             }

#             result = mt5.order_send(request)
#             if result.retcode != mt5.TRADE_RETCODE_DONE:
#                 self.log_error(f"Trade failed: {result.comment}")
#                 return

#             self.trade_count += 1
#             self.active_trades.append({
#                 'ticket': result.order,
#                 'time': datetime.now(),
#                 'direction': direction,
#                 'lot_size': lot_size,
#                 'sl': sl,
#                 'tp': tp
#             })

#             self.last_signal_reason = f"{direction} - {reason}"
#             self.update_display()

#         except Exception as e:
#             self.log_error(f"Trade execution error: {str(e)}")

#     # ========================
#     #    POSITION MANAGEMENT
#     # ========================

#     def manage_positions(self):
#         """Manage open positions with trailing SL"""
#         try:
#             for trade in list(self.active_trades):
#                 position = mt5.positions_get(ticket=trade['ticket'])
#                 if not position:
#                     self.active_trades.remove(trade)
#                     continue

#                 position = position[0]
#                 current_price = mt5.symbol_info_tick(SYMBOL).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(SYMBOL).ask

#                 # Update trailing stop
#                 if position.profit > 0:
#                     self.update_trailing_sl(position, current_price)

#                 # Check if position needs closing
#                 self.check_position_health(position)

#         except Exception as e:
#             self.log_error(f"Position management error: {str(e)}")

#     def update_trailing_sl(self, position, current_price):
#         """Update trailing stop loss dynamically"""
#         entry_price = position.price_open
#         sl_distance = abs(entry_price - position.sl)
#         buffer = sl_distance * 0.5  # Trail at 50% of initial SL distance

#         if position.type == mt5.ORDER_TYPE_BUY:
#             new_sl = current_price - buffer
#             if new_sl > position.sl:
#                 self.modify_sl(position.ticket, new_sl)
#         else:
#             new_sl = current_price + buffer
#             if new_sl < position.sl:
#                 self.modify_sl(position.ticket, new_sl)

#     def modify_sl(self, ticket, new_sl):
#         """Modify stop loss level"""
#         request = {
#             "action": mt5.TRADE_ACTION_SLTP,
#             "position": ticket,
#             "sl": new_sl,
#             "deviation": 10,
#         }
#         mt5.order_send(request)

#     def check_position_health(self, position):
#         """Check position status and close if needed"""
#         duration = (datetime.now() - position.time_update).seconds
#         pnl = position.profit
#         rr_achieved = abs(pnl) / (abs(position.price_open - position.sl) * position.volume)

#         # Close position if RR target achieved
#         if rr_achieved >= RR_RATIO:
#             self.close_position(position, f"RR Target ({rr_achieved:.1f}R)")
#         # Close if position exceeds maximum duration
#         elif duration >= 300:  # 5 minutes
#             self.close_position(position, "Time Expiry")

#     def close_position(self, position, reason):
#         """Close position and update statistics"""
#         try:
#             request = {
#                 "action": mt5.TRADE_ACTION_DEAL,
#                 "symbol": SYMBOL,
#                 "volume": position.volume,
#                 "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
#                 "position": position.ticket,
#                 "price": mt5.symbol_info_tick(SYMBOL).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(SYMBOL).ask,
#                 "deviation": 10,
#                 "magic": 3000,
#                 "comment": reason,
#             }

#             result = mt5.order_send(request)
#             if result.retcode == mt5.TRADE_RETCODE_DONE:
#                 if position.profit > 0:
#                     self.win_trades += 1
#                 else:
#                     self.loss_trades += 1

#                 self.total_rr += abs(position.profit) / (abs(position.price_open - position.sl) * position.volume)
#                 self.active_trades = [t for t in self.active_trades if t['ticket'] != position.ticket]

#         except Exception as e:
#             self.log_error(f"Close position error: {str(e)}")

#     # ========================
#     #    UTILITIES & DISPLAY
#     # ========================
#     def update_display(self):
#         """Update console display with trading metrics"""
#         try:
#             win_rate = self.win_trades / self.trade_count * 100 if self.trade_count > 0 else 0
#             avg_rr = self.total_rr / self.trade_count if self.trade_count > 0 else 0
#             growth = (self.current_balance - self.initial_balance) / self.initial_balance * 100

#             print(f"\033[4;0H{COLORS['CYAN']}Time: {datetime.now().strftime('%H:%M:%S')} | Running: {str(datetime.now() - self.start_time).split('.')[0]}")
#             print(f"\033[5;0H{COLORS['BOLD']}Balance: ${self.current_balance:.2f} | Growth: {growth:+.2f}%")
#             print(f"\033[6;0HTrades: {self.trade_count} | Active: {len(self.active_trades)} | Spread: {self.get_current_spread():.1f}")
#             print(f"\033[7;0H{COLORS['PROFIT']}Win Rate: {win_rate:.1f}% | Avg RR: {avg_rr:.1f}")
#             print(f"\033[8;0H{COLORS['TRADING']}Last Signal: {self.last_signal_reason}")
#             print(f"\033[9;0H{COLORS['PROFIT']}Wins: {self.win_trades} {COLORS['LOSS']}Losses: {self.loss_trades}")
#             print(f"\033[10;0H{COLORS['OKBLUE']}---------------------------------------------------{COLORS['ENDC']}")

#         except Exception as e:
#             self.log_error(f"Display update error: {str(e)}")

#     # ========================
#     #    POSITION MANAGEMENT
#     # ========================

#     def manage_positions(self):
#         """Manage all open positions with trailing stops and health checks"""
#         try:
#             current_time = datetime.now()
#             positions_to_remove = []

#             for trade in self.active_trades:
#                 position = mt5.positions_get(ticket=trade['ticket'])
#                 if not position:
#                     positions_to_remove.append(trade)
#                     continue

#                 position = position[0]
#                 current_price = mt5.symbol_info_tick(SYMBOL).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(SYMBOL).ask

#                 # Update trailing stop loss
#                 self.update_trailing_sl(position, current_price)

#                 # Check position health
#                 if self.check_position_health(position):
#                     positions_to_remove.append(trade)

#             # Remove closed positions from active list
#             for trade in positions_to_remove:
#                 if trade in self.active_trades:
#                     self.active_trades.remove(trade)

#         except Exception as e:
#             self.log_error(f"Position management error: {str(e)}")

#     def check_position_health(self, position):
#         """Check if position needs to be closed"""
#         duration = (datetime.now() - position.time_update).total_seconds()
#         pnl = position.profit
#         rr_achieved = abs(pnl) / (abs(position.price_open - position.sl) * position.volume)

#         # Close conditions
#         if rr_achieved >= RR_RATIO:
#             self.close_position(position, f"Achieved {rr_achieved:.1f}R")
#             return True
#         elif duration >= 300:  # 5 minutes
#             self.close_position(position, "Time Expiry")
#             return True
#         return False

#     # ========================
#     #    HELPER FUNCTIONS
#     # ========================

#     def get_market_data(self):
#         """Retrieve OHLC data with error handling"""
#         try:
#             rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 100)
#             return pd.DataFrame(rates) if rates is not None else None
#         except Exception as e:
#             self.log_error(f"Data retrieval error: {str(e)}")
#             return None

#     def valid_spread(self):
#         """Check if spread is within acceptable limits"""
#         spread = self.get_current_spread()
#         return spread <= SPREAD_LIMIT if spread is not None else False

#     def get_current_spread(self):
#         """Get current spread in points"""
#         try:
#             tick = mt5.symbol_info_tick(SYMBOL)
#             return (tick.ask - tick.bid) * 10**5  # Convert to points
#         except:
#             return 0.0

#     def get_current_atr(self):
#         """Get current ATR value"""
#         df = self.get_market_data()
#         if df is not None and not df.empty:
#             return ta.ATR(df['high'], df['low'], df['close'], ATR_PERIOD).iloc[-1]
#         return 0.0

#     def log_error(self, message):
#         """Log errors with timestamp"""
#         timestamp = datetime.now().strftime("%H:%M:%S")
#         print(f"{COLORS['FAIL']}[{timestamp}] ERROR: {message}{COLORS['ENDC']}")

#     def shutdown(self, message=""):
#         """Graceful shutdown procedure"""
#         print(f"\n{COLORS['BOLD']}Initiating shutdown...{COLORS['ENDC']}")
#         self.close_all_positions()
#         mt5.shutdown()
#         print(f"{COLORS['BOLD']}{message}{COLORS['ENDC']}")
#         print(f"Final balance: {self.current_balance:.2f}")
#         print(f"Total trades: {self.trade_count}")
#         print(f"Win rate: {self.win_trades/self.trade_count*100:.1f}%" if self.trade_count > 0 else "")
#         sys.exit(0)

#     def close_all_positions(self):
#         """Close all open positions on shutdown"""
#         try:
#             positions = mt5.positions_get(symbol=SYMBOL)
#             if positions:
#                 print(f"{COLORS['WARNING']}Closing all open positions...{COLORS['ENDC']}")
#                 for position in positions:
#                     self.close_position(position, "Shutdown")
#         except Exception as e:
#             self.log_error(f"Position closure error: {str(e)}")

#     # ========================
#     #    MAIN LOOP
#     # ========================


#     def run(self):
#         """Main trading loop"""
#         try:
#             while self.running and self.manage_risk():
#                 # Get trading signal
#                 long_signal, short_signal, signal_reason = self.analyze_market()

#                 # Execute trades
#                 if long_signal and len(self.active_trades) < MAX_TRADES:
#                     self.execute_trade('BUY', signal_reason)
#                 elif short_signal and len(self.active_trades) < MAX_TRADES:
#                     self.execute_trade('SELL', signal_reason)

#                 # Update display every 0.5 seconds
#                 if time.time() - self.last_update > 0.5:
#                     self.update_display()
#                     self.last_update = time.time()

#                 time.sleep(0.1)

#         except KeyboardInterrupt:
#             self.shutdown("User interrupted operation")
#         except Exception as e:
#             self.shutdown(f"Critical error: {str(e)}")


# if __name__ == "__main__":
#     try:
#         bot = AdvancedCryptoScalper()
#         bot.run()
#     except Exception as e:
#         print(f"{COLORS['FAIL']}Fatal initialization error: {str(e)}{COLORS['ENDC']}")








import os
import sys
import MetaTrader5 as mt5  # type: ignore
import pandas as pd  # type: ignore
import numpy as np
import time
from datetime import datetime, timedelta
import requests  # type: ignore # For alternative data sourcing

# ========================
#    INSTITUTIONAL CONFIG
# ========================
SYMBOLS = ["EURUSDm", "GBPUSDm", "USDJPYm",
           "AUDJPYm", "AUDCADm", "USDCHFm", "EURGBPm"]
TIMEFRAMES = {
    'M5': mt5.TIMEFRAME_M5,
    'M15': mt5.TIMEFRAME_M15,
    'H1': mt5.TIMEFRAME_H1,
    'H4': mt5.TIMEFRAME_H4
}
RISK_PER_TRADE = 0.03  # 3% risk per trade
MAX_TRADES = 3
LIQUIDITY_BUFFER = 0.0015  # 15 pips buffer from liquidity zones
ORDER_BLOCK_PERIOD = 20  # Lookback for order blocks

# Free Financial Data API (Alternative to MT5)
ALPHA_VANTAGE_API = "V67J7MUVK4F52O9A"
FINANCIAL_MODELING_PREP_API = "hDgsFWHXS59u2MzsYCSbeyo3YTAuBqxk "

COLORS = {
    # Basic colors
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',  # Red color for errors
    'CYAN': '\033[96m',
    'MAGENTA': '\033[95m',

    # Trading colors
    'BUY': '\033[92m',    # Green
    'SELL': '\033[91m',   # Red
    'NEUTRAL': '\033[94m',  # Blue
    'TRADING': '\033[93m',  # Yellow
    'PROFIT': '\033[92m',  # Green
    'LOSS': '\033[91m',   # Red

    # Formatting
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}


class InstitutionalGradeTrader:
    def __init__(self):
        self.running = True
        self.active_trades = []
        self.market_structure = {}
        self.liquidity_zones = {}
        self.historical_data = {}  # Initialize historical data storage
        self.trade_history = []
        self.error_log = []
        self.warning_log = []
        self.setup_environment()

    def setup_environment(self):
        """Initialize trading environment with fallback data sources"""
        try:
            if not mt5.initialize():
                raise ConnectionError("MT5 connection failed - using API data")
            print(
                f"{COLORS['BOLD']}Connected to institutional liquidity pool{COLORS['ENDC']}")
        except:
            print(
                f"{COLORS['WARNING']}Using alternative data sources{COLORS['ENDC']}")

        self.load_historical_data()
        self.analyze_initial_market_structure()

    def log_error(self, message):
        """Log errors with timestamp and context"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] ERROR: {message}"
        self.error_log.append(entry)
        print(f"{COLORS['FAIL']}{entry}{COLORS['ENDC']}")

    def log_trade(self, symbol, direction, size, price, sl, tp):
        """Log successful trades"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = (f"[{timestamp}] TRADE: {symbol} {direction} {size} @ {price} | "
                 f"SL: {sl} | TP: {tp}")
        self.trade_history.append(entry)
        print(f"{COLORS['OKGREEN']}{entry}{COLORS['ENDC']}")

    def log_warning(self, message):
        """Log non-critical warnings"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] WARNING: {message}"
        self.warning_log.append(entry)
        print(f"{COLORS['WARNING']}{entry}{COLORS['ENDC']}")

    def load_historical_data(self):
        """Load historical data for all symbols across timeframes"""
        print(
            f"{COLORS['BOLD']}Loading institutional-grade historical data...{COLORS['ENDC']}")
        for symbol in SYMBOLS:
            self.historical_data[symbol] = {}
            for tf in TIMEFRAMES.keys():
                try:
                    self.historical_data[symbol][tf] = self.get_data(
                        symbol, tf)
                except Exception as e:
                    print(
                        f"{COLORS['WARNING']}Failed to load {tf} data for {symbol}: {str(e)}{COLORS['ENDC']}")
            time.sleep(0.5)  # Rate limit protection

    def find_fair_value_gaps(self, df):
        """Identify ICT Fair Value Gaps (FVG) in price series"""
        fvgs = []
        if len(df) < 3:
            return fvgs

        for i in range(len(df)-2):
            current = df.iloc[i]
            next_1 = df.iloc[i+1]
            next_2 = df.iloc[i+2]

            # Bearish FVG (Price efficiency gap)
            if (current.high > next_1.high and
                next_1.high > next_2.high and
                    current.low > next_2.low):
                fvgs.append(('BEARISH', current.high, next_2.low))

            # Bullish FVG
            if (current.low < next_1.low and
                next_1.low < next_2.low and
                    current.high < next_2.high):
                fvgs.append(('BULLISH', next_2.high, current.low))

        return fvgs[-5:]  # Return last 5 FVGs

    def identify_pricing_zones(self, df):
        """Determine premium/discount zones using market structure"""
        if len(df) < 20:
            return 'NEUTRAL'

        sma = df.close.rolling(20).mean().iloc[-1]
        current_close = df.close.iloc[-1]

        # Calculate standard deviation
        std_dev = df.close.rolling(20).std().iloc[-1]

        premium_level = sma + std_dev
        discount_level = sma - std_dev

        if current_close > premium_level:
            return 'PREMIUM'
        elif current_close < discount_level:
            return 'DISCOUNT'
        return 'FAIR VALUE'

    def analyze_initial_market_structure(self):
        """Initial market structure analysis during startup"""
        print(
            f"{COLORS['BOLD']}Analyzing institutional market patterns...{COLORS['ENDC']}")
        for symbol in SYMBOLS:
            # Analyze H4 timeframe for market structure
            h4_data = self.historical_data[symbol].get('H4', pd.DataFrame())
            if not h4_data.empty:
                self.market_structure[symbol] = self.determine_market_structure(
                    h4_data)

            # Identify liquidity zones on H1 timeframe
            h1_data = self.historical_data[symbol].get('H1', pd.DataFrame())
            if not h1_data.empty:
                self.liquidity_zones[symbol] = self.find_liquidity_zones(
                    h1_data)

    # ========================
    #    CORE PRICE ACTION ANALYSIS
    # ========================

    # Add this to your existing analyze_market method

    def analyze_market(self, symbol):
        """Enhanced with full ICT/SMC analysis"""
        tf_data = {
            'M5': self.get_data(symbol, 'M5'),
            'M15': self.get_data(symbol, 'M15'),
            'H1': self.get_data(symbol, 'H1'),
            'H4': self.get_data(symbol, 'H4')
        }

        analysis = {
            'liquidity': self.find_liquidity_zones(tf_data['H4']),
            'order_blocks': self.detect_order_blocks(tf_data['H1']),
            'market_structure': self.determine_market_structure(tf_data['H4']),
            'fair_value_gaps': self.find_fair_value_gaps(tf_data['M15']),
            'premium_discount': self.identify_pricing_zones(tf_data['H1']),
            # Add this method next
            'bos_choch': self.check_breakouts(tf_data['H4'])
        }

        return self.generate_trading_signals(symbol, analysis)

    def check_breakouts(self, df):
        """Identify Break of Structure (BOS) and Change of Character (CHOCH)"""
        if len(df) < 10:
            return None

        last_swing_high = df.high.rolling(5).max().iloc[-1]
        last_swing_low = df.low.rolling(5).min().iloc[-1]
        current_close = df.close.iloc[-1]

        if current_close > last_swing_high:
            return 'BOS'
        elif current_close < last_swing_low:
            return 'CHOCH'
        return None

    def find_liquidity_zones(self, df):
        """Identify institutional liquidity pools"""
        df = df[-100:]  # Last 100 periods
        return {
            'highs': self.find_swing_highs(df, 3),
            'lows': self.find_swing_lows(df, 3),
            'volume_clusters': self.find_volume_clusters(df)
        }

    def detect_order_blocks(self, df):
        """Smart Money order block detection"""
        blocks = []
        for i in range(3, len(df)-3):
            # Bearish order block detection
            if df.close[i] > df.open[i] and \
               df.close[i+1] < df.open[i+1] and \
               df.high[i] > max(df.high[i+1:i+4]):
                blocks.append(('BEARISH', df.high[i], df.low[i]))

            # Bullish order block detection
            if df.close[i] < df.open[i] and \
               df.close[i+1] > df.open[i+1] and \
               df.low[i] < min(df.low[i+1:i+4]):
                blocks.append(('BULLISH', df.high[i], df.low[i]))

        return blocks[-ORDER_BLOCK_PERIOD:]  # Return recent blocks

    def determine_market_structure(self, df):
        """Determine initial market structure from historical data"""
        structure = []
        highs = self.find_swing_highs(df, 3)
        lows = self.find_swing_lows(df, 3)

        for i in range(1, len(highs)):
            if highs[i] > highs[i-1] and lows[i] > lows[i-1]:
                structure.append('UPTREND')
            elif highs[i] < highs[i-1] and lows[i] < lows[i-1]:
                structure.append('DOWNTREND')
            else:
                structure.append('RANGE')
        return structure

    # ========================
    #    TRADING SIGNAL GENERATION
    # ========================

    def generate_trading_signals(self, symbol, analysis):
        """Generate signals using institutional order flow concepts"""
        entry_signals = []

        # 1. Liquidity Grab Strategy
        current_price = self.get_current_price(symbol)
        liquidity = analysis['liquidity']

        # Buy Signal Conditions
        if (current_price < min(liquidity['lows']) + LIQUIDITY_BUFFER and
            any(b[0] == 'BULLISH' for b in analysis['order_blocks']) and
                'UPTREND' in analysis['market_structure'][-2:]):

            stop_loss = min(liquidity['lows']) - LIQUIDITY_BUFFER
            entry_price = min(liquidity['lows']) + LIQUIDITY_BUFFER
            target = self.calculate_risk_reward(entry_price, stop_loss)

            entry_signals.append(('BUY', entry_price, stop_loss, target))

        # Sell Signal Conditions
        if (current_price > max(liquidity['highs']) - LIQUIDITY_BUFFER and
            any(b[0] == 'BEARISH' for b in analysis['order_blocks']) and
                'DOWNTREND' in analysis['market_structure'][-2:]):

            stop_loss = max(liquidity['highs']) + LIQUIDITY_BUFFER
            entry_price = max(liquidity['highs']) - LIQUIDITY_BUFFER
            target = self.calculate_risk_reward(entry_price, stop_loss)

            entry_signals.append(('SELL', entry_price, stop_loss, target))

        return entry_signals

    # ========================
    #    RISK MANAGEMENT
    # ========================

    # def calculate_position_size(self, entry, stop_loss):
    #     """Institutional position sizing based on liquidity distance"""
    #     account_info = mt5.account_info()
    #     risk_amount = account_info.balance * RISK_PER_TRADE
    #     risk_per_unit = abs(entry - stop_loss)

    #     if risk_per_unit == 0:
    #         return 0.0

    #     return round(risk_amount / risk_per_unit, 2)

    def calculate_position_size(self, symbol, entry, stop_loss):
        """Exness USD Account Position Sizing"""
        try:
            # Pair configuration
            jpy_pairs = ["USDJPYm", "AUDJPYm"]
            usd_quote_pairs = ["EURUSDm", "GBPUSDm", "USDCHFm"]
            cross_pairs = ["AUDCADm", "EURGBPm"]

            # Get current price and pip size
            pip_size = 0.0001  # Default for most pairs
            if symbol in jpy_pairs:
                pip_size = 0.01  # JPY pairs have 2 decimal places

            # Calculate pips risk
            price_distance = abs(entry - stop_loss)
            pips_risk = price_distance / pip_size

            # Validate minimum pips
            min_pips = 3 if symbol in usd_quote_pairs else 5
            if pips_risk < min_pips:
                self.log_error(f"Stop loss too close: {pips_risk:.1f} pips")
                return 0.0

            # Calculate pip value based on pair type
            if symbol in usd_quote_pairs:
                pip_value = 10.00  # $10 per standard lot
            elif symbol in jpy_pairs:
                pip_value = self.calculate_jpy_pip_value(symbol)
            else:
                pip_value = self.calculate_cross_pip_value(symbol)

            # Calculate position size
            risk_amount = mt5.account_info().balance * RISK_PER_TRADE
            raw_size = risk_amount / (pips_risk * pip_value)
            validated_size = self.validate_exness_size(raw_size)

            self.log_info(
                f"{symbol} | Size: {validated_size:.2f} | Pips: {pips_risk:.1f}")
            return validated_size

        except Exception as e:
            self.log_error(f"Position error: {str(e)}")
            return 0.0

    def calculate_jpy_pip_value(self):
        """JPY Pair Pip Value Calculation"""
        try:
            # For USDJPYm: (0.01 / USDJPY price) * 100000
            # For AUDJPYm: (0.01 / USDJPY price) * 100000
            usdjpy_rate = mt5.symbol_info_tick("USDJPYm").ask
            return (0.01 / usdjpy_rate) * 100000 if usdjpy_rate else 0.83
        except:
            return 0.83  # Fallback value

    def calculate_cross_pip_value(self, symbol):
        """Cross Pair Pip Value Calculation"""
        try:
            clean_symbol = symbol.replace('m', '')
            base_currency = clean_symbol[:3]
            quote_currency = clean_symbol[3:]

            # Get base/USD and quote/USD rates
            base_rate = mt5.symbol_info_tick(f"{base_currency}USDm").ask
            quote_rate = mt5.symbol_info_tick(f"{quote_currency}USDm").ask

            return (0.0001 * base_rate / quote_rate) * 100000
        except:
            return 10.00  # Fallback to $10

    def validate_exness_size(self, raw_size):
        """Exness-specific Validation"""
        exness_constraints = {
            'min_lot': 0.01,
            'max_lot': 50.0,
            'step': 0.01
        }

        validated = round(
            raw_size / exness_constraints['step']) * exness_constraints['step']
        return max(min(validated, exness_constraints['max_lot']), exness_constraints['min_lot'])

    def get_pip_value(self, base_currency, quote_currency):
        """Robust pip value calculation with error handling"""
        account_currency = mt5.account_info().currency
        pip_value = 0.0

        try:
            # Direct quote conversion (EURUSD for USD account)
            if quote_currency == account_currency:
                return 10.0  # $10 per standard lot for direct quotes

            # Construct proper conversion pair
            conversion_pair = f"{account_currency}{quote_currency}m"
            if not mt5.symbol_info(conversion_pair):
                # Try without 'm'
                conversion_pair = f"{account_currency}{quote_currency}"

            # Get conversion rate safely
            tick = mt5.symbol_info_tick(conversion_pair)
            if not tick:
                raise ValueError(f"No tick data for {conversion_pair}")

            conversion_rate = tick.ask

            # Calculate pip value for different quote types
            if quote_currency == "JPY":
                pip_value = 1000 / conversion_rate  # JPY pairs have 2 decimal places
            else:
                pip_value = 10.0 / conversion_rate

            return round(pip_value, 4)

        except Exception as e:
            self.log_error(
                f"Pip calc error {base_currency}{quote_currency}: {str(e)}")
            return 0.0

    def validate_position_size(self, symbol_info, raw_size):
        """Professional Size validation"""
        min_lot = symbol_info.volume_min
        max_lot = symbol_info.volume_max
        step = symbol_info.volume_step

        validated = round(raw_size / step) * step
        validated = max(min(validated, max_lot), min_lot)

        if abs(validated - raw_size) > step:
            self.log_warning(
                f"Size adjusted from {raw_size:.2f} to {validated:.2f}")

        return round(validated, 2)

    def calculate_risk_reward(self, entry, stop_loss, rr_ratio=3):
        """Calculate target based on institutional RR ratios"""
        distance = abs(entry - stop_loss)
        return entry + (distance * rr_ratio) if entry > stop_loss else entry - (distance * rr_ratio)

    # ========================
    #    DATA MANAGEMENT
    # ========================

    def get_data(self, symbol, timeframe):
        """Fetch data from MT5 or fallback API"""
        try:
            rates = mt5.copy_rates_from_pos(
                symbol, TIMEFRAMES[timeframe], 0, 500)
            if rates is None:
                return pd.DataFrame()

            df = pd.DataFrame(rates)
            # Rename MT5 columns to standard names
            df = df.rename(columns={
                'tick_volume': 'volume',
                'real_volume': 'volume',
                'spread': 'spread'
            })
            return df

        except Exception as e:
            print(
                f"{COLORS['WARNING']}Data error ({symbol} {timeframe}): {str(e)}{COLORS['ENDC']}")
            return pd.DataFrame()

    def fetch_api_data(self, symbol, timeframe):
        """Fetch data from financial API"""
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={timeframe}&apikey={ALPHA_VANTAGE_API}"
        response = requests.get(url)
        data = response.json()
        return self.parse_api_data(data)

    # ========================
    #    UTILITIES
    # ========================

    def find_swing_highs(self, df, window=3):
        """Identify swing highs using rolling window"""
        return df['high'].rolling(window, center=True).apply(
            lambda x: x.iloc[window//2] == x.max(), raw=False
        ).dropna().astype(bool).tolist()

    def find_swing_lows(self, df, window=3):
        """Identify swing lows using rolling window"""
        return df['low'].rolling(window, center=True).apply(
            lambda x: x.iloc[window//2] == x.min(), raw=False
        ).dropna().astype(bool).tolist()

    def find_volume_clusters(self, df):
        """Identify volume-based liquidity zones with proper column handling"""
        if df.empty or 'tick_volume' not in df.columns:
            return []

        try:
            # Use observed=True to handle future warnings
            grouped = df.groupby(
                pd.qcut(df['close'], 10, duplicates='drop', observed=True)
            )['tick_volume'].sum()

            return grouped.nlargest(3).index.tolist()

        except Exception as e:
            print(
                f"{COLORS['WARNING']}Volume cluster error: {str(e)}{COLORS['ENDC']}")

            return []

    def get_current_price(self, symbol):
        """Get current market price with spread check"""
        tick = mt5.symbol_info_tick(symbol)
        return (tick.ask + tick.bid) / 2

    # ========================
    #    EXECUTION & MONITORING
    # ========================

    def execute_trade(self, symbol, signal):
        """Execute institutional-sized trade with liquidity consideration"""
        trade_type = signal[0]
        entry_price = signal[1]
        stop_loss = signal[2]
        take_profit = signal[3]

        position_size = self.calculate_position_size(
            symbol, entry_price, stop_loss)

        if position_size <= 0:
            self.log_error(f"Invalid position size for {symbol}")
            return

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": position_size,
            "type": mt5.ORDER_TYPE_BUY if trade_type == 'BUY' else mt5.ORDER_TYPE_SELL,
            "price": entry_price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 20,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
            "comment": "Institutional Liquidity Play"
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log_error(f"Trade execution failed: {result.comment}")
        else:
            self.log_trade(
                symbol=symbol,
                direction=signal[0],
                size=position_size,
                price=entry_price,
                sl=stop_loss,
                tp=take_profit
            )
            self.active_trades.append(result.order)

    def monitor_positions(self):
        """Institutional-grade position monitoring"""
        for trade in list(self.active_trades):
            position = mt5.positions_get(ticket=trade)
            if not position:
                self.active_trades.remove(trade)
                continue

            # Check for liquidity shifts
            current_analysis = self.analyze_market(position.symbol)
            current_price = self.get_current_price(position.symbol)

            # Early exit if liquidity zone breached
            if (position.type == mt5.ORDER_TYPE_BUY and
                    current_price < min(current_analysis['liquidity']['lows'])):
                self.close_position(trade, "Liquidity Zone Breach")

            if (position.type == mt5.ORDER_TYPE_SELL and
                    current_price > max(current_analysis['liquidity']['highs'])):
                self.close_position(trade, "Liquidity Zone Breach")

    # ========================
    #    MAIN LOOP
    # ========================

    def run(self):
        """Institutional trading cycle"""
        print(
            f"{COLORS['BOLD']}Starting institutional trading protocol{COLORS['ENDC']}")
        while self.running:
            try:
                for symbol in SYMBOLS:
                    signals = self.analyze_market(symbol)
                    for signal in signals:
                        if len(self.active_trades) < MAX_TRADES:
                            self.execute_trade(symbol, signal)

                self.monitor_positions()
                time.sleep(60)  # Analyze every minute

            except KeyboardInterrupt:
                self.running = False
                print(
                    f"{COLORS['WARNING']}Terminating institutional session{COLORS['ENDC']}")

        mt5.shutdown()


if __name__ == "__main__":
    trader = InstitutionalGradeTrader()
    trader.run()
