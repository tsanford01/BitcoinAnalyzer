# analysis\make_recommendation.py
import requests
import time
from analysis.evaluate_recommendation import evaluate_recommendation


def get_price_trend(days, current_price):
    while True:
        try:
            # Get the price data from the last `days` days
            response = requests.get(
                f'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}')

            # Handle rate limiting (status code 429)
            if response.status_code == 429:
                time.sleep(60)  # Wait for 60 seconds before retrying
                continue

            bitcoin_price = response.json()

            # Calculate the average price over the last `days` days
            average_price = sum([price[1] for price in bitcoin_price['prices']]) / len(bitcoin_price['prices'])

            # Calculate the percentage difference between the average price and the current price
            percentage_difference = (current_price - average_price) / average_price * 100

            return percentage_difference

        except Exception as e:
            print(f"Error: {e}")
            return None


def get_market_sentiment():
    while True:
        try:
            # Get the sentiment of the market
            response = requests.get('https://api.coingecko.com/api/v3/coins/bitcoin/sentiment')

            # Handle rate limiting (status code 429)
            if response.status_code == 429:
                time.sleep(60)  # Wait for 60 seconds before retrying
                continue

            # Check if the response status code is OK (200)
            if response.status_code == requests.codes.ok:
                sentiment = response.json()['sentiment_votes_up_percentage']
                return sentiment
            else:
                raise Exception(f"Error: Received status code {response.status_code} from API.")

        except Exception as e:
            print(f"Error: {e}")
            return None


def make_recommendation(current_price):
    try:
        # Evaluate the most recent recommendation
        result, error = evaluate_recommendation(current_price)
        if error is not None:
            return None, error
        # get the percentage change since the last recommendation
        with open('data/recommendation_evaluations.txt', 'r') as file:
            lines = file.readlines()
            if len(lines) < 2:
                return {'message': 'Not enough data to make a recommendation.'}, None
            last_line = lines[-2].strip()
            previous_percentage_change = float(last_line.split(' ')[1])
        # calculate the percentage change since the last recommendation
        percentage_change = (current_price - previous_percentage_change) / previous_percentage_change * 100
        # calculate the long-term trend over the last 7 days
        long_term_trend = get_price_trend(7)
        # get the market sentiment
        sentiment = get_market_sentiment()

        # Calculate the confidence level based on percentage change, long-term trend, and market sentiment
        confidence_level = abs(percentage_change) + abs(long_term_trend) + sentiment
        confidence_level = min(confidence_level, 100)  # Cap the confidence level at 100

        # Define arbitrary confidence levels for the examples
        high_confidence = 85
        low_confidence = 50

        # Use the information to make a recommendation
        if percentage_change > 5 and long_term_trend > 2 and sentiment > 60:
            message = (f'Bitcoin price has increased by {percentage_change:.2f}% since the last recommendation, '
                       f'long-term trend is {long_term_trend:.2f}% positive, and market sentiment is {sentiment:.2f}% '
                       f'positive. It is recommended to sell.')
            confidence_level = high_confidence
        elif percentage_change < -5 and long_term_trend < -2 and sentiment < 40:
            message = (f'Bitcoin price has decreased by {abs(percentage_change):.2f}% since the last recommendation, '
                       f'long-term trend is {long_term_trend:.2f}% negative, and market sentiment is {sentiment:.2f}% '
                       f'negative. It is recommended to buy.')
            confidence_level = high_confidence
        else:
            message = 'No significant change in Bitcoin price since the last recommendation.'
            confidence_level = low_confidence

        # Return a dictionary containing both the message and the confidence level
        return {'message': message, 'confidence_level': confidence_level}, None
    except Exception as e:
        return {'message': f'Error: {e}'}, None


if __name__ == '__main__':
    make_recommendation()
