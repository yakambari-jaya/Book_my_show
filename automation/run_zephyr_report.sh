#!/bin/bash
# Script to run the Jira Zephyr Test Summary automation

# Default values
HEADLESS=""
OUTPUT=""

# Display help message
function show_help {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -u, --url URL          Jira instance URL (required)"
    echo "  -n, --username USER    Jira username (required)"
    echo "  -p, --password PASS    Jira password (required)"
    echo "  -v, --version VER      Version to extract data for (required)"
    echo "  -o, --output FILE      Output CSV file path (optional)"
    echo "  -h, --headless         Run in headless mode (optional)"
    echo "  --help                 Show this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -u|--url)
            URL="$2"
            shift 2
            ;;
        -n|--username)
            USERNAME="$2"
            shift 2
            ;;
        -p|--password)
            PASSWORD="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="--output $2"
            shift 2
            ;;
        -h|--headless)
            HEADLESS="--headless"
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Check required parameters
if [ -z "$URL" ] || [ -z "$USERNAME" ] || [ -z "$PASSWORD" ] || [ -z "$VERSION" ]; then
    echo "Error: Missing required parameters"
    show_help
fi

# Run the Python script
echo "Running Jira Zephyr Test Summary automation..."
python jira_zephyr_test_summary.py --url "$URL" --username "$USERNAME" --password "$PASSWORD" --version "$VERSION" $OUTPUT $HEADLESS

# Check if the script executed successfully
if [ $? -eq 0 ]; then
    echo "Automation completed successfully!"
else
    echo "Automation failed. Check the error messages above."
fi

