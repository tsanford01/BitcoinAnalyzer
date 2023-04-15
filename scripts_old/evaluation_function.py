import pandas as pd


def evaluate_performance():
    # Read in the performance data
    try:
        df = pd.read_csv('performance.csv')
    except pd.errors.EmptyDataError:
        return {'message': 'Performance data file is empty or missing.'}, None

    # Calculate the profit/loss percentage for each trade
    df['Profit/Loss %'] = df['Profit/Loss'] / df['Cost'] * 100

    # Calculate the total profit/loss and profit/loss percentage for all trades
    total_profit_loss = df['Profit/Loss'].sum()
    total_profit_loss_percent = total_profit_loss / df['Cost'].sum() * 100

    # Return the results
    with open('performance_evaluation.txt', 'w') as file:
        file.write(f'Total Profit/Loss: {total_profit_loss}\n'
                   f'Total Profit/Loss Percentage: {total_profit_loss_percent:.2f}%\n\n'
                   f'Individual Trades:\n'
                   f'{df.to_string(index=False)}')
    return {'message': 'Evaluation complete.'}, None


def get_last_percentage_change():
    # Get the percentage change since the last recommendation
    with open('recommendation_evaluations.txt', 'r') as file:
        lines = file.readlines()
    if len(lines) < 2:
        return 0.0
    last_line = lines[-2].strip()
    previous_percentage_change = float(last_line.split(' ')[1])
    return previous_percentage_change
