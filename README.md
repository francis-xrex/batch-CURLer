# Batch Curl Tool


## Quick Start

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Edit the config files:
   - Open the file `properties/config.properties`
     ```
     [Authorization]
     jwt_token=Authorization: Bearer {jwt-token}
     
     [API]
     base_url={m-kyc-prod-url}
     ```


## Scripts

The repository contains two scripts:

1. **update_occupation.py** - Updates applicant occupation data
2. **add_comment.py** - Add kyc comment API
