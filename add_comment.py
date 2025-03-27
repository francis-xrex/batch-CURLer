import os
import json
import pandas as pd
import requests
import configparser
import datetime
import logging

# Function to read configuration from properties file
def read_config():
    """Read configuration from config.properties file"""
    config_file_path = 'properties/config.properties'
    try:
        # Use configparser to read the INI-style properties file
        config = configparser.ConfigParser()
        config.read(config_file_path)
        
        # Create configuration dictionary
        configuration = {}
        
        # Get the JWT token from the Authorization section
        if 'Authorization' not in config:
            raise ValueError("Authorization section not found in config file")
        
        if 'jwt_token' not in config['Authorization']:
            raise ValueError("jwt_token key not found in Authorization section")
        
        configuration['jwt_token'] = config['Authorization']['jwt_token']
        
        # Get the API base URL from the API section
        if 'API' not in config:
            raise ValueError("API section not found in config file")
        
        if 'base_url' not in config['API']:
            raise ValueError("base_url key not found in API section")
        
        configuration['api_base_url'] = config['API']['base_url']
        
        return configuration
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at {config_file_path}")
    except Exception as e:
        raise Exception(f"Error reading configuration: {str(e)}")

# API endpoint paths
COMMENT_API_ENDPOINT = '/cms/v2/applicants/{applicant_id}/institutions/{institution_key}/comment'

def read_csv_data():
    """Read and parse the CSV file"""
    csv_path = 'source/2025_occupation_fix.csv'
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")

def add_comment(applicant_id, institution_key, comment_data, jwt_token, api_base_url):
    """Make API call to add a comment to an institution"""
    url = f"{api_base_url}{COMMENT_API_ENDPOINT.format(applicant_id=applicant_id, institution_key=institution_key)}"
    headers = {
        'Authorization': jwt_token,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, json=comment_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error adding comment for applicant {applicant_id}, institution {institution_key}: {str(e)}")
        return None

def setup_logging():
    """Set up logging configuration and return the log filename"""
    # Set up logging
    log_dir = 'log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create a log filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"add_comment_errors_{timestamp}.log")
    
    # Configure logging to only capture errors and above
    logging.basicConfig(
        filename=log_filename,
        level=logging.ERROR,  # Changed from INFO to ERROR
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return log_filename

def log_success(applicant_id, message=None):
    """Log success message for an applicant"""
    if message is None:
        message = f"Successfully add comment for applicant {applicant_id}"
    
    print(message)
    # Removed logging.info call as we only want to log errors
    return message

def log_failure(applicant_id, message=None):
    """Log failure message for an applicant"""
    if message is None:
        message = f"Failed to add comment for applicant {applicant_id}"
    
    print(message)
    logging.error(message)  # Keep error logging
    return message

def log_error(error_message):
    """Log an error message"""
    print(error_message)
    logging.error(error_message)

def main():
    try:
        # Set up logging
        setup_logging()
        
        # Read configuration
        config = read_config()
        jwt_token = config['jwt_token']
        api_base_url = config['api_base_url']
        
        # Read CSV data
        df = read_csv_data()
        
        # Process each row
        for index, row in df.iterrows():
            # Get applicant ID from the UID column
            applicant_id = row['Applican ID']
            
            # Add a comment to TW institution for this applicant
            institution_key = row['Institution']
            comment_data = {
                 "comment": (
                    "- Change occupation CMS note: Occupation updated due to data segregation issue from 2.0 to 3.0.\n"
                    "- Change criminal subjected CMS note: Criminal subjected updated as user is from 2.0."
                )
            }
        
            # Make comment API call
            result = add_comment(applicant_id, institution_key, comment_data, jwt_token, api_base_url)
                            
            if result and (('code' in result and result['code'] == '0')):
                log_success(applicant_id)
            else:
                # Get error details if available
                error_details = ""
                if isinstance(result, dict):
                    if 'code' in result and result['code'] != '0':
                        error_details = f" - Error code: {result['code']}, Description: {result.get('desc', 'Unknown error')}, Data: {result.get('data', 'Unknown data')}"
                
                log_failure(applicant_id, f"Failed to add comment for applicant: {applicant_id}{error_details}")
    except Exception as e:
        print(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main() 