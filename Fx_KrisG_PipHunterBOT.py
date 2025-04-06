import os
import sys
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from datetime import datetime
import talib as ta

# ========================
#    GLOBAL CONFIGURATION
# ========================
SYMBOL = "BTCUSDm"
TIMEFRAME = mt5.TIMEFRAME_M5
RISK_PER_TRADE = 0.02  # 2% risk per trade
MAX_TRADES = 5
MAX_GROWTH = 0.30  # 30% capital growth limit
MAX_DRAWDOWN = -0.10  # 10% max drawdown
SPREAD_LIMIT = 5.0  # Maximum allowed spread (points)
ATR_PERIOD = 14
EMA_FAST = 8
EMA_SLOW = 21
RSI_PERIOD = 14
RR_RATIO = 2.5  # Risk-Reward Ratio

# ANSI Escape Codes for display
COLORS = {
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'CYAN': '\033[96m',
    'TRADING': '\033[93m',
    'PROFIT': '\033[92m',
    'LOSS': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}

class AdvancedCryptoScalper:
    def __init__(self):
        self.running = True
        self.active_trades = []
        self.trade_count = 0
        self.win_trades = 0
        self.loss_trades = 0
        self.total_rr = 0.0
        self.last_signal_reason = ""
        self.start_time = datetime.now()
        self.last_update = time.time()
        self.current_balance = 0.0
        
        try:
            print(f"{COLORS['OKBLUE']}Connecting to MT5...{COLORS['ENDC']}")
            if not self.initialize_mt5():
                raise ConnectionError("Failed to connect to MT5")
            
            print(f"{COLORS['OKBLUE']}Validating account...{COLORS['ENDC']}")
            self.validate_account()
            self.setup_display()
            
        except Exception as e:
            self.shutdown(f"Initialization failed: {str(e)}")

    def initialize_mt5(self):
        """Initialize MT5 connection with detailed logging"""
        for attempt in range(3):
            try:
                if not mt5.initialize():
                    print(f"{COLORS['FAIL']}MT5 initialization failed (attempt {attempt+1}/3){COLORS['ENDC']}")
                    time.sleep(1)
                    continue
                    
                if not mt5.symbol_select(SYMBOL, True):
                    print(f"{COLORS['FAIL']}Symbol selection failed{COLORS['ENDC']}")
                    mt5.shutdown()
                    return False
                    
                print(f"{COLORS['OKGREEN']}Successfully connected to MT5{COLORS['ENDC']}")
                return True
                
            except Exception as e:
                print(f"{COLORS['FAIL']}Connection error: {str(e)}{COLORS['ENDC']}")
                time.sleep(2)
                
        return False

    def validate_account(self):
        """Validate account information with proper error handling"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                raise ValueError("Failed to retrieve account information")
                
            self.initial_balance = account_info.balance
            if self.initial_balance <= 10:
                raise ValueError("Limited Funds! Add minimum $10 to get started.")
                
            self.current_balance = self.initial_balance
            print(f"\n{COLORS['OKGREEN']}=== Account Information ===")
            print(f"Login: {account_info.login}")
            print(f"Balance: {self.initial_balance:.2f}")
            print(f"Leverage: 1:{account_info.leverage}")
            print(f"Currency: {account_info.currency}")
            print(f"==========================={COLORS['ENDC']}\n")
            
        except Exception as e:
            raise RuntimeError(f"Warning🚨: {str(e)}")

    def get_current_spread(self):
        """Get current spread in points (corrected calculation)"""
        try:
            tick = mt5.symbol_info_tick(SYMBOL)
            if tick:
                return tick.ask - tick.bid  # Direct spread value
            return 0.0
        except:
            return 0.0

    def setup_display(self):
        """Initialize professional console display"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{COLORS['BOLD']}{COLORS['HEADER']}=== AI QUANT SCALPER v3.0 ===")
        print(f"{COLORS['OKBLUE']}Symbol: {SYMBOL} | Timeframe: 5M | Strategy: Fib/EMA/RSI/MACD")
        print(f"Risk Management: {RISK_PER_TRADE*100}% per trade | RR: 1:{RR_RATIO}")
        print("---------------------------------------------------{COLORS['ENDC']}")

    # ========================
    #    CORE TRADING LOGIC
    # ========================
    
    def analyze_market(self):
        """Generate trade signals with detailed condition checking"""
        try:
            df = self.get_market_data()
            if df is None or len(df) < 100:
                return False, False, "Insufficient data"

            df = self.calculate_indicators(df)
            current = df.iloc[-1]
            prev = df.iloc[-2]

            fib_levels = self.calculate_fibonacci(df)
            reasons = []

            # Long Conditions
            long_conditions = {
                'EMA Cross': current['ema_fast'] > current['ema_slow'] and prev['ema_fast'] <= prev['ema_slow'],
                'RSI Oversold': current['rsi'] < 60,
                'Fibonacci Support': current['close'] > fib_levels['61.8'],
                'MACD Bullish': current['macd'] > current['macd_signal'],
                'Volume Spike': current['tick_volume'] > df['tick_volume'].rolling(20).mean().iloc[-2] * 1.2
            }
            
            # Short Conditions
            short_conditions = {
                'EMA Cross': current['ema_fast'] < current['ema_slow'] and prev['ema_fast'] >= prev['ema_slow'],
                'RSI Overbought': current['rsi'] > 40,
                'Fibonacci Resistance': current['close'] < fib_levels['38.2'],
                'MACD Bearish': current['macd'] < current['macd_signal'],
                'Volume Spike': current['tick_volume'] > df['tick_volume'].rolling(20).mean().iloc[-2] * 1.5
            }

            long_reasons = [k for k,v in long_conditions.items() if v]
            short_reasons = [k for k,v in short_conditions.items() if v]

            if len(long_reasons) >= 2 and self.valid_spread():
                return True, False, "LONG: " + " + ".join(long_reasons)
            
            if len(short_reasons) >= 2 and self.valid_spread():
                return False, True, "SHORT: " + " + ".join(short_reasons)

            return False, False, "Waiting for confirmation..."

        except Exception as e:
            self.log_error(f"Analysis error: {str(e)}")
            return False, False, "Analysis error"

    def calculate_indicators(self, df):
        """Calculate technical indicators"""
        df['ema_fast'] = ta.EMA(df['close'], EMA_FAST)
        df['ema_slow'] = ta.EMA(df['close'], EMA_SLOW)
        df['rsi'] = ta.RSI(df['close'], RSI_PERIOD)
        df['macd'], df['macd_signal'], _ = ta.MACD(df['close'])
        df['atr'] = ta.ATR(df['high'], df['low'], df['close'], ATR_PERIOD)
        return df.dropna()

    def calculate_fibonacci(self, df):
        """Calculate Fibonacci retracement levels"""
        lookback = 20
        high = df['high'].rolling(lookback).max().iloc[-1]
        low = df['low'].rolling(lookback).min().iloc[-1]
        diff = high - low
        
        return {
            '23.6': high - diff * 0.236,
            '38.2': high - diff * 0.382,
            '50.0': high - diff * 0.5,
            '61.8': high - diff * 0.618
        }

    # ========================
    #    RISK MANAGEMENT
    # ========================
    
    def manage_risk(self):
        """Check trading limits and manage positions"""
        if self.check_limits():
            return False
            
        self.current_balance = mt5.account_info().equity
        self.manage_positions()
        return True

    def check_limits(self):
        """Enforce growth/drawdown limits"""
        growth = (self.current_balance - self.initial_balance) / self.initial_balance
        drawdown = (self.initial_balance - self.current_balance) / self.initial_balance

        if growth >= MAX_GROWTH:
            self.shutdown(f"{COLORS['OKGREEN']}Profit target reached (+{growth*100:.1f}%)")
            return True
            
        if drawdown >= abs(MAX_DRAWDOWN):
            self.shutdown(f"{COLORS['FAIL']}Drawdown limit hit (-{drawdown*100:.1f}%)")
            return True
            
        return False

    def calculate_position_size(self):
        """Dynamic position sizing with active trade adjustment"""
        active_trades = len(self.active_trades)
        risk_multiplier = 1 / (active_trades + 1)  # Reduce risk with more trades
        
        atr = self.get_current_atr()
        if atr == 0:
            return 0.01
            
        risk_amount = self.current_balance * RISK_PER_TRADE * risk_multiplier
        lot_size = (risk_amount / (atr * 100)) / 100  # BTCUSDm specific
        return round(max(min(lot_size, 50), 0.01), 2)

    # ========================
    #    TRADE EXECUTION
    # ========================
    
    
    def execute_trade(self, direction, reason):
        """Execute trade with detailed logging"""
        if not self.valid_spread():
            return
            
        try:
            lot_size = self.calculate_position_size()
            tick = mt5.symbol_info_tick(SYMBOL)
            price = tick.ask if direction == 'BUY' else tick.bid
            atr = self.get_current_atr()
            
            # Calculate SL/TP based on ATR and RR
            sl_distance = atr * 1.5
            tp_distance = sl_distance * RR_RATIO
            
            if direction == 'BUY':
                sl = price - sl_distance
                tp = price + tp_distance
            else:
                sl = price + sl_distance
                tp = price - tp_distance

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": SYMBOL,
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_BUY if direction == 'BUY' else mt5.ORDER_TYPE_SELL,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 10,
                "magic": 3000,
                "comment": reason,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.log_error(f"Trade failed: {result.comment}")
                return
                
            self.trade_count += 1
            self.active_trades.append({
                'ticket': result.order,
                'time': datetime.now(),
                'direction': direction,
                'lot_size': lot_size,
                'sl': sl,
                'tp': tp
            })
            
            self.last_signal_reason = f"{direction} - {reason}"
            self.update_display()

        except Exception as e:
            self.log_error(f"Trade execution error: {str(e)}")

    # ========================
    #    POSITION MANAGEMENT
    # ========================
    
    def manage_positions(self):
        """Manage open positions with trailing SL"""
        try:
            for trade in list(self.active_trades):
                position = mt5.positions_get(ticket=trade['ticket'])
                if not position:
                    self.active_trades.remove(trade)
                    continue
                    
                position = position[0]
                current_price = mt5.symbol_info_tick(SYMBOL).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(SYMBOL).ask
                
                # Update trailing stop
                if position.profit > 0:
                    self.update_trailing_sl(position, current_price)

                # Check if position needs closing
                self.check_position_health(position)

        except Exception as e:
            self.log_error(f"Position management error: {str(e)}")

    def update_trailing_sl(self, position, current_price):
        """Update trailing stop loss dynamically"""
        entry_price = position.price_open
        sl_distance = abs(entry_price - position.sl)
        buffer = sl_distance * 0.5  # Trail at 50% of initial SL distance
        
        if position.type == mt5.ORDER_TYPE_BUY:
            new_sl = current_price - buffer
            if new_sl > position.sl:
                self.modify_sl(position.ticket, new_sl)
        else:
            new_sl = current_price + buffer
            if new_sl < position.sl:
                self.modify_sl(position.ticket, new_sl)

    def modify_sl(self, ticket, new_sl):
        """Modify stop loss level"""
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl": new_sl,
            "deviation": 10,
        }
        mt5.order_send(request)

    def check_position_health(self, position):
        """Check position status and close if needed"""
        duration = (datetime.now() - position.time_update).seconds
        pnl = position.profit
        rr_achieved = abs(pnl) / (abs(position.price_open - position.sl) * position.volume)

        # Close position if RR target achieved
        if rr_achieved >= RR_RATIO:
            self.close_position(position, f"RR Target ({rr_achieved:.1f}R)")
        # Close if position exceeds maximum duration
        elif duration >= 300:  # 5 minutes
            self.close_position(position, "Time Expiry")

    def close_position(self, position, reason):
        """Close position and update statistics"""
        try:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": SYMBOL,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position.ticket,
                "price": mt5.symbol_info_tick(SYMBOL).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(SYMBOL).ask,
                "deviation": 10,
                "magic": 3000,
                "comment": reason,
            }
            
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                if position.profit > 0:
                    self.win_trades += 1
                else:
                    self.loss_trades += 1
                
                self.total_rr += abs(position.profit) / (abs(position.price_open - position.sl) * position.volume)
                self.active_trades = [t for t in self.active_trades if t['ticket'] != position.ticket]

        except Exception as e:
            self.log_error(f"Close position error: {str(e)}")

    # ========================
    #    UTILITIES & DISPLAY
    # ========================
    def update_display(self):
        """Update console display with trading metrics"""
        try:
            win_rate = self.win_trades / self.trade_count * 100 if self.trade_count > 0 else 0
            avg_rr = self.total_rr / self.trade_count if self.trade_count > 0 else 0
            growth = (self.current_balance - self.initial_balance) / self.initial_balance * 100

            print(f"\033[4;0H{COLORS['CYAN']}Time: {datetime.now().strftime('%H:%M:%S')} | Running: {str(datetime.now() - self.start_time).split('.')[0]}")
            print(f"\033[5;0H{COLORS['BOLD']}Balance: ${self.current_balance:.2f} | Growth: {growth:+.2f}%")
            print(f"\033[6;0HTrades: {self.trade_count} | Active: {len(self.active_trades)} | Spread: {self.get_current_spread():.1f}")
            print(f"\033[7;0H{COLORS['PROFIT']}Win Rate: {win_rate:.1f}% | Avg RR: {avg_rr:.1f}")
            print(f"\033[8;0H{COLORS['TRADING']}Last Signal: {self.last_signal_reason}")
            print(f"\033[9;0H{COLORS['PROFIT']}Wins: {self.win_trades} {COLORS['LOSS']}Losses: {self.loss_trades}")
            print(f"\033[10;0H{COLORS['OKBLUE']}---------------------------------------------------{COLORS['ENDC']}")

        except Exception as e:
            self.log_error(f"Display update error: {str(e)}")
            
    # ========================
    #    POSITION MANAGEMENT
    # ========================
    
    def manage_positions(self):
        """Manage all open positions with trailing stops and health checks"""
        try:
            current_time = datetime.now()
            positions_to_remove = []
            
            for trade in self.active_trades:
                position = mt5.positions_get(ticket=trade['ticket'])
                if not position:
                    positions_to_remove.append(trade)
                    continue
                
                position = position[0]
                current_price = mt5.symbol_info_tick(SYMBOL).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(SYMBOL).ask
                
                # Update trailing stop loss
                self.update_trailing_sl(position, current_price)
                
                # Check position health
                if self.check_position_health(position):
                    positions_to_remove.append(trade)
            
            # Remove closed positions from active list
            for trade in positions_to_remove:
                if trade in self.active_trades:
                    self.active_trades.remove(trade)
                    
        except Exception as e:
            self.log_error(f"Position management error: {str(e)}")

    def check_position_health(self, position):
        """Check if position needs to be closed"""
        duration = (datetime.now() - position.time_update).total_seconds()
        pnl = position.profit
        rr_achieved = abs(pnl) / (abs(position.price_open - position.sl) * position.volume)

        # Close conditions
        if rr_achieved >= RR_RATIO:
            self.close_position(position, f"Achieved {rr_achieved:.1f}R")
            return True
        elif duration >= 300:  # 5 minutes
            self.close_position(position, "Time Expiry")
            return True
        return False

    # ========================
    #    HELPER FUNCTIONS
    # ========================
    
    def get_market_data(self):
        """Retrieve OHLC data with error handling"""
        try:
            rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 100)
            return pd.DataFrame(rates) if rates is not None else None
        except Exception as e:
            self.log_error(f"Data retrieval error: {str(e)}")
            return None

    def valid_spread(self):
        """Check if spread is within acceptable limits"""
        spread = self.get_current_spread()
        return spread <= SPREAD_LIMIT if spread is not None else False

    def get_current_spread(self):
        """Get current spread in points"""
        try:
            tick = mt5.symbol_info_tick(SYMBOL)
            return (tick.ask - tick.bid) * 10**5  # Convert to points
        except:
            return 0.0

    def get_current_atr(self):
        """Get current ATR value"""
        df = self.get_market_data()
        if df is not None and not df.empty:
            return ta.ATR(df['high'], df['low'], df['close'], ATR_PERIOD).iloc[-1]
        return 0.0

    def log_error(self, message):
        """Log errors with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{COLORS['FAIL']}[{timestamp}] ERROR: {message}{COLORS['ENDC']}")

    def shutdown(self, message=""):
        """Graceful shutdown procedure"""
        print(f"\n{COLORS['BOLD']}Initiating shutdown...{COLORS['ENDC']}")
        self.close_all_positions()
        mt5.shutdown()
        print(f"{COLORS['BOLD']}{message}{COLORS['ENDC']}")
        print(f"Final balance: {self.current_balance:.2f}")
        print(f"Total trades: {self.trade_count}")
        print(f"Win rate: {self.win_trades/self.trade_count*100:.1f}%" if self.trade_count > 0 else "")
        sys.exit(0)

    def close_all_positions(self):
        """Close all open positions on shutdown"""
        try:
            positions = mt5.positions_get(symbol=SYMBOL)
            if positions:
                print(f"{COLORS['WARNING']}Closing all open positions...{COLORS['ENDC']}")
                for position in positions:
                    self.close_position(position, "Shutdown")
        except Exception as e:
            self.log_error(f"Position closure error: {str(e)}")

    # ========================
    #    MAIN LOOP
    # ========================
    
    
    def run(self):
        """Main trading loop"""
        try:
            while self.running and self.manage_risk():
                # Get trading signal
                long_signal, short_signal, signal_reason = self.analyze_market()
                
                # Execute trades
                if long_signal and len(self.active_trades) < MAX_TRADES:
                    self.execute_trade('BUY', signal_reason)
                elif short_signal and len(self.active_trades) < MAX_TRADES:
                    self.execute_trade('SELL', signal_reason)
                
                # Update display every 0.5 seconds
                if time.time() - self.last_update > 0.5:
                    self.update_display()
                    self.last_update = time.time()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.shutdown("User interrupted operation")
        except Exception as e:
            self.shutdown(f"Critical error: {str(e)}")
            

if __name__ == "__main__":
    try:
        bot = AdvancedCryptoScalper()
        bot.run()
    except Exception as e:
        print(f"{COLORS['FAIL']}Fatal initialization error: {str(e)}{COLORS['ENDC']}")
