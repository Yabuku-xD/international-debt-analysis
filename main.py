import os
import argparse

def create_directories():
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)
    os.makedirs("results/tables", exist_ok=True)

def parse_arguments():
    parser = argparse.ArgumentParser(description='India External Debt Analysis')
    
    parser.add_argument('--steps', nargs='+', default=['all'],
                        choices=['all', 'preprocessing', 'analysis', 'visualization'],
                        help='Steps to run in the pipeline')
    
    return parser.parse_args()

def run_pipeline(steps):
    print("Starting India External Debt Analysis Pipeline")
    
    if 'all' in steps or 'preprocessing' in steps:
        print("Step 1: Data Preprocessing")
        import scripts.data_preprocessing
        scripts.data_preprocessing.main()
    
    if 'all' in steps or 'analysis' in steps:
        print("Step 2: Data Analysis")
        import scripts.data_analysis
        scripts.data_analysis.main()
    
    if 'all' in steps or 'visualization' in steps:
        print("Step 3: Data Visualization")
        import scripts.visualization
        scripts.visualization.main()
    
    print("Pipeline completed successfully")

def main():
    create_directories()
    args = parse_arguments()
    run_pipeline(args.steps)

if __name__ == "__main__":
    main()