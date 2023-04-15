# recommendation_app.py
import csv
import tkinter as tk
from datetime import datetime
from threading import Thread
from tkinter import ttk
import requests
import time
import analysis_module as analysis_module  # You may need to update this import
from utils.data_retrieval import get_historical_data

current_datetime = datetime.now()


def get_current_bitcoin_price():
    while True:
        try:
            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
            if response.status_code == 429:
                # Rate limited, wait before making another request
                time.sleep(60)
                continue
            data = response.json()
            # print(data)  # Inspect the JSON structure
            current_price = data['bitcoin']['usd']
            return current_price
        except KeyError as e:
            print(f"KeyError: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None


current_price = get_current_bitcoin_price()
# print(current_price)


class RecommendationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Recommendation Tool")
        self.root.geometry("1200x600")
        self.is_running = False

        # Initialize default update frequencies (in seconds)
        self.update_price_frequency = 10
        self.analysis_loop_frequency = 60

        # Create a StringVar instance to hold the current Bitcoin price text
        self.current_price_text = tk.StringVar()

        # Main frame to hold all elements
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header frame and label
        self.header_frame = tk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        self.header = tk.Label(self.header_frame, text="Bitcoin Recommendation Tool", font=("Helvetica", 16))
        self.header.pack()

        # Current price frame and label
        self.current_price_frame = tk.Frame(self.main_frame)
        self.current_price_frame.pack(fill=tk.X)
        self.current_price_label = tk.Label(self.current_price_frame, textvariable=self.current_price_text,
                                            font=("Helvetica", 12))
        self.current_price_label.pack()

        # Create a progress bar to visualize the countdown
        self.progress_bar = ttk.Progressbar(self.main_frame, mode='determinate', length=300,
                                            maximum=self.analysis_loop_frequency)
        self.progress_bar.pack(pady=(10, 5))

        # Label to display remaining time
        self.remaining_time_label = tk.Label(self.main_frame, font=("Helvetica", 12))
        self.remaining_time_label.pack(pady=(5, 15))

        # Buttons frame
        self.buttons_frame = tk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.X, pady=(0, 20))

        # Start analysis button
        self.start_button = tk.Button(self.buttons_frame, text="Start Analysis", command=self.start_analysis)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Stop analysis button
        self.stop_button = tk.Button(self.buttons_frame, text="Stop Analysis", command=self.stop_analysis)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to view history
        self.history_button = tk.Button(self.buttons_frame, text="View History", command=self.view_history)
        self.history_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to evaluate performance
        self.evaluate_button = tk.Button(self.buttons_frame, text="Evaluate Performance",
                                         command=self.evaluate_performance_wrapper)
        self.evaluate_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Settings button
        self.settings_button = tk.Button(self.buttons_frame, text="Settings", command=self.open_settings_window)
        self.settings_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Label to display sentiment indicator
        self.sentiment_indicator = tk.Label(self.main_frame, font=("Helvetica", 14))
        self.sentiment_indicator.pack(pady=(10, 5))

        # Label to display recommendation
        self.recommendation_text = tk.StringVar()
        self.recommendation_label = tk.Label(self.main_frame, textvariable=self.recommendation_text,
                                             font=("Helvetica", 14))
        self.recommendation_label.pack(pady=(5, 5))

        # Status frame and label
        self.status_frame = tk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=(20, 0))
        self.status_text = tk.StringVar()
        self.status_label = tk.Label(self.status_frame, textvariable=self.status_text, font=("Helvetica", 12))
        self.status_label.pack()

        # Create a frame to display the history at the bottom of the main window
        self.history_frame = tk.Frame(self.main_frame)
        self.history_frame.pack(fill=tk.BOTH, pady=10, expand=True)

        # Show History Scrollbar creation
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=1)

        # Create a scrollbar and associate it with the canvas
        self.scrollbar = tk.Scrollbar(self.canvas, orient='vertical', command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self.on_configure)

        # Create the history frame inside the canvas
        self.history_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.history_frame, anchor='nw')

        # Initialize past_recommendations as an empty list
        self.past_recommendations = []

        # Update the current Bitcoin price and display it
        self.update_current_price()

        # Initialize remaining time to 1 minutes (60 seconds)
        self.remaining_time = 60

        # Start the countdown update
        self.update_countdown()

        self.price_schedule = None  # Initialize the price schedule attribute

    def update_price_schedule(self, new_schedule):
        # Update the price schedule with the new schedule provided
        self.price_schedule = new_schedule
        # Perform any additional actions needed to update the schedule

    # Wrapper function to call evaluate_performance and handle results
    def update_current_price(self):
        # Retrieve the current Bitcoin price using the new function
        current_price = get_current_bitcoin_price()
        if current_price is not None:
            # Update the current price label
            self.current_price_text.set(f"Current Bitcoin Price: ${current_price}")
        else:
            self.current_price_text.set("Error retrieving current price.")

        # Schedule the next update in 10 seconds (10000 milliseconds)
        self.root.after(self.update_price_frequency * 1000, self.update_current_price)

    def start_analysis(self):
        # Set the running flag to True
        self.is_running = True
        self.status_text.set("Analysis started.")
        # Start the analysis loop in a separate thread
        analysis_thread = Thread(target=self.analysis_loop)
        analysis_thread.start()
        # Schedule the update_current_price and analysis_loop with the user-defined frequency
        self.update_price_schedule = self.root.after(self.update_price_frequency * 1000, self.update_current_price)
        self.analysis_loop_schedule = self.root.after(self.analysis_loop_frequency * 1000, self.analysis_loop)

    def stop_analysis(self):
        # Set the running flag to False to stop the analysis loop
        self.is_running = False
        self.status_text.set("Analysis stopped.")

    def view_history(self):
        # Clear the history frame before displaying the history
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        # Display the past recommendations in the history frame
        for recommendation in self.past_recommendations:
            recommendation_label = tk.Label(self.history_frame, text=f"{recommendation[0]} - {recommendation[1]}")
            recommendation_label.pack()

        # Scroll to the bottom of the history frame to show the latest recommendations
        self.canvas.update()
        self.canvas.yview_moveto(1)

    def on_configure(self, event):
        # Update the scroll region to match the size of the history frame
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

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

    def get_current_bitcoin_price():
        while True:
            try:
                response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
                if response.status_code == 429:
                    # Rate limited, wait before making another request
                    time.sleep(60)
                    continue
                data = response.json()
                # print(data)  # Inspect the JSON structure
                current_price = data['bitcoin']['usd']
                return current_price
            except KeyError as e:
                print(f"KeyError: {e}")
                return None
            except Exception as e:
                print(f"Error: {e}")
                return None

    current_price = get_current_bitcoin_price()
    # print(current_price)

    def analysis_loop(self):
        while self.is_running:
            # Retrieve the current Bitcoin price
            current_price = get_current_bitcoin_price()  # Replace this with your function
            if current_price is None:
                # Handle error in retrieving current price
                continue

            # Retrieve historical data
            historical_data = get_historical_data()

            # Use evaluation_function to evaluate historical data and calculate indicators
            indicators = analysis_module.evaluate_performance(historical_data)

            # Call the make_recommendation function and get the recommendation and error (if any)
            recommendation, error = analysis_module.make_recommendation(current_price)

            # Retrieve the confidence level from the recommendation
            confidence_level = recommendation.get('confidence_level')

            # Check if there is an error
            if error is not None:
                # Print the error message to the console
                print("Error:", error)
                # Display the error message in the UI
                self.status_text.set(error)
                return

            # Ensure the recommendation is not None and contains the 'message' key
            if recommendation is not None and 'message' in recommendation:
                # Use the message from the recommendation
                self.recommendation_text.set(recommendation['message'])
            else:
                # Handle the case when the recommendation is None or invalid
                self.recommendation_text.set("No recommendation available.")

            evaluation = analysis_module.evaluate_recommendation(current_price)

            # Use track_performance to track the performance of the recommendations
            analysis_module.track_performance(evaluation, self.past_recommendations, current_price)

            # Update the recommendation text and store the recommendation with a timestamp
            self.recommendation_text.set(recommendation['message'])  # Use the message from the recommendation
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.past_recommendations.append((timestamp, recommendation['message']))  # Store the message

            # Update the sentiment indicator based on the recommendation
            sentiment = recommendation.get('sentiment')
            self.update_sentiment_indicator(sentiment)

            # Schedule the next update based on the user-defined frequency
            self.analysis_loop_schedule = self.root.after(self.analysis_loop_frequency * 100, self.analysis_loop)

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

    def start_analysis(self):
        # Set the running flag to True
        self.is_running = True
        self.status_text.set("Analysis started.")
        # Start the analysis loop in a separate thread
        analysis_thread = Thread(target=self.analysis_loop)
        analysis_thread.start()
        # Start the update_current_price with the user-defined frequency
        self.update_price_schedule = self.root.after(self.update_price_frequency * 100, self.update_current_price)

    def stop_analysis(self):
        # Set the running flag to False to stop the analysis loop
        self.is_running = False
        self.status_text.set("Analysis stopped.")
        # Cancel the scheduled updates when stopping the analysis
        self.root.after_cancel(self.update_price_schedule)
        self.root.after_cancel(self.analysis_loop_schedule)

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
    # app.update_countdown()
    app.update_price_schedule(new_schedule="Hourly")

    # Define the on_close behavior
    root.protocol("WM_DELETE_WINDOW", app.on_close)

    root.mainloop()
