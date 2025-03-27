# Batch Occupation Update Tool

This tool updates applicant occupation data via API calls using data from a CSV file.

## Setup

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure settings:
   - Open the file `properties/config.properties`
   - The file should contain your configuration in the format:
     ```
     [Authorization]
     jwt_token=Authorization: Bearer YOUR_JWT_TOKEN
     
     [API]
     base_url=https://m-kyc-api.qa.xrex.works
     ```
   - Save the file

3. Prepare your CSV file:
   - The CSV should be located at `source/2025_occupation_fix.csv`
   - Required columns: `UID`, `Expected employment key`, `Expected occupation key`

## Available Scripts

The repository contains two scripts:

1. **update_occupation.py** - Updates applicant occupation data
2. **add_comment.py** - Alternative script with the same functionality (can be customized for different needs)

## Running the Tool

To run the main script:
```
python update_occupation.py
```

To run the alternative script:
```
python add_comment.py
```

Both scripts will read the CSV file and make API calls to update the occupation information.

## Output

The scripts will print the status of each API call, indicating success or failure for each applicant ID. 