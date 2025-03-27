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

# API endpoint path
API_ENDPOINT = '/cms/v2/applicants/{applicant_id}/occupation'

def read_csv_data():
    """Read and parse the CSV file"""
    csv_path = 'source/2025_occupation_fix.csv'
    try:
        # Use dtype parameter to ensure numeric columns with potential leading zeros
        # are read as strings (object type in pandas)
        df = pd.read_csv(csv_path, dtype={'Expected occupation key': str})
        return df
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")

def update_occupation(applicant_id, data, jwt_token, api_base_url):
    """Make API call to update occupation"""
    url = f"{api_base_url}{API_ENDPOINT.format(applicant_id=applicant_id)}"
    headers = {
        'Authorization': jwt_token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.put(url, headers=headers, json=data)
        # Get the response content regardless of status code
        # Since we need to check for code in the JSON response
        try:
            result = response.json()
            return result
        except ValueError:
            # If can't parse JSON, return error info
            return {
                "success": False,
                "error_code": response.status_code,
                "error_message": response.text
            }
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        print(f"Error updating occupation for applicant {applicant_id}: {error_message}")
        return {
            "success": False,
            "error_code": "RequestException",
            "error_message": error_message
        }

def setup_logging():
    """Set up logging configuration and return the log filename"""
    # Set up logging
    log_dir = 'log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create a log filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"occupation_update_errors_{timestamp}.log")
    
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
        message = f"Successfully updated occupation for applicant {applicant_id}"
    
    print(message)
    # Removed logging.info call as we only want to log errors
    return message

def log_failure(applicant_id, message=None):
    """Log failure message for an applicant"""
    if message is None:
        message = f"Failed to update occupation for applicant {applicant_id}"
    
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
        log_filename = setup_logging()
        
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
            
            # Prepare data for API call - ensure occupation_key preserves leading zeros
            occupation_value = row['Expected occupation key']
            # Make sure occupation_key is exactly 3 digits with leading zeros if needed
            if occupation_value.isdigit() and len(occupation_value) < 3:
                occupation_value = occupation_value.zfill(3)
                
            data = {
                "employment_key": row['Expected employment key'],
                "occupation_key": occupation_value,
                "is_public_politician": False,
                "is_criminal_investigation": False
            }
            
            # Print the data before making the API call
            print(data);
            
            # Make API call
            result = update_occupation(applicant_id, data, jwt_token, api_base_url)
            
            # Check result for success or failure
            if result and (('code' in result and result['code'] == '0')):
                log_success(applicant_id)
            else:
                # Get error details if available
                error_details = ""
                if isinstance(result, dict):
                    if 'code' in result and result['code'] != '0':
                        error_details = f" - Error code: {result['code']}, Description: {result.get('desc', 'Unknown error')}, Data: {result.get('data', 'Unknown data')}"
                
                log_failure(applicant_id, f"Failed to update occupation for applicant {applicant_id}{error_details}")
                
        # Completion message only in console
        print(f"Process completed. Log file for errors: {log_filename}")
                
    except Exception as e:
        log_error(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main() 