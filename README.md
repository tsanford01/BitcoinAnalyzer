# BitcoinAnalyzer
# Bitcoin Recommendation Tool

## Overview
The Bitcoin Recommendation Tool is a graphical user interface (GUI) application that provides real-time Bitcoin price analysis and recommendations for buying or selling Bitcoin based on historical data. The tool is implemented in Python using the Tkinter library and utilizes external data sources to obtain the latest Bitcoin price information.

## Features
- Real-time Bitcoin price updates displayed in the main window.
- Analysis of historical Bitcoin price data to generate recommendations for buying or selling.
- Ability to view past recommendations with timestamps in a separate window.
- Option to evaluate the performance of past recommendations.
- Countdown timer with a progress bar that indicates the time until the next recommendation is generated.
- Configurable update frequencies for both price updates and analysis loop.

## Installation
1. Clone the repository or download the source code.
2. Navigate to the project directory.
3. Ensure you have Python 3 and the required libraries (Tkinter, pandas, requests) installed.

## Usage
1. Run the `recommendation_app.py` script to start the application.
2. The main window will open, displaying the current Bitcoin price and analysis results.
3. Use the available buttons to start/stop analysis, view recommendation history, evaluate performance, and access settings.
4. The "Start Analysis" button starts the analysis loop, generating recommendations based on Bitcoin price data.
5. The "Stop Analysis" button stops the analysis loop.
6. The "Settings" button opens the settings window where you can configure update frequencies.

## Dependencies
- Tkinter (for creating the GUI)
- pandas (for data manipulation)
- requests (for making HTTP requests to fetch price data)

## Contributing
If you would like to contribute to the development of the Bitcoin Recommendation Tool, please feel free to submit pull requests or open issues with suggested enhancements.

## License
This project is open-source and available under the MIT License.

## Disclaimer
The Bitcoin Recommendation Tool is for educational purposes only and should not be used as financial advice. Cryptocurrency trading involves risk, and users should consult with a financial advisor before making any investment decisions.
