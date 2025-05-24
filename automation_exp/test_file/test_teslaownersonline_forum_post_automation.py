import subprocess
import os
from datetime import datetime

def run_scrapy_spider():
    """Run the Tesla Owners Online forum posts spider and capture its output."""
    # Create the output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), '../forum_threads')
    os.makedirs(output_dir, exist_ok=True)

    # Generate the output CSV filename with timestamp
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f'teslaownersonline_forum_threads_{current_time}.csv'
    output_path = os.path.join(output_dir, output_filename)

    # Generate the log file name with spider name and timestamp
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(project_root, 'logs')
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
