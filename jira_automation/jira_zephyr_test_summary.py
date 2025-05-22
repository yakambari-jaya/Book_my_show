#!/usr/bin/env python3
"""
Jira Zephyr Test Summary Automation Script

This script automates the extraction of test cycle summaries from Jira with Zephyr extension.
It logs into Jira, navigates to the specified version's test cycles, extracts test results data,
and generates a summary report showing pass/fail/blocked counts by component.

Requirements:
- Python 3.6+
- Selenium
- Chrome WebDriver
- pandas (for data processing)

Usage:
python jira_zephyr_test_summary.py --version "Version Name" --username "your_username" --password "your_password" --url "https://your-jira-instance.com"
"""

import argparse
import csv
import os
import time
from collections import defaultdict
from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class JiraZephyrAutomation:
    def __init__(self, url, username, password, version, headless=False):
        """
        Initialize the Jira Zephyr automation.
        
        Args:
            url (str): Jira instance URL
            username (str): Jira username
            password (str): Jira password
            version (str): Version to extract test data for
            headless (bool): Run Chrome in headless mode if True
        """
        self.url = url
        self.username = username
        self.password = password
        self.version = version
        
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)
        
        # Data storage
        self.test_data = []
        
    def login(self):
        """Log into Jira instance."""
        print(f"Logging into {self.url}...")
        self.driver.get(self.url)
        
        # Wait for login form and enter credentials
        username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_field.send_keys(self.username)
        
        # Some Jira instances have a two-step login process
        try:
            # Click the "Continue" or "Next" button if it exists
            continue_button = self.wait.until(EC.element_to_be_clickable((By.ID, "login-submit")))
            continue_button.click()
            
            # Now enter password
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_field.send_keys(self.password)
            login_button = self.wait.until(EC.element_to_be_clickable((By.ID, "login-submit")))
            login_button.click()
        except:
            # If no continue button, enter password directly
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_field.send_keys(self.password)
            login_button = self.wait.until(EC.element_to_be_clickable((By.ID, "login-submit")))
            login_button.click()
        
        # Wait for login to complete
        self.wait.until(EC.presence_of_element_located((By.ID, "jira")))
        print("Login successful!")
        
    def navigate_to_zephyr_cycles(self):
        """Navigate to Zephyr test cycles for the specified version."""
        print(f"Navigating to Zephyr test cycles for version: {self.version}...")
        
        # Navigate to Zephyr Test Cycles page
        # Note: This URL path may vary depending on your Jira/Zephyr configuration
        self.driver.get(f"{self.url}/secure/ZephyrLightweight.jspa")
        
        # Wait for the page to load
        time.sleep(5)
        
        # Select the version from the dropdown
        # This is a simplified approach - you may need to adjust selectors based on your Jira UI
        try:
            version_dropdown = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'version-dropdown')]")))
            version_dropdown.click()
            
            version_option = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[contains(text(), '{self.version}')]")))
            version_option.click()
            
            # Wait for the page to refresh with the selected version
            time.sleep(3)
        except Exception as e:
            print(f"Error selecting version: {e}")
            print("Continuing with default version...")
        
        print("Successfully navigated to Zephyr test cycles.")
        
    def extract_test_data(self):
        """Extract test data from the Zephyr test cycles page."""
        print("Extracting test data...")
        
        # Wait for test cycles to load
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'cycle-summary')]")))
        
        # Find all test cycles
        cycles = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'cycle-summary')]")
        print(f"Found {len(cycles)} test cycles.")
        
        for cycle_idx, cycle in enumerate(cycles):
            try:
                # Click on the cycle to expand it
                cycle.click()
                time.sleep(2)
                
                # Get cycle name
                cycle_name = cycle.find_element(By.XPATH, ".//span[contains(@class, 'cycle-name')]").text
                print(f"Processing cycle: {cycle_name}")
                
                # Find all test cases in this cycle
                test_cases = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'test-case-row')]")
                
                for test_case in test_cases:
                    try:
                        # Extract test case details
                        test_id = test_case.find_element(By.XPATH, ".//div[contains(@class, 'test-id')]").text
                        test_summary = test_case.find_element(By.XPATH, ".//div[contains(@class, 'test-summary')]").text
                        component = test_case.find_element(By.XPATH, ".//div[contains(@class, 'component')]").text
                        status = test_case.find_element(By.XPATH, ".//div[contains(@class, 'test-status')]").text
                        
                        # Add to our data collection
                        self.test_data.append({
                            'Cycle': cycle_name,
                            'Test ID': test_id,
                            'Summary': test_summary,
                            'Component': component,
                            'Status': status
                        })
                    except Exception as e:
                        print(f"Error extracting test case data: {e}")
                        continue
                
                # Click the cycle again to collapse it before moving to the next one
                cycle.click()
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing cycle {cycle_idx}: {e}")
                continue
        
        print(f"Extracted data for {len(self.test_data)} test cases.")
        
    def generate_summary_report(self, output_file=None):
        """
        Generate a summary report of test results by component.
        
        Args:
            output_file (str): Path to save the CSV report
        
        Returns:
            DataFrame: Summary report
        """
        if not self.test_data:
            print("No test data to generate report from.")
            return None
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(self.test_data)
        
        # Create a summary by component and status
        summary = df.pivot_table(
            index='Component',
            columns='Status',
            values='Test ID',
            aggfunc='count',
            fill_value=0
        )
        
        # Add a total column
        summary['Total'] = summary.sum(axis=1)
        
        # Calculate percentages
        for status in summary.columns:
            if status != 'Total':
                summary[f'{status} %'] = (summary[status] / summary['Total'] * 100).round(2)
        
        # If output file is not specified, create one with timestamp
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"zephyr_summary_{self.version}_{timestamp}.csv"
        
        # Save to CSV
        summary.to_csv(output_file)
        print(f"Summary report saved to {output_file}")
        
        return summary
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            print("WebDriver closed.")


def main():
    """Main function to run the automation."""
    parser = argparse.ArgumentParser(description='Extract test data from Jira Zephyr.')
    parser.add_argument('--url', required=True, help='Jira instance URL')
    parser.add_argument('--username', required=True, help='Jira username')
    parser.add_argument('--password', required=True, help='Jira password')
    parser.add_argument('--version', required=True, help='Version to extract data for')
    parser.add_argument('--output', help='Output CSV file path')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    args = parser.parse_args()
    
    try:
        # Initialize and run the automation
        automation = JiraZephyrAutomation(
            url=args.url,
            username=args.username,
            password=args.password,
            version=args.version,
            headless=args.headless
        )
        
        # Execute the workflow
        automation.login()
        automation.navigate_to_zephyr_cycles()
        automation.extract_test_data()
        automation.generate_summary_report(args.output)
        
    except Exception as e:
        print(f"Error running automation: {e}")
    finally:
        # Ensure WebDriver is closed
        if 'automation' in locals():
            automation.close()


if __name__ == "__main__":
    main()

