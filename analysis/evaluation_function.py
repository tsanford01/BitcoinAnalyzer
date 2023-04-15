import pandas as pd
import os


def evaluate_performance(historical_data):
    # Define the path to the performance data file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, '..', 'data', 'performance.csv')

    # Initialize an empty DataFrame
    df = pd.DataFrame()

    # Check if the file exists and is not empty
    if os.path.isfile(data_path) and os.path.getsize(data_path) > 0:
        # Read in the performance data
        try:
            df = pd.read_csv(data_path)
        except FileNotFoundError:
            # Handle the case when the file is not found
            print("File 'performance.csv' not found. Creating an empty DataFrame.")

    # Check if 'Profit/Loss' and 'Cost' columns exist in the DataFrame
    if 'Profit/Loss' in df.columns and 'Cost' in df.columns:
        # Calculate the profit/loss percentage for each trade
        df['Profit/Loss %'] = df['Profit/Loss'] / df['Cost'] * 100

        # Calculate the total profit/loss and profit/loss percentage for all trades
        total_profit_loss = df['Profit/Loss'].sum()
        total_profit_loss_percent = total_profit_loss / df['Cost'].sum() * 100

        # Write the results to a file
        with open('performance_evaluation.txt', 'w') as file:
            file.write(f'Total Profit/Loss: {total_profit_loss}\n'
                       f'Total Profit/Loss Percentage: {total_profit_loss_percent:.2f}%\n\n'
                       f'Individual Trades:\n'
                       f'{df.to_string(index=False)}')
        return {'message': 'Evaluation complete.'}, None
    else:
        # Columns not found in the DataFrame, return a message
        return {'message': 'Columns "Profit/Loss" and/or "Cost" not found in the data.'}, None


def get_last_percentage_change():
    # Get the percentage change since the last recommendation
    with open('recommendation_evaluations.txt', 'r') as file:
        lines = file.readlines()
    if len(lines) < 2:
        return 0.0
    last_line = lines[-2].strip()
    previous_percentage_change = float(last_line.split(' ')[1])
    return previous_percentage_change
