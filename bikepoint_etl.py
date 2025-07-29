import requests
import os
import json
import logging
from datetime import datetime, timedelta
import time
from helper import setup_logger
import boto3
from dotenv import load_dotenv

setup_logger()
load_dotenv()

import requests
import json
import logging
import time
import os
import boto3
from datetime import datetime, timedelta
import tempfile

def bikepoint_extract(temp_dir):
    for i in range(3):
        try:
            response = requests.get("https://api.tfl.gov.uk/BikePoint/")
            response.raise_for_status()

            bikepoints = response.json()

            # Extract modification times
            mod_times = []
            for point in bikepoints:
                for item in point.get("additionalProperties", []):
                    if "modified" in item:
                        mod_times.append(item["modified"])

            latest_mod_time = datetime.strptime(max(mod_times), "%Y-%m-%dT%H:%M:%S.%fZ")

            if datetime.now() - latest_mod_time > timedelta(days=1):
                raise Exception("Last Update Over 1 Day Ago - Outside acceptance window")
            else:
                logging.info("Latest retrieved data within 24 hour acceptance window")

            # Write to temp file
            filename = "bikepoint_json_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".json"
            filepath = os.path.join(temp_dir, filename)

            with open(filepath, "w") as f:
                json.dump(bikepoints, f, indent=4)

            logging.info(f"Data successfully written to {filepath}")
            return filepath  # Return path for downstream use

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get data - {e}")
            time.sleep(2)

        except json.JSONDecodeError as j:
            logging.error(f"Invalid JSON - {j}")
            raise

        except Exception as e:
            logging.error(f"{e}")
            time.sleep(5)

    raise Exception("Failed to retrieve valid data after 3 attempts")


def get_single_json_from_temp(temp_dir):
    try:
        temp_files = os.listdir(temp_dir)
        json_files = [f for f in temp_files if f.endswith(".json")]

        if not json_files:
            raise FileNotFoundError("No JSON files found in temp directory")
        elif len(json_files) > 1:
            raise Exception("Multiple JSON files found in temp directory. Expected only one.")

        local_path = os.path.join(temp_dir, json_files[0])
        name_for_s3 = f"bikepoint-stage/{json_files[0]}"

        logging.info(f"Identified JSON file for upload: {json_files[0]}")
        return local_path, name_for_s3
    except Exception as e:
        logging.error(f"Error accessing temp directory: {e}")
        raise


def upload_json_to_s3(file_path, bucket, object_name, aws_access, aws_secret_access):
    s3_client = boto3.client(
        service_name='s3',
        aws_access_key_id=aws_access,
        aws_secret_access_key=aws_secret_access
    )
    try:
        s3_client.upload_file(file_path, bucket, object_name)
        logging.info(f"File uploaded to S3: s3://{bucket}/{object_name}")
    except boto3.exceptions.S3UploadFailedError as e:
        logging.error(f"S3 upload failed: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during S3 upload: {e}")


# 🧪 Example usage
if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            file_path = bikepoint_extract(temp_dir)
            local_path, s3_key = get_single_json_from_temp(temp_dir)
            upload_json_to_s3(local_path, "your-bucket-name", s3_key, "your-access-key", "your-secret-key")
        except Exception as e:
            logging.error(f"Pipeline failed: {e}")