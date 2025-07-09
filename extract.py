import requests
import os
import json
import logging
from datetime import datetime, timedelta
import time

logging.basicConfig(filename='bikepoint_log.log', encoding='utf-8', level=logging.DEBUG)

for i in range(3):
    try:
        response = requests.get("https://api.tfl.gov.uk/BikPoint/")
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