import subprocess
import os
from datetime import datetime

def run_scrapy_spider():
    """Run the Tesla Owners Online forum posts spider and capture its output."""
    # Get the current script directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate to project root (3 levels up from test_file folder)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    # Path to output directory
    
    output_dir = os.path.join(project_root, 'automation_exp_output')
    os.makedirs(output_dir, exist_ok=True)

    # Generate the output CSV filename with timestamp
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f'teslaownersonline_forum_threads_{current_time}.csv'
    output_path = os.path.join(output_dir, output_filename)

    # Set the log directory to the specified path
    log_dir = os.path.join(project_root, 'automation_exp_log')
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f'teslaownersonline_forum_posts_spider_{current_time}.log'
    log_path = os.path.join(log_dir, log_filename)

    command = [
        "scrapy", "crawl", "teslaownersonline_forum_posts_spider", "-o", f"{output_path}:csv",
        "-s", f"LOG_FILE={log_path}"
    ]
    try:
        # Run the command and capture output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)
        print(result.stderr)
        print(f"Log file created at: {os.path.abspath(log_path)}")
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(e.stderr)

if __name__ == "__main__":
    run_scrapy_spider()
