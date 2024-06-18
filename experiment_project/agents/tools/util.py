import yfinance as yf
def stock_data(symbol:str,start_date:str,end_date:str):
    """
       收集指定股票在指定日期范围内的价格、成交量和市场趋势数据。

       参数:
       symbol (str): 股票代码，例如 'NVDA' 代表 NVIDIA，'TSLA' 代表 Tesla。
       start_date (str): 数据收集的起始日期，格式为 'YYYY-MM-DD'。
       end_date (str): 数据收集的结束日期，格式为 'YYYY-MM-DD'。

       返回:
       Pandas DataFrame: 包含指定股票在指定日期范围内的价格、成交量和市场趋势数据。

       示例:
       data = stock_data('NVDA', '2023-01-01', '2023-12-31')
    """
    data = yf.download(symbol, start=start_date, end=end_date)
    return data