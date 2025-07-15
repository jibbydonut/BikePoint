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

def bikepoint_extract():

    for i in range(3):
        try:
            response = requests.get("https://api.tfl.gov.uk/BikePoint/")
            response.raise_for_status()

            bikepoints = response.json()

            # if modify date > 1 day ago, raise exception
            # get latest modify time from json
            mod_times = []
            for point in bikepoints:
                for item in point.get("additionalProperties",[]):
                    if "modified" in item:
                        mod_times.append(item["modified"])
            
            latest_mod_time = datetime.strptime(max(mod_times), "%Y-%m-%dT%H:%M:%S.%fZ")

            if datetime.now() - latest_mod_time > timedelta(days=1):
                raise Exception("Last Update Over 1 Day Ago - Outside acceptance window")
            else:
                logging.info(f"Latest retrieved data within 24 hour acceptance window")

            # Setup filename, path and output to file
            filename = "bikepoint_json_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

            filepath = "temp/" + filename + ".json"

            with open(filepath,"w") as f:
                json.dump(bikepoints,f,indent=4)

            logging.info(f"Data successfully written to {filepath}")
            break

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get data - {e}")
            time.sleep(2)

        except json.JSONDecodeError as j:
            logging.error(f"Invalid JSON - {j}")
            raise
            time.sleep(2)

        except Exception as e:
            logging.error(f"{e}")
            time.sleep(5)


# temp_files = os.listdir("temp")
# json_files = [f for f in temp_files if f.endswith(".json")]

# if not json_files:
#     raise FileNotFoundError("No JSON files found in temp/")
# elif len(json_files) > 1:
#     raise Exception("Multiple JSON files found in temp/. Expected only one.")

# local_path = os.path.join("temp", json_files[0])
# name_for_s3 = f"bikepoint-stage/{json_files[0]}"


# s3_client = boto3.client(
#         service_name='s3',
#         aws_access_key_id=aws_access,
#         aws_secret_access_key=aws_secret_access
#     )

# try:
#     s3_client.upload_file(local_path, bucket, name_for_s3)
#     logging.info(f"File uploaded to S3: s3://{bucket}/{name_for_s3}")
#     os.remove(local_path)
# except boto3.exceptions.S3UploadFailedError as e:
#     logging.error(f"S3 upload failed: {e}")
# except Exception as e:
#     logging.error(f"Unexpected error during S3 upload: {e}")

def get_single_json_from_temp():
    try:
        temp_files = os.listdir("temp")
        json_files = [f for f in temp_files if f.endswith(".json")]

        if not json_files:
            raise FileNotFoundError("No JSON files found in temp/")
        elif len(json_files) > 1:
            raise Exception("Multiple JSON files found in temp/. Expected only one.")
        
        local_path = os.path.join("temp", json_files[0])
        name_for_s3 = f"bikepoint-stage/{json_files[0]}"

        logging.info(f"Identified JSON file for upload: {json_files[0]}")
        return local_path, name_for_s3
    except FileNotFoundError as fnf:
        logging.error(f"File error: {fnf}")
        raise
    except Exception as e:
        logging.error(f"Validation error in temp/: {e}")
        raise


def upload_json_to_s3(file_path, bucket, object_name, aws_access, aws_secret_access):
    s3_client = boto3.client(
        service_name='s3',
        aws_access_key_id=aws_access,
        aws_secret_access_key=aws_secret_access
    )
    try:
        s3_client.upload_file(file_path, bucket, object_name)
        logging.info(f"File uploaded to S3: s3://{bucket}/{name_for_s3}")
        os.remove(local_path)
    except boto3.exceptions.S3UploadFailedError as e:
        logging.error(f"S3 upload failed: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during S3 upload: {e}")


# aws_access = os.getenv('ACCESS_KEY')
# aws_secret_access = os.getenv('SECRET_ACCESS_KEY')
# bucket = os.getenv("AWS_BUCKET_NAME")

bikepoint_extract()

try:
    local_path, name_for_s3 = get_single_json_from_temp()
    upload_json_to_s3(local_path, bucket, name_for_s3, aws_access, aws_secret_access)
except Exception as e:
    logging.error(f"Pipeline failed: {e}")



