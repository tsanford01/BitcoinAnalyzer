import tkinter as tk
from recommendation_app import RecommendationApp


def main():
    # Create the root window
    root = tk.Tk()

    # Create an instance of the RecommendationApp class
    app = RecommendationApp(root)

    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()
