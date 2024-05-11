# filename: stock_price_plot.py

import yfinance as yf
import matplotlib.pyplot as plt

# Download stock data from start of 2021
nvda = yf.download('NVDA', start='2021-01-01')
tsla = yf.download('TSLA', start='2021-01-01')

# Plot close price
plt.figure(figsize=(14,7))
plt.plot(nvda.Close, label='NVDA')
plt.plot(tsla.Close, label='TSLA')
plt.title('NVDA and TSLA Stock Price 2021')
plt.ylabel('Price')
plt.xlabel('Date')
plt.legend()
plt.grid(True)

# Save the figure
plt.savefig('NVDA_TSLA_2021.png')