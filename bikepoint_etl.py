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

aws_access = os.getenv('ACCESS_KEY')
aws_secret_access = os.getenv('SECRET_ACCESS_KEY')
bucket = os.getenv("AWS_BUCKET_NAME")

temp_files = os.listdir("temp")
json_files = [f for f in temp_files if f.endswith(".json")]

if not json_files:
    raise FileNotFoundError("No JSON files found in temp/")
elif len(json_files) > 1:
    raise Exception("Multiple JSON files found in temp/. Expected only one.")

local_path = os.path.join("temp", json_files[0])
name_for_s3 = f"bikepoint-stage/{json_files[0]}"


s3_client = boto3.client(
        service_name='s3',
        aws_access_key_id=aws_access,
        aws_secret_access_key=aws_secret_access
    )

response = s3_client.upload_file(local_path, bucket, name_for_s3)
print(response)


# bikepoint_extract()