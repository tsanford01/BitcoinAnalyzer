# data\data_retrieval.py

import pandas as pd


def get_historical_data():
    # Define the file path for the historical_data.csv file
    file_path = 'data/historical_data.csv'

    try:
        # Read the data from the CSV file
        historical_data = pd.read_csv(file_path, engine='python')
        return historical_data
    except FileNotFoundError:
        print("Error: The historical_data.csv file was not found.")
        return None
    except Exception as e:
        print(f"Error: Failed to read historical data from CSV file. {e}")
        return None
