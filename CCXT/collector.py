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

# Function to fetch and save trades for a specific pair
def fetch_and_save_trades(pair):
    while True:
        current_date = datetime.now().strftime('%Y-%m-%d')
        try:
            # Fetch last 100 trades for the specified pair
            trades = exchange.fetch_trades(pair, limit=100)
            new_trades = []
            
            # Loop through each trade and add it to the list if the tid is unique
            for trade in trades:
                tid = trade['id']
                if tid not in unique_tids[pair]:
                    unique_tids[pair].add(tid)
                    new_trades.append({
                        'tid': tid,
                        'timestamp': trade['timestamp'],
                        'price': trade['price'],
                        'amount': trade['amount'],
                        'type': trade['side']  # buy/sell
                    })

            if new_trades:
                # Convert new trades to a DataFrame
                df = pd.DataFrame(new_trades)
                
                # Create directory if it doesn't exist
                directory = f'/data/ccxt-data/{exchange_name}/{pair.replace("/", "_")}/'
                os.makedirs(directory, exist_ok=True)
                
                # Define the filename based on the current date
                filename = f'{directory}trades_ccxt_{current_date}.csv'
                
                # If the file exists, append to it; otherwise, create a new file
                if os.path.exists(filename):
                    df.to_csv(filename, mode='a', header=False, index=False)  # Append new data
                else:
                    df.to_csv(filename, mode='w', header=True, index=False)  # Write new data

        except Exception as e:
            print(f"Error fetching trades for {pair}: {e}")
        
        time.sleep(0.5)  # Wait for 500 milliseconds

# Create and start a separate thread for each trading pair
pairs = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'XRP/USDT']
threads = []

for pair in pairs:
    thread = threading.Thread(target=fetch_and_save_trades, args=(pair,))
    thread.daemon = True
    thread.start()
    threads.append(thread)

# Keep the main thread running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program interrupted.")
