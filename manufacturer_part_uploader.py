import os
import re
import requests
import json

# Load configurations from config.json
with open('config.json', 'r') as file:
    config = json.load(file)

DIRECTORY = config['DIRECTORY_PATH']

# Determine whether to use local or remote configurations based on REMOTE_PUSH
if config.get('REMOTE_PUSH', 0) == 0:
    BASE_URL = config['LOCAL']['API']['BASE_URL']
    AUTH_TOKEN = config['LOCAL']['API']['AUTHORIZATION_TOKEN']
else:
    BASE_URL = config['REMOTE']['API']['BASE_URL']
    AUTH_TOKEN = config['REMOTE']['API']['AUTHORIZATION_TOKEN']

# ----------- Utility Functions -----------
def extract_manufacturer(data):
    """Extract manufacturer from the data."""
    pattern = r"Manufacturer:\s*(\S+)"
    match = re.search(pattern, data)
    return match.group(1) if match else None

def extract_manufacturer_part_number(data):
    """Extract manufacturer part number from the data."""
    lines = data.split("\n")
    return lines[0].strip()

def get_id_by_name(data, target_name):
    """Get ID by name from the manufacturer data."""
    for item in data:
        if item['name'] == target_name:
            return item['id']
    return None

# ----------- API Handling Functions -----------
def getManufacturers():
    """Get a list of manufacturers from the API."""
    url = f"{BASE_URL}/manufacturer/getManufacturers?Content-Type=application/json&Authorization=Bearer {AUTH_TOKEN}"
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    return response.json()

def addManufacturerRequest(manufacturer):
    """Add a manufacturer using the API."""
    url = f"{BASE_URL}/manufacturer/add?Content-Type=application/json&Authorization=Bearer {AUTH_TOKEN}"
    payload = {"name": manufacturer}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def addPart(part_name, org_id):
    """Add a part using the API."""
    url = f"{BASE_URL}/addPart?Content-Type=application/json&Authorization=Bearer {AUTH_TOKEN}"
    payload = {
        "part": part_name,
        "orgId": org_id
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def getParts():
    """Get a list of parts from the API."""
    url = f"{BASE_URL}/getParts?Content-Type=application/json&Authorization=Bearer {AUTH_TOKEN}"
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    return response.json()

# ----------- Main Script Handling -----------
def process_and_upload_data(file_path):
    """Read and process data from a file."""
    print(f"Processing file: {file_path}...")

    with open(file_path, "r") as file:
        data = file.read()

    manufacturer = extract_manufacturer(data)
    if manufacturer:
        print(f"Extracted Manufacturer: {manufacturer}")
    else:
        print("Error: Manufacturer not found!")
        return

    manufacturer_part_number = extract_manufacturer_part_number(data)
    if manufacturer_part_number:
        print(f"Extracted Manufacturer Part Number: {manufacturer_part_number}")
    else:
        print("Error: Manufacturer Part Number not found!")
        return

    print("Requesting addition of manufacturer...")
    addManufacturerRequest(manufacturer)

    print("Fetching manufacturers...")
    manufacturer_data = getManufacturers()
    org_id = get_id_by_name(manufacturer_data, manufacturer)

    if org_id:
        print(f"Found Organization ID: {org_id} for Manufacturer: {manufacturer}")
        print(f"Uploading Part: {manufacturer_part_number} under Organization ID: {org_id}...")
        response = addPart(manufacturer_part_number, org_id)

        if response.status == 409:
            print(f"Part {manufacturer_part_number} already exists in the database for Organization ID: {org_id}.")
    else:
        print(f"Error: Organization ID not found for Manufacturer: {manufacturer}")

def main():
    """Main script execution."""
    try:
        # List all files in the directory
        file_list = os.listdir(DIRECTORY)

        # Process each file one by one
        for file_name in file_list:
            if file_name.endswith(".txt"):
                file_path = os.path.join(DIRECTORY, file_name)
                process_and_upload_data(file_path)

    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
