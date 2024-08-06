"""
Apollo API Client

Usage:
  apollo.py company <query>
  apollo.py create <name> <email> <company>
  apollo.py upload <type> <file>
  apollo.py enrich <domains>...
  apollo.py (-h | --help)
  apollo.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

Commands:
  company <query>     Search for contacts or companies.
  create <name> <email> <company>     Create a new contact.
  upload <type> <file>     Upload data from a CSV file. Type can be 'contact' or 'company'.
  enrich <domains>...     Enrich data for specified domains.
"""

import requests
import logging
from docopt import docopt
import os
import pandas as pd
import json

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to read API key from file
def read_api_key():
    if not os.path.exists('api_key.key'):
        logger.error("API key file 'api_key.key' not found.")
        raise FileNotFoundError("API key file 'api_key.key' not found.")
    with open('api_key.key', 'r') as file:
        return file.read().strip()

# Function to upload data from CSV
def upload_data(file_path, data_type):
    if not os.path.exists(file_path):
        logger.error(f"CSV file '{file_path}' not found.")
        raise FileNotFoundError(f"CSV file '{file_path}' not found.")
    
    # Read CSV file
    data = pd.read_csv(file_path)
    
    # Define the endpoint based on data type
    if data_type == 'contact':
        url = f"{BASE_URL}/contacts"
    elif data_type == 'company':
        url = f"{BASE_URL}/accounts"
    else:
        logger.error(f"Unsupported data type: {data_type}")
        raise ValueError(f"Unsupported data type: {data_type}")
    
    # Iterate over rows in the CSV file
    for _, row in data.iterrows():
        try:
            response = requests.post(url, headers=headers, json=row.to_dict())
            response.raise_for_status()
            print(f"Successfully uploaded: {row}")
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            logger.error(f"An error occurred: {err}")
            print(f"An error occurred: {err}")

# Function to pretty print JSON response
def pretty_print_json(data):
    if isinstance(data, dict):
        data_items = [data]
    elif isinstance(data, list):
        data_items = data
    else:
        logger.error("Unexpected data format. Expected a list or dict.")
        print("Unexpected data format.")
        return

    for idx, item in enumerate(data_items, start=1):
        print(f"Item {idx}:")
        pretty_json = json.dumps(item, indent=4)
        print(pretty_json)

# Function to enrich data for specified domains
def enrich_domains(domains):
    url = "https://api.apollo.io/api/v1/organizations/bulk_enrich"
    data = {
        "domains": domains
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        pretty_print_json(response_data)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Define your API key file and base URL
API_KEY_FILE = 'api_key.key'
BASE_URL = "https://api.apollo.io/v1"

# Main function
if __name__ == '__main__':
    try:
        api_key = read_api_key()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        logger.error("Exiting due to missing API key file.")
        exit(1)

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'X-Api-Key': api_key
    }

    arguments = docopt(__doc__, version='Apollo API Client 1.0')

    if arguments['company']:
        query = arguments['<query>']
        search_url = f"{BASE_URL}/accounts"
        params = {"name": query}
        try:
            response = requests.post(search_url, headers=headers, json=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            response_data = response.json()
            pretty_print_json(response_data)
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            logger.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
            logger.error(f"An error occurred: {err}")

    elif arguments['create']:
        name = arguments['<name>']
        email = arguments['<email>']
        company = arguments['<company>']
        create_url = f"{BASE_URL}/contacts"
        data = {
            "first_name": name,
            "email": email,
            "company": company
        }
        try:
            response = requests.post(create_url, headers=headers, json=data)
            response.raise_for_status()
            if response.status_code == 201:
                print("Contact created:", response.json())
            elif response.status_code == 200:
                print(f"Solicitud aceptada: {response.text}")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            logger.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")
            logger.error(f"An error occurred: {err}")

    elif arguments['upload']:
        data_type = arguments['<type>']
        file_path = arguments['<file>']
        try:
            upload_data(file_path, data_type)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            logger.error(f"Error: {e}")

    elif arguments['enrich']:
        domains = arguments['<domains>']
        try:
            enrich_domains(domains)
        except Exception as e:
            print(f"Error: {e}")
            logger.error(f"Error: {e}")