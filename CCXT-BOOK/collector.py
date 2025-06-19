import ccxt
import pandas as pd
import time
import threading
import os
from datetime import datetime

# Get the exchange name from the environment variable (required, no default)
exchange_name = os.getenv('EXCHANGE_NAME')

if exchange_name is None:
    raise ValueError("Environment variable 'EXCHANGE_NAME' is not set.")

# Initialize ccxt exchange dynamically based on the environment variable
try:
    exchange = getattr(ccxt, exchange_name)()
except AttributeError:
    raise ValueError(f"Exchange '{exchange_name}' is not supported by ccxt.")

# Define a set to store unique transaction IDs (tids) for each pair
unique_tids = {
    'BTC/USDT': set(),
    'ETH/USDT': set(),
    'ADA/USDT': set(),
    'XRP/USDT': set()
}

# Create an empty DataFrame for each trading pair for trades, order books, and spreads
dfs = {
    'BTC/USDT': pd.DataFrame(columns=['tid', 'timestamp', 'price', 'amount', 'type']),
    'ETH/USDT': pd.DataFrame(columns=['tid', 'timestamp', 'price', 'amount', 'type']),
    'ADA/USDT': pd.DataFrame(columns=['tid', 'timestamp', 'price', 'amount', 'type']),
    'XRP/USDT': pd.DataFrame(columns=['tid', 'timestamp', 'price', 'amount', 'type'])
}
order_books_dfs = {pair: pd.DataFrame(columns=['timestamp', 'bid', 'ask', 'bid_volume', 'ask_volume']) for pair in unique_tids.keys()}
spreads_dfs = {pair: pd.DataFrame(columns=['timestamp', 'spread']) for pair in unique_tids.keys()}

# Function to fetch and process trades for a specific pair
def fetch_trades_ccxt(pair):
    global dfs
    try:
        trades = exchange.fetch_trades(pair, limit=100)
        new_trades = []
        
        for trade in trades:
            tid = trade['id']
            if tid not in unique_tids[pair]:
                unique_tids[pair].add(tid)
                new_trades.append({
                    'tid': tid,
                    'timestamp': trade['timestamp'],
                    'price': trade['price'],
                    'amount': trade['amount'],
                    'type': trade['side']
                })

        if new_trades:
            dfs[pair] = pd.concat([dfs[pair], pd.DataFrame(new_trades)], ignore_index=True)
    except Exception as e:
        print(f"Error fetching trades for {pair}: {e}")

# Function to fetch and process order book for a specific pair
def fetch_order_book(pair):
    global order_books_dfs, spreads_dfs
    try:
        order_book = exchange.fetch_order_book(pair)
        timestamp = datetime.now()
        
        bid = order_book['bids'][0][0] if order_book['bids'] else None
        ask = order_book['asks'][0][0] if order_book['asks'] else None
        bid_volume = order_book['bids'][0][1] if order_book['bids'] else None
        ask_volume = order_book['asks'][0][1] if order_book['asks'] else None
        spread = ask - bid if bid and ask else None

        order_books_dfs[pair] = pd.concat([order_books_dfs[pair], pd.DataFrame([{
            'timestamp': timestamp,
            'bid': bid,
            'ask': ask,
            'bid_volume': bid_volume,
            'ask_volume': ask_volume
        }])], ignore_index=True)
        
        if spread is not None:
            spreads_dfs[pair] = pd.concat([spreads_dfs[pair], pd.DataFrame([{
                'timestamp': timestamp,
                'spread': spread
            }])], ignore_index=True)
    except Exception as e:
        print(f"Error fetching order book for {pair}: {e}")

# Function to save trades to CSV every 500ms for a specific pair
def save_trades_to_csv(pair):
    while True:
        fetch_trades_ccxt(pair)
        
        current_time = datetime.now().strftime('%Y-%m-%d')
        directory = f'/data/ccxt-data-book/{exchange_name}/{pair.replace("/", "_")}/'
        os.makedirs(directory, exist_ok=True)
        
        filename = f'{directory}trades_ccxt_{current_time}.csv'
        
        dfs[pair].to_csv(filename, index=False)
        time.sleep(0.5)

# Function to save order book and spread data every minute for a specific pair
def save_order_books_and_spreads_to_csv(pair):
    while True:
        fetch_order_book(pair)
        
        current_time = datetime.now().strftime('%Y-%m-%d')
        directory = f'/data/ccxt-data-book/{exchange_name}/{pair.replace("/", "_")}/'
        os.makedirs(directory, exist_ok=True)
        
        order_book_filename = f'{directory}order_book_{current_time}.csv'
        spread_filename = f'{directory}spreads_{current_time}.csv'
        
        order_books_dfs[pair].to_csv(order_book_filename, index=False)
        spreads_dfs[pair].to_csv(spread_filename, index=False)
        
        time.sleep(60)  # Wait for 1 minute

# Create and start a separate thread for each trading pair to save trades, order books, and spreads
pairs = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'XRP/USDT']
threads = []

for pair in pairs:
    order_book_thread = threading.Thread(target=save_order_books_and_spreads_to_csv, args=(pair,))
    order_book_thread.daemon = True
    order_book_thread.start()
    threads.append(order_book_thread)

# Keep the main thread running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program interrupted, saving remaining data.")
    for pair in pairs:
        order_books_dfs[pair].to_csv(f'/data/ccxt-data-book/{exchange_name}/order_books_{pair.replace("/", "_")}_final.csv', index=False)
        spreads_dfs[pair].to_csv(f'/data/ccxt-data-book/{exchange_name}/spreads_{pair.replace("/", "_")}_final.csv', index=False)
