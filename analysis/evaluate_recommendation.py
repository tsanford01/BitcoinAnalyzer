# analysis\evaluate_recommendation.py
import datetime
import requests
import pandas as pd
import os
from datetime import datetime, timedelta
import dateutil.parser
import time


def get_actual_price_changes(start_date, end_date):
    # Convert start_date and end_date to UNIX timestamps
    global actual_price_changes
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())

    # Define the file path for the CSV file (including the 'data' directory)
    file_path = 'data/historical_data.csv'

    # Check if the file exists and is not empty
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        # Read the data from the CSV file
        actual_price_changes = pd.read_csv(file_path, engine='python')

        # Check if the data contains the desired date range
        min_timestamp = actual_price_changes['timestamp'].min()
        max_timestamp = actual_price_changes['timestamp'].max()

        if min_timestamp <= start_timestamp and max_timestamp >= end_timestamp:
            # Filter the data for the desired date range
            actual_price_changes = actual_price_changes[(actual_price_changes['timestamp'] >= start_timestamp) &
                                                        (actual_price_changes['timestamp'] <= end_timestamp)]
        else:
            # Fetch missing data from the API and append it to the existing data
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
            params = {
                "vs_currency": "usd",
                "from": start_timestamp,
                "to": end_timestamp
            }
            while True:
                response = requests.get(url, params=params)
                # Handle rate limiting (status code 429)
                if response.status_code == 429:
                    time.sleep(60)  # Wait for 60 seconds before retrying
                    continue
                if response.ok:
                    data = response.json()
                    new_data = pd.DataFrame(data.get("prices", []), columns=['timestamp', 'price'])

                    # Append new_data to actual_price_changes and drop duplicates
                    actual_price_changes = pd.concat([actual_price_changes, new_data]).drop_duplicates()
                    actual_price_changes.to_csv(file_path, index=False)
                    break
                else:
                    raise Exception(f"Error: Received status code {response.status_code} from API.")
    else:
        # Fetch data from the API and save it to the file
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
        params = {
            "vs_currency": "usd",
            "from": start_timestamp,
            "to": end_timestamp
        }
        while True:
            response = requests.get(url, params=params)
            # Handle rate limiting (status code 429)
            if response.status_code == 429:
                time.sleep(60)  # Wait for 60 seconds before retrying
                continue
            if response.ok:
                data = response.json()
                actual_price_changes = pd.DataFrame(data.get("prices", []), columns=['timestamp', 'price'])
                actual_price_changes.to_csv(file_path, index=False)
                break
            else:
                raise Exception(f"Error: Received status code {response.status_code} from API.")

    return actual_price_changes


# Attempt to read existing data
try:
    file_path = 'data/historical_data.csv'
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        # Use the 'python' engine when reading the CSV file
        existing_data = pd.read_csv(file_path, engine='python')
        if not existing_data['timestamp'].empty:
            last_date_in_existing_data = existing_data['timestamp'].max()
            try:
                start_date = (datetime.fromtimestamp(last_date_in_existing_data) + timedelta(days=1)).strftime(
                    '%Y-%m-%d')
            except (OSError, ValueError):
                # Fallback mechanism: If the timestamp is invalid, go back 30 days
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                start_date = start_date.strftime('%Y-%m-%d')
        else:
            # Fallback mechanism: If there is no timestamp data, go back 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            start_date = start_date.strftime('%Y-%m-%d')
    else:
        # Fallback mechanism: If the file is empty or does not exist, go back 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        start_date = start_date.strftime('%Y-%m-%d')
except FileNotFoundError:
    # Fallback mechanism: If there is no existing data, go back 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_date = start_date.strftime('%Y-%m-%d')

# Set the end date as the current date
end_date = datetime.now().strftime('%Y-%m-%d')

# Fetch data using the selected start and end dates
actual_price_changes = get_actual_price_changes(start_date, end_date)
# print(actual_price_changes)


def evaluate_recommendation(current_price):
    try:
        # Define the file path for the recommendations.txt file (including the 'data' directory)
        recommendations_file_path = 'data/recommendations.txt'
        evaluations_file_path = 'data/recommendation_evaluations.txt'

        # Get the most recent recommendation from our file
        with open(recommendations_file_path, 'r') as file:
            lines = file.readlines()
            last_line = lines[-1].strip()
        # Extract the date and the recommendation from the line
        date_str, recommendation_str = last_line.split('Bitcoin price has', 1)
        recommendation_str = 'Bitcoin price has' + recommendation_str
        date = dateutil.parser.parse(date_str.strip())

        # Get the Bitcoin price at the time of the recommendation
        one_hour_ago = (date - datetime.timedelta(hours=1)).strftime('%s')
        while True:
            response = requests.get(f'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range'
                                    f'?vs_currency=usd&from={one_hour_ago}&to=9999999999')
            # Handle rate limiting (status code 429)
            if response.status_code == 429:
                time.sleep(60)  # Wait for 60 seconds before retrying
                continue
            if response.ok:
                historical_data = response.json()
                opening_price = historical_data['prices'][0][1]
                break
            else:
                raise Exception(f"Error: Received status code {response.status_code} from API.")

        # Calculate the percentage change
        percentage_change = (current_price - opening_price) / opening_price * 100

        # Save the result to a file
        with open(evaluations_file_path, 'a') as file:
            file.write(f'{date} {percentage_change:.2f} {recommendation_str}')

        return {
            "message": f'The percentage change since the last recommendation was {percentage_change:.2f} percent.'}, None
    except Exception as e:
        return {"message": "Error: {}".format(str(e))}, None


