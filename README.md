# BikePoint Data Pipeline

A Python script that extracts London bike point data from the Transport for London (TfL) API, validates data freshness, and uploads it to AWS S3 for further processing.

## Overview

This pipeline performs the following operations:
1. **Data Extraction**: Fetches bike point data from the TfL BikePoint API
2. **Data Validation**: Ensures data is fresh (updated within the last 24 hours)
3. **Local Storage**: Temporarily stores data as JSON files with timestamped filenames
4. **Cloud Upload**: Uploads validated data to AWS S3 for downstream processing

## Features

- **Retry Logic**: Automatically retries failed API requests up to 3 times with exponential backoff
- **Data Freshness Validation**: Rejects data that hasn't been updated in over 24 hours
- **Error Handling**: Comprehensive logging and exception handling for robust operation
- **Temporary File Management**: Uses Python's `tempfile` module for secure temporary storage
- **AWS Integration**: Direct upload to S3 with proper error handling

## Prerequisites

### Python Dependencies
```bash
pip install requests boto3 python-dotenv
```

### Required Files
- `helper.py` - Must contain a `setup_logger()` function for logging configuration
- `.env` - Environment variables file (optional, for storing AWS credentials)

### AWS Credentials
Configure AWS credentials using one of these methods:
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- AWS credentials file (`~/.aws/credentials`)
- IAM roles (if running on EC2)
- Pass credentials directly to the `upload_json_to_s3()` function

## Installation

1. Clone or download the script
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `helper.py` file with logging setup:
   ```python
   import logging
   
   def setup_logger():
       logging.basicConfig(
           level=logging.INFO,
           format='%(asctime)s - %(levelname)s - %(message)s'
       )
   ```
4. Configure your AWS credentials

## Usage

### Basic Usage
```python
from your_script import bikepoint_extract, get_single_json_from_temp, upload_json_to_s3
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    try:
        # Extract data from TfL API
        file_path = bikepoint_extract(temp_dir)
        
        # Get file details for S3 upload
        local_path, s3_key = get_single_json_from_temp(temp_dir)
        
        # Upload to S3
        upload_json_to_s3(
            local_path, 
            "your-bucket-name", 
            s3_key, 
            "your-access-key", 
            "your-secret-key"
        )
    except Exception as e:
        print(f"Pipeline failed: {e}")
```

### Environment Variables
Create a `.env` file to store sensitive information:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
S3_BUCKET_NAME=your_bucket_name_here
```

## API Reference

### `bikepoint_extract(temp_dir)`
Extracts bike point data from the TfL API and saves it to a temporary directory.

**Parameters:**
- `temp_dir` (str): Path to temporary directory for file storage

**Returns:**
- `str`: Full path to the created JSON file

**Raises:**
- `Exception`: If data is older than 24 hours or after 3 failed attempts

### `get_single_json_from_temp(temp_dir)`
Identifies and prepares a single JSON file from the temporary directory for S3 upload.

**Parameters:**
- `temp_dir` (str): Path to temporary directory containing JSON files

**Returns:**
- `tuple`: (local_file_path, s3_object_name)

**Raises:**
- `FileNotFoundError`: If no JSON files found
- `Exception`: If multiple JSON files found

### `upload_json_to_s3(file_path, bucket, object_name, aws_access, aws_secret_access)`
Uploads a local file to AWS S3.

**Parameters:**
- `file_path` (str): Local path to file
- `bucket` (str): S3 bucket name
- `object_name` (str): S3 object key/name
- `aws_access` (str): AWS access key ID
- `aws_secret_access` (str): AWS secret access key

## Data Structure

The script processes TfL BikePoint API data, which includes:
- Bike point locations and IDs
- Available bikes and docking spaces
- Additional properties with modification timestamps
- Station status information

## Error Handling

The pipeline includes comprehensive error handling for:
- **Network Issues**: Automatic retries with backoff for API requests
- **Data Quality**: Validation of data freshness and JSON structure
- **File Operations**: Safe temporary file handling
- **AWS Operations**: S3 upload error handling and logging

## Logging

All operations are logged with appropriate levels:
- `INFO`: Successful operations and status updates
- `ERROR`: Failed operations with details
- Timestamps and structured formatting for easy monitoring

## File Naming Convention

Generated files follow the pattern:
```
bikepoint_json_YYYY_MM_DD_HH_MM_SS.json
```

S3 objects are stored under the prefix:
```
bikepoint-stage/bikepoint_json_YYYY_MM_DD_HH_MM_SS.json
```

## Monitoring and Maintenance

- Monitor logs for API failures or data quality issues
- Verify S3 uploads are completing successfully
- Check data freshness validation is working as expected
- Review AWS costs and S3 storage usage regularly

## License

This project is provided as-is for data pipeline purposes. Ensure compliance with TfL API terms of service when using their data.

## Contributing

When modifying this script:
1. Maintain the existing error handling patterns
2. Update logging messages for new functionality
3. Test retry logic thoroughly
4. Validate AWS credential handling remains secure