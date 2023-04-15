# analysis_module.py

# Other necessary imports
import pandas as pd

from analysis.evaluate_recommendation import evaluate_recommendation
# Import necessary functions from the 'analysis' module
from analysis.evaluation_function import evaluate_performance, get_last_percentage_change
from analysis.make_recommendation import make_recommendation, get_price_trend, get_market_sentiment
from analysis.track_performance import track_performance


def analysis_pipeline():
    # Read historical data from CSV file
    historical_data = pd.read_csv('data/historical_data.csv')

    # Evaluate performance and calculate indicators
    indicators = evaluate_performance(historical_data)

    # Calculate the last percentage change in price
    last_percentage_change = get_last_percentage_change(historical_data)

    # Get price trend and market sentiment
    price_trend = get_price_trend(historical_data)
    market_sentiment = get_market_sentiment(historical_data)

    # Make a recommendation based on indicators
    recommendation = make_recommendation()

    # Get actual price changes
    actual_price_changes = get_actual_price_changes(historical_data)

    # Evaluate the recommendation
    evaluation = evaluate_recommendation(current_price)

    # Track the performance
    past_recommendations = []
    track_performance(evaluation, past_recommendations)


# Run the analysis pipeline
if __name__ == "__main__":
    analysis_pipeline()
