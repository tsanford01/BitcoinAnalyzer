import time
from make_recommendation import make_recommendation
import requests
from datetime import datetime
def track_performance():
    try:
        # set up the data file
        with open('performance.csv', 'a+') as file:
            file.write('Timestamp,Trade,Price,Amount,Cost,Average Cost,Profit/Loss
')
        # loop continuously
        while True:
            # wait 15 minutes
            time.sleep(15 * 60)
            # get the current price of Bitcoin
            current_price = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd').json()['bitcoin']['usd']
            # evaluate the performance of the last trade
            with open('performance.csv', 'r') as file:
                line = file.readlines()[-1].strip()
                last_trade = line.split(',')
            last_price = float(last_trade[2])
            last_amount = float(last_trade[3])
            last_cost = float(last_trade[4])
            last_profit_loss = float(last_trade[-1])
            # get the percentage change since the last recommendation
            with open('recommendation_evaluations.txt', 'r') as file:
                lines = file.readlines()
                if len(lines) < 2:
                    continue
                last_line = lines[-2].strip()
                previous_percentage_change = float(last_line.split(' ')[1])
            percentage_change = (current_price - previous_percentage_change) / previous_percentage_change * 100
            # make a trade if the percentage change is outside the threshold
            if percentage_change > 5:
                amount = 0.1  # arbitrary amount for testing purposes
                cost = amount * current_price
                profit_loss = (last_amount * current_price - last_cost) + (amount * last_price - cost)
                with open('performance.csv', 'a') as file:
                    file.write(f'{datetime.now()},sell,{current_price},{amount},{cost},{(last_cost + cost) / (last_amount + amount)},{profit_loss}
')
            elif percentage_change < -5:
                amount = 0.1  # arbitrary amount for testing purposes
                cost = amount * current_price
                profit_loss = (last_amount * current_price - last_cost) + (amount * last_price - cost)
                with open('performance.csv', 'a') as file:
                    file.write(f'{datetime.now()},buy,{current_price},{amount},{cost},{(last_cost + cost) / (last_amount + amount)},{profit_loss}
')
            else:
                continue
    except KeyboardInterrupt:
        return ({'message': 'Loop interrupted by user.'}, None)
    except Exception as e:
        return ({'message': f'Error: {e}'}, None)

if __name__ == '__main__':
    track_performance()
