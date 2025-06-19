# Crypto Exchange Trade Data Collector

## 📚 Library
- [CCXT](https://github.com/ccxt/ccxt) — A unified API for over 53 cryptocurrency exchanges.

## 🛠 Tools
- Docker — Containerized deployment and orchestration.

---

## ⚙️ How CCXT Works

CCXT is a unified API that allows fetching data from the public and private APIs of major cryptocurrency exchanges. It simplifies the integration by offering a consistent interface for accessing trades, order books, and other market data.

---

## 🎯 Our Goal

To fetch **trade data** from all supported exchanges **without missing or duplicating trades**.

This system currently supports the following trading pairs:
- `BTC_USDT`
- `ETH_USDT`
- `ADA_USDT`
- `XRP_USDT`

---

## 🚀 Implementation Strategy

- Fetch the **last 1000 trades** every **500 milliseconds**.
- Save new trades to a file in the format:  



### Architecture Overview

- **1 container per exchange**.
- **Each trading pair is managed by a dedicated thread** within the container.
- Each thread:
- Sleeps for 500ms.
- Fetches the latest 1000 trades.
- Appends any new trades to the corresponding file.

---

## 🧱 Deployment

- An **orchestrator container** is responsible for launching all exchange-specific containers.
- **Docker volumes** are used to ensure data persists on the host machine.

### How to Run

1. Build the Docker images (if needed).
2. Start the orchestrator container:
 ```bash
 docker run --rm your-orchestrator-image
