


def list_dict_demo():
    ticker_list = ["AAPL", "GOOGL", "MSFT", "AMD", "TSLA"]

    #Use a list comprehension to filter only tickers starting with "A". Print the result.   
    a_tickers = [ticker for ticker in ticker_list if ticker.startswith("A")]
    print("Tickers starting with 'A':", a_tickers)

    #create a dictionary that maps tickers to prices
    ticker_prices = {"AAPL": 150.0, "GOOGL": 2800.0, "MSFT": 300.0, "AMD": 100.0, "TSLA": 700.0}

    # Use a dict comprehension to build expensive containing only entries where price > 200.


    expensive_tickers = {ticker: price for ticker, price in ticker_prices.items() if price > 200}    
    print("Expensive tickers (price > $200):", expensive_tickers)

if __name__ == "__main__":
    list_dict_demo()
