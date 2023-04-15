import requests
import datetime
from analysis.evaluate_recommendation import evaluate_recommendation


def get_price_trend(days):
    # Get the price data from the last `days` days
    bitcoin_price = requests.get(
        f'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}').json()
    # Calculate the average price over the last `days` days
    average_price = sum([price[1] for price in bitcoin_price['prices']]) / len(bitcoin_price['prices'])
    # Calculate the current price of Bitcoin
    current_price = \
        requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd').json()['bitcoin'][
            'usd']
    # Calculate the percentage difference between the average price and the current price
    percentage_difference = (current_price - average_price) / average_price * 100
    return percentage_difference


def get_market_sentiment():
    # get the sentiment of the market
    response = requests.get('https://api.coingecko.com/api/v3/coins/bitcoin/sentiment')
    if response.status_code == requests.codes.ok:
        sentiment = response.json()['sentiment_votes_up_percentage']
    return sentiment


def make_recommendation():
    try:
        # evaluate the most recent recommendation
        result, error = evaluate_recommendation()
        if error is not None:
            return None, error
        # get the current price of Bitcoin
        current_price = \
            requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd').json()[
                'bitcoin'][
                'usd']
        # get the percentage change since the last recommendation
        with open('recommendation_evaluations.txt', 'r') as file:
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
        # use the information to make a recommendation
        if percentage_change > 5 and long_term_trend > 2 and sentiment > 60:
            return ({
                        'message': f'Bitcoin price has increased by {percentage_change:.2f}% since the last recommendation, long-term trend is {long_term_trend:.2f}% positive, and market sentiment is {sentiment:.2f}% positive. It is recommended to sell.'},
                    None)
        elif percentage_change < -5 and long_term_trend < -2 and sentiment < 40:
            return ({
                        'message': f'Bitcoin price has decreased by {abs(percentage_change):.2f}% since the last '
                                   f'recommendation, long-term trend is {long_term_trend:.2f}% negative, and market '
                                   f'sentiment is {sentiment:.2f}% negative. It is recommended to buy.'},
                    None)
        else:
            return {'message': 'No significant change in Bitcoin price since the last recommendation.'}, None
    except Exception as e:
        return {'message': f'Error: {e}'}, None


if __name__ == '__main__':
    make_recommendation()
