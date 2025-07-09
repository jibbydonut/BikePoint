import requests
import os
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

try:
    response = requests.get("https://api.tfl.gov.uk/BikePoint/")
    response.raise_for_status()

    bikepoints = response.json()

    filename = "bikepoint_json_" + datetime.now().strftime("%Y_%m_%d_%H:%M:%S")
    basepath = r"/temp"

    filepath = os.path.join(basepath, filename + ".json")

    with open(filepath,"w",encoding="utf-8") as f:
        json.dump(bikepoints,f,indent=4)
    
    logging.info(f"Data successfully written to {filepath}")

except requests.exceptions.RequestException as e:
    logging.error(f"Failed to get data - {e}")