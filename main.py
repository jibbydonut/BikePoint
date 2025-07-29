
import os
import logging
from dotenv import load_dotenv
from bikepoint_etl import bikepoint_extract,get_single_json_from_temp,upload_json_to_s3
from helper import setup_logger

setup_logger()
load_dotenv()
import os
os.makedirs('temp', exist_ok=True)


def main():
    try:
        # Extract data from API
        bikepoint_extract()
        logging.info("Stage 1: Extraction successful")

        # Validate and locate JSON
        local_path, name_for_s3 = get_single_json_from_temp()
        logging.info("Stage 2: JSON validation successful")

        # Upload to S3
        aws_access = os.getenv('ACCESS_KEY')
        aws_secret = os.getenv('SECRET_ACCESS_KEY')
        bucket = os.getenv("AWS_BUCKET_NAME")

        upload_json_to_s3(local_path, bucket, name_for_s3, aws_access, aws_secret)
        logging.info("Stage 3: Upload successful")

        logging.info("🎉 Pipeline completed successfully")

    except Exception as e:
        logging.error(f"❌ Pipeline failed at some stage: {e}")

if __name__ == "__main__":
    main()