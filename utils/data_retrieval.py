# data\data_retrieval.py
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def get_historical_data():
    # Define the file path for the historical_data.csv file
    file_path = 'data/historical_data.csv'

    try:
        # Read the data from the CSV file
        historical_data = pd.read_csv(file_path)
        return historical_data
    except FileNotFoundError:
        print("Error: The historical_data.csv file was not found.")
        return None
    except Exception as e:
        print(f"Error: Failed to read historical data from CSV file. {e}")
        return None


def get_current_bitcoin_price():
    # CoinGecko API URL for Bitcoin data
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

    try:
        # Send GET request to the API
        response = requests.get(url)

        # Check for successful response
        if response.status_code == 200:
            # Parse response JSON
            data = response.json()

            # Extract Bitcoin price in USD
            bitcoin_price = data["bitcoin"]["usd"]

            # Return the current Bitcoin price
            return bitcoin_price
        else:
            print(f"Error: Received status code {response.status_code} from API.")
            return None
    except Exception as e:
        print(f"Error: Failed to retrieve Bitcoin price. {e}")
        return None


# Example usage of the function
if __name__ == "__main__":
    current_price = get_current_bitcoin_price()
    if current_price is not None:
        print(f"Current Bitcoin price (USD): {current_price}")
    else:
        print("Failed to retrieve current Bitcoin price.")
