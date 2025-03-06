import os
import subprocess
import sys

def main():
    """Run the Streamlit application."""
    try:
        # Check if Streamlit is installed
        subprocess.run([sys.executable, "-m", "pip", "show", "streamlit"], 
                      check=True, capture_output=True)
        
        # Run the Streamlit application
        print("Starting Profile Picture Generator...")
        subprocess.run(["streamlit", "run", "app.py"], check=True)
        
    except subprocess.CalledProcessError:
        print("Streamlit is not installed. Installing required packages...")
        
        # Install required packages
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        
        # Run the Streamlit application
        print("Starting Profile Picture Generator...")
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 