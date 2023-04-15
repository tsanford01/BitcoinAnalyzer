import tkinter as tk
from tkinter import ttk
from threading import Thread
from datetime import datetime, timedelta
import time
import os
import pandas as pd
import analysis_module as analysis_module  # You may need to update this import
from utils.data_retrieval import get_current_bitcoin_price, get_historical_data
import csv

current_datetime = datetime.now()


class RecommendationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Recommendation Tool")
        self.root.geometry("600x500")
        self.is_running = False

        # Initialize default update frequencies (in seconds)
        self.update_price_frequency = 10
        self.analysis_loop_frequency = 60

        # Start the update_current_price and analysis_loop with default frequencies
        self.update_price_schedule = self.root.after(self.update_price_frequency * 1000, self.update_current_price)
        self.analysis_loop_schedule = self.root.after(self.analysis_loop_frequency * 1000, self.analysis_loop)

        # Create a StringVar instance to hold the current Bitcoin price text
        self.current_price_text = tk.StringVar()

        self.header = tk.Label(self.root, text="Bitcoin Recommendation Tool", font=("Helvetica", 16))
        self.header.pack(pady=10)

        # Create a Label widget to display the current Bitcoin price
        self.current_price_label = tk.Label(self.root, textvariable=self.current_price_text, font=("Helvetica", 12))
        self.current_price_label.pack(pady=10)

        # List to store past recommendations
        self.past_recommendations = []

        # start analysis button
        self.start_button = tk.Button(self.root, text="Start Analysis", command=self.start_analysis)
        self.start_button.pack(pady=10)

        # Stop Analysis Button
        self.stop_button = tk.Button(self.root, text="Stop Analysis", command=self.stop_analysis)
        self.stop_button.pack(pady=10)

        # Button to view history
        self.history_button = tk.Button(self.root, text="View History", command=self.view_history)
        self.history_button.pack(pady=10)

        # Load past recommendations from file
        self.load_recommendations()

        # Button to evaluate performance
        self.evaluate_button = tk.Button(self.root, text="Evaluate Performance",
                                         command=self.evaluate_performance_wrapper)  # Update here
        self.evaluate_button.pack(pady=10)

        # settings button
        self.settings_button = tk.Button(self.root, text="Settings", command=self.open_settings_window)
        self.settings_button.pack(pady=10)

        # Update the current Bitcoin price and display it
        self.update_current_price()

        # Label to display sentiment indicator
        self.sentiment_indicator = tk.Label(self.root, font=("Helvetica", 14))
        self.sentiment_indicator.pack(pady=10)

        # Initialize remaining time to 1 minutes (60 seconds)
        self.remaining_time = 60

        # Create a progress bar to visualize the countdown
        self.progress_bar = ttk.Progressbar(self.root, mode='determinate', length=300, maximum=self.remaining_time)
        self.progress_bar.pack(pady=10)

        # Label to display remaining time
        self.remaining_time_label = tk.Label(self.root, font=("Helvetica", 12))
        self.remaining_time_label.pack(pady=10)

        self.recommendation_text = tk.StringVar()
        self.recommendation_label = tk.Label(self.root, textvariable=self.recommendation_text, font=("Helvetica", 14))
        self.recommendation_label.pack(pady=10)

        self.status_text = tk.StringVar()
        self.status_label = tk.Label(self.root, textvariable=self.status_text, font=("Helvetica", 12))
        self.status_label.pack(pady=10)

    # Wrapper function to call evaluate_performance and handle results
    def update_current_price(self):
        current_price = get_current_bitcoin_price()
        if current_price is not None:
            # If current_price is not None, set the text
            self.current_price_text.set(f"Current Bitcoin Price: ${current_price:.2f}")
        else:
            # If current_price is None, display an error message
            self.current_price_text.set("Error: Failed to retrieve current Bitcoin price.")

        # Schedule the next update in 10 seconds (10000 milliseconds)
        self.root.after(self.update_price_frequency * 1000, self.update_current_price)

    def start_analysis(self):
        # Set the running flag to True
        self.is_running = True
        self.status_text.set("Analysis started.")
        # Start the analysis loop in a separate thread
        analysis_thread = Thread(target=self.analysis_loop)
        analysis_thread.start()

    def stop_analysis(self):
        # Set the running flag to False to stop the analysis loop
        self.is_running = False
        self.status_text.set("Analysis stopped.")

    def view_history(self):
        # Create a new window for history
        history_window = tk.Toplevel(self.root)
        history_window.title("Recommendation History")

        # Label for the history window
        history_label = tk.Label(history_window, text="Recommendation History", font=("Helvetica", 14))
        history_label.pack(pady=10)

        # Display the past recommendations
        for recommendation in self.past_recommendations:
            recommendation_label = tk.Label(history_window, text=f"{recommendation[0]} - {recommendation[1]}")
            recommendation_label.pack()

    def update_sentiment_indicator(self, sentiment):
        if sentiment == 'bullish':
            self.sentiment_indicator.config(text='Bullish Sentiment 📈', fg='green')
        elif sentiment == 'bearish':
            self.sentiment_indicator.config(text='Bearish Sentiment 📉', fg='red')
        else:
            self.sentiment_indicator.config(text='Neutral Sentiment 🟡', fg='orange')

    def update_countdown(self):
        # Update remaining time
        self.remaining_time -= 1

        # Update progress bar value based on remaining time
        self.progress_bar['value'] = 60 - self.remaining_time

        # Calculate minutes and seconds
        minutes, seconds = divmod(self.remaining_time, 60)

        # Update remaining time label
        self.remaining_time_label.config(text=f"Time until next notification: {minutes} min {seconds} sec")

        # Check if time is up
        if self.remaining_time == 0:
            # Reset remaining time to 1 minutes (60 seconds)
            self.remaining_time = 600

            # Perform analysis and notification
            self.analysis_loop()

        # Schedule the next update in 1 second (1000 milliseconds)
        self.root.after(1000, self.update_countdown)

    def analysis_loop(self):
        while self.is_running:
            # Retrieve historical data
            historical_data = get_historical_data()

            # Use evaluation_function to evaluate historical data and calculate indicators
            indicators = analysis_module.evaluate_performance(historical_data)

            # Use make_recommendation to generate a recommendation based on indicators
            recommendation = analysis_module.make_recommendation(indicators)

            # Evaluate the recommendation using the entire recommendation dictionary
            evaluation = analysis_module.evaluate_recommendation(recommendation, historical_data)

            # Use track_performance to track the performance of the recommendations
            analysis_module.track_performance(evaluation, self.past_recommendations)

            # Update the recommendation text and store the recommendation with a timestamp
            self.recommendation_text.set(recommendation['message'])  # Use the message from the recommendation
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.past_recommendations.append((timestamp, recommendation['message']))  # Store the message

            # Update the sentiment indicator based on the recommendation
            sentiment = recommendation.get('sentiment')
            self.update_sentiment_indicator(sentiment)

            # Schedule the next update based on the user-defined frequency
            self.analysis_loop_schedule = self.root.after(self.analysis_loop_frequency * 1000, self.analysis_loop)

    # Wrapper function to call evaluate_performance and handle results
    def evaluate_performance_wrapper(self):
        historical_data = get_historical_data()
        if historical_data is not None:
            analysis_module.evaluate_performance(historical_data)
        else:
            print("Failed to retrieve historical data.")

    def load_recommendations(self):
        # Define the file path for the recommendations.csv file
        file_path = 'data/recommendations.csv'
        try:
            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    self.past_recommendations.append((row[0], row[1]))
        except FileNotFoundError:
            pass

    def save_recommendations(self):
        # Define the file path for the recommendations.csv file
        file_path = 'data/recommendations.csv'
        with open(file_path, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            for recommendation in self.past_recommendations:
                csv_writer.writerow(recommendation)

    def on_close(self):
        # Save recommendations to file
        self.save_recommendations()
        # Close the application
        self.root.destroy()

    def open_settings_window(self):
        # Create a new window for settings
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")

        # Label for updating Bitcoin price frequency
        update_price_label = tk.Label(settings_window, text="Update Bitcoin Price (seconds):", font=("Helvetica", 12))
        update_price_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        # Entry for updating Bitcoin price frequency
        self.update_price_entry = tk.Entry(settings_window)
        self.update_price_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # Label for analysis loop frequency
        analysis_loop_label = tk.Label(settings_window, text="Analysis Loop (seconds):", font=("Helvetica", 12))
        analysis_loop_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        # Entry for analysis loop frequency
        self.analysis_loop_entry = tk.Entry(settings_window)
        self.analysis_loop_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        # Button to save settings
        save_button = tk.Button(settings_window, text="Save", command=self.save_settings)
        save_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W + tk.E)

    def stop_analysis(self):
        # ...
        # Cancel the scheduled updates when stopping the analysis
        self.root.after_cancel(self.update_price_schedule)
        self.root.after_cancel(self.analysis_loop_schedule)

    def start_analysis(self):
        # ...
        # Start the update_current_price and analysis_loop with the user-defined frequency
        self.update_price_schedule = self.root.after(self.update_price_frequency * 1000, self.update_current_price)
        self.analysis_loop_schedule = self.root.after(self.analysis_loop_frequency * 1000, self.analysis_loop)

    def save_settings(self):
        try:
            # Retrieve values from entries
            update_price_frequency = int(self.update_price_entry.get())
            analysis_loop_frequency = int(self.analysis_loop_entry.get())

            # Update frequencies in the main window
            self.update_price_frequency = update_price_frequency
            self.analysis_loop_frequency = analysis_loop_frequency

            # Restart update_current_price and analysis_loop with the new frequency
            self.root.after_cancel(self.update_price_schedule)
            self.root.after_cancel(self.analysis_loop_schedule)
            self.update_current_price()
            self.analysis_loop()

        except ValueError:
            # Handle invalid input
            print("Invalid input for frequencies. Please enter valid integers.")
        except Exception as e:
            # Handle other exceptions
            print(f"Error saving settings: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RecommendationApp(root)

    # Start the countdown update
    app.update_countdown()

    root.mainloop()

    # Define the on_close behavior
    root.protocol("WM_DELETE_WINDOW", app.on_close)

    root.mainloop()
