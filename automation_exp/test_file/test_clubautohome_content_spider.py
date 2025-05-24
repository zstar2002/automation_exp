import subprocess
import os
from datetime import datetime

def run_scrapy_spider():
    """Run the Scrapy content spider and capture its output."""
    # Set the output and log directories using relative paths from the test file
    test_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(test_file_dir))
    output_dir = os.path.join(project_root, 'automation_exp_output')
    log_dir = os.path.join(project_root, 'automation_exp_log')
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    # Generate the output CSV filename with timestamp
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f'clubautohome_post_content_{current_time}.csv'
    output_path = os.path.join(output_dir, output_filename)

    # Generate the log file name with spider name and timestamp
    log_filename = f'clubautohome_content_spider_{current_time}.log'
    log_path = os.path.join(log_dir, log_filename)

    command = [
        "scrapy", "crawl", "clubautohome_content_spider", "-o", f"{output_path}:csv",
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
