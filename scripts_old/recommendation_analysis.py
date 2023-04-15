def evaluate_recommendation(current_price):
    try:
        # get the most recent recommendation from our file
        with open('recommendations.txt', 'r') as file:
            lines = file.readlines()
            last_line = lines[-1].strip()
        # extract the date and the recommendation from the line
        date_str, recommendation_str = last_line.split('Bitcoin price has', 1)
        recommendation_str = 'Bitcoin price has' + recommendation_str
        date = datetime.datetime.strptime(date_str.strip(), '%Y-%m-%d %H:%M:%S.%f')
        # get the current Bitcoin price
        current_price = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd').json()['bitcoin']['usd']
        # get the Bitcoin price at the time of the recommendation
        one_hour_ago = (date - datetime.timedelta(hours=1)).strftime('%s')
        historical_data = requests.get(f'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range'
                                       f'?vs_currency=usd&from={one_hour_ago}&to=9999999999').json()
        opening_price = historical_data['prices'][0][1]
        # calculate the percentage change
        percentage_change = (current_price - opening_price) / opening_price * 100
        # save the result to a file
        with open('data/recommendation_evaluations.txt', 'a') as file:
            file.write(f'{date} {percentage_change:.2f} {recommendation_str}')
        return {"message": f'The percentage change since the last recommendation was {percentage_change:.2f} percent.'}, None
    except Exception as e:
        return {"message": "Error: {}"}.format(str(e)), None
