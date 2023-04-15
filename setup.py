
import subprocess
import sys

def install_dependencies():
    try:
        # Define the command to install dependencies from requirements.txt
        install_command = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]

        # Execute the command using the subprocess module
        subprocess.check_call(install_command)

        print("Dependencies installed successfully.")

    except subprocess.CalledProcessError as e:
        print("Error occurred while installing dependencies.")
        print(e)

if __name__ == "__main__":
    install_dependencies()
