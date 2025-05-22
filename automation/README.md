# Jira Zephyr Test Summary Automation

This script automates the extraction of test cycle summaries from Jira with the Zephyr extension. It logs into Jira, navigates to the specified version's test cycles, extracts test results data, and generates a summary report showing pass/fail/blocked counts by component.

## Features

- Automatically logs into Jira
- Navigates to Zephyr test cycles for a specified version
- Extracts test data including component information and test status
- Generates a summary report showing:
  - Number of tests passed, failed, or blocked per component
  - Percentage of tests in each status per component
- Outputs results to a CSV file (easily viewable in Excel)

## Requirements

- Python 3.6+
- Chrome browser installed
- Internet connection to access your Jira instance

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure you have Chrome installed on your system

## Usage

Run the script with the following command:

```bash
python jira_zephyr_test_summary.py --url "https://your-jira-instance.com" --username "your_username" --password "your_password" --version "Version Name"
```

### Command Line Arguments

- `--url`: Your Jira instance URL (required)
- `--username`: Your Jira username (required)
- `--password`: Your Jira password (required)
- `--version`: The version to extract test data for (required)
- `--output`: Custom output file path (optional, default: auto-generated filename with timestamp)
- `--headless`: Run Chrome in headless mode (optional, add this flag to run without UI)

### Example

```bash
python jira_zephyr_test_summary.py --url "https://jira.company.com" --username "john.doe" --password "mypassword" --version "2.3.0" --output "sprint_report.csv"
```

## Output

The script generates a CSV file with a summary of test results by component, including:

- Counts of tests in each status (Pass, Fail, Blocked, etc.) per component
- Percentage of tests in each status per component
- Total number of tests per component

## Scheduling

To run this script 2-3 times per week, you can use:

### Windows Task Scheduler

1. Open Task Scheduler
2. Create a new Basic Task
3. Set the trigger to run on your desired schedule (e.g., Monday, Wednesday, Friday at 9 AM)
4. Set the action to "Start a program"
5. Browse to your Python executable and add the script with its arguments as parameters

### Linux/Mac Cron Job

Add a cron job by editing your crontab:

```bash
crontab -e
```

Add a line like this to run the script on Monday, Wednesday, and Friday at 9 AM:

```
0 9 * * 1,3,5 /usr/bin/python3 /path/to/jira_zephyr_test_summary.py --url "https://your-jira-instance.com" --username "your_username" --password "your_password" --version "Version Name"
```

## Notes

- The script may need adjustments based on your specific Jira and Zephyr configuration
- XPath selectors in the script might need to be updated if your Jira/Zephyr UI differs
- For security, consider storing credentials in environment variables rather than passing them directly in the command line

