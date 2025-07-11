import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os

class DataFetcher:
    """Data fetching utilities for NSE stocks and market data"""
    
    def __init__(self):
        self.nse_stocks = self._load_nse_stock_list()
    
    def _load_nse_stock_list(self):
        """
        Load NSE stock list
        Returns a list of NSE stock symbols
        """
        # Stock symbols - Enhanced list (EXACT SAME as user provided)
        nse_stocks = [
            "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
            "BAJAJ-AUTO.NS", "BAJAJFINSV.NS", "BAJFINANCE.NS", "BHARTIARTL.NS", "BPCL.NS",
            "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
            "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
            "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ICICIGI.NS",
            "ICICIPRULI.NS", "INDUSINDBK.NS", "INFY.NS", "ITC.NS", "JSWSTEEL.NS",
            "KOTAKBANK.NS", "LT.NS", "LTIM.NS", "M&M.NS", "MARUTI.NS",
            "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS",
            "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS", "TATACONSUM.NS", "TATAMOTORS.NS",
            "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS",
            "UPL.NS", "WIPRO.NS", "DLF.NS", "SHRIRAMFIN.NS", "CHOLAFIN.NS",
            "BAJAJHLDNG.NS", "JINDALSTEL.NS", "RECLTD.NS", "ETERNAL.NS", "PFC.NS",
            "LODHA.NS", "SWIGGY.NS", "JIOFIN.NS", "ADANIPOWER.NS", "VBL.NS",
            "BANKBARODA.NS", "PNB.NS", "MOTHERSON.NS", "DMART.NS", "SIEMENS.NS",
            "TATAPOWER.NS", "JSWENERGY.NS", "ADANIGREEN.NS", "NAUKRI.NS", "ABB.NS",
            "TRENT.NS", "HAVELLS.NS", "IOC.NS", "SHREECEM.NS", "TVSMOTOR.NS",
            "AMBUJACEM.NS", "VEDL.NS", "BOSCHLTD.NS", "INDHOTEL.NS",
            "GAIL.NS", "GODREJCP.NS", "IRFC.NS", "ZYDUSLIFE.NS",
            "CANBK.NS", "BEL.NS", "DABUR.NS", "HAL.NS", "CGPOWER.NS"
        ]
        
        return nse_stocks
    
    def get_nse_stock_list(self):
        """
        Get the list of NSE stocks for scanning
        
        Returns:
            List of NSE stock symbols
        """
        return self.nse_stocks
    
    def get_stock_data(self, symbol, period="60d", interval="1d"):
        """
        Fetch stock data from Yahoo Finance
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Convert interval for yfinance compatibility
            interval_map = {
                "15m": "15m",
                "1h": "1h", 
                "4h": "1h",  # Will aggregate to 4h later
                "1d": "1d"
            }
            
            yf_interval = interval_map.get(interval, interval)
            
            # Fetch data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=yf_interval)
            
            if data.empty:
                return None
            
            # Convert to 4-hour data if requested
            if interval == "4h" and yf_interval == "1h":
                data = self._resample_to_4h(data)
            
            # Clean data
            data = data.dropna()
            
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _resample_to_4h(self, hourly_data):
        """
        Resample hourly data to 4-hour intervals
        
        Args:
            hourly_data: DataFrame with hourly OHLCV data
            
        Returns:
            DataFrame resampled to 4-hour intervals
        """
        try:
            # Resample to 4-hour intervals
            resampled = hourly_data.resample('4H').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            return resampled
            
        except Exception as e:
            print(f"Error resampling to 4h: {e}")
            return hourly_data
    
    def get_multiple_stocks_data(self, symbols, period="60d", interval="1d"):
        """
        Fetch data for multiple stocks
        
        Args:
            symbols: List of stock symbols
            period: Data period
            interval: Data interval
            
        Returns:
            Dict with symbol as key and DataFrame as value
        """
        stock_data = {}
        
        for symbol in symbols:
            try:
                data = self.get_stock_data(symbol, period, interval)
                if data is not None:
                    stock_data[symbol] = data
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue
        
        return stock_data
    
    def get_latest_price(self, symbol):
        """
        Get the latest price for a stock
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with latest price information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'current_price': info.get('currentPrice', 0),
                'previous_close': info.get('previousClose', 0),
                'change': info.get('currentPrice', 0) - info.get('previousClose', 0),
                'change_percent': ((info.get('currentPrice', 0) - info.get('previousClose', 0)) / 
                                 info.get('previousClose', 1)) * 100 if info.get('previousClose') else 0,
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0)
            }
            
        except Exception as e:
            print(f"Error fetching latest price for {symbol}: {e}")
            return None
    
    def check_market_hours(self):
        """
        Check if the market is currently open
        
        Returns:
            Boolean indicating if market is open
        """
        try:
            now = datetime.now()
            
            # NSE trading hours: 9:15 AM to 3:30 PM IST (Monday to Friday)
            market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
            
            # Check if it's a weekday and within trading hours
            is_weekday = now.weekday() < 5  # Monday = 0, Friday = 4
            is_trading_hours = market_open <= now <= market_close
            
            return is_weekday and is_trading_hours
            
        except Exception as e:
            print(f"Error checking market hours: {e}")
            return False
    
    def validate_symbol(self, symbol):
        """
        Validate if a stock symbol exists and has data
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            Boolean indicating if symbol is valid
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="5d", interval="1d")
            
            return not data.empty
            
        except Exception as e:
            print(f"Error validating symbol {symbol}: {e}")
            return False
