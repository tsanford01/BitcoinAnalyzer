import requests
import datetime
from evaluate_recommendation import evaluate_recommendation

def make_recommendation():
    try:
        # evaluate the most recent recommendation
        result, error = evaluate_recommendation()
        if error is not None:
            return (None, error)
        # get the current price of Bitcoin
        current_price = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd').json()['bitcoin']['usd']
        # get the percentage change since the last recommendation
        with open('data/recommendation_evaluations.txt', 'r') as file:
            lines = file.readlines()
            if len(lines) < 2:
                return ({'message': 'Not enough data to make a recommendation.'}, None)
            last_line = lines[-2].strip()
            previous_percentage_change = float(last_line.split(' ')[1])
        percentage_change = (current_price - previous_percentage_change) / previous_percentage_change * 100
        # make a recommendation based on the percentage change
        if percentage_change > 5:
            return ({'message': f'Bitcoin price has increased by {percentage_change:.2f} percent since the last recommendation. It is recommended to sell.'}, None)
        elif percentage_change < -5:
            return ({'message': f'Bitcoin price has decreased by {abs(percentage_change):.2f} percent since the last recommendation. It is recommended to buy.'}, None)
        else:
            return ({'message': 'No significant change in Bitcoin price since the last recommendation.'}, None)
    except Exception as e:
        return ({'message': f'Error: {e}'}, None)

if __name__ == '__main__':
    make_recommendation()
