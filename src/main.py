import sys
import os

# Ensure the root of the project is in the PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src import get_data

def main():
    """
        - Main wrapper function to execute the pipeline
    """

    print("Executing main pipeline...")
    # phase 1: extracting data into raw data folder
    get_data.main()
    
    print("Pipeline execution finished.")

if __name__ == "__main__":
    main()
