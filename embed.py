#!/bin/python3
import os
import json
import common as common
import config as config
import requests
import random
from supabase import create_client, Client

CONFIG = common.read_json(config.CONFIG_FILE)

# Load configurations from config.json
with open('config.json', 'r') as file:
    config = json.load(file)

DIRECTORY = config['DIRECTORY_PATH']

# Check the value of REMOTE_PUSH and set SUPABASE_URL and SUPABASE_KEY accordingly
if config.get('REMOTE_PUSH', 0) == 0:
    SUPABASE_URL = config['LOCAL']['SUPABASE']['URL']
    SUPABASE_KEY = config['LOCAL']['SUPABASE']['KEY']
else:
    SUPABASE_URL = config['REMOTE']['SUPABASE']['URL']
    SUPABASE_KEY = config['REMOTE']['SUPABASE']['KEY']

url: str = SUPABASE_URL
key: str = SUPABASE_KEY
supabase: Client = create_client(url, key)

def __read_file(fpath):
    """
    """
    outstr = ""
    fptr = open(fpath, "r")
    for elem in fptr.readlines():
        outstr += elem
    return outstr

def check_part_exists(partId):
    result = supabase.table('Embeddings').select('id').eq('partId', partId).execute()
    return len(result.data) > 0

def extract_manufacturer_part_number(data):
    """Extract manufacturer part number from the data."""
    lines = data.split("\n")
    return lines[0].strip()

def custom_dispatch_request(rtype, url, data, token=None, output_file_name=None):
    if rtype == 'POST':
        return custom_send_post_request(url, data, token, output_file_name)

def custom_send_post_request(url, data, token, output_file_name):
    headers = {'Authorization': 'Bearer {}'.format(token)}
    r = requests.post(url, json=data, headers=headers, verify=False)

    try:
        output = r.json()
        common.write_json(output_file_name, output)
    except:
        with open(CONFIG["ERROR_TXT"], "wb") as binary_file:
            binary_file.write(r.content)
    return r.status_code

def extract_embedding_from_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        embedding = data['data'][0]['embedding']

        return embedding

def main():
    file_list = os.listdir(DIRECTORY)
    random.shuffle(file_list)

    for filename in file_list:
        fpath = os.path.join(DIRECTORY, filename)
        print(f"Processing file: {fpath}") # Debug info for file being processed

        outstr = common.read_file(fpath)
        source_directory = os.path.dirname(fpath)
        source_name = os.path.basename(source_directory)

        with open(fpath, "r") as file:
            data = file.read()

        part_number = extract_manufacturer_part_number(data)
        print(f"Extracted part number: {part_number}") # Debug info for extracted part number

        sourceId = supabase.table('Sources').select('id').eq('name', source_name).execute().data[0]['id']

        part_query = supabase.table('parts').select('id').eq('part', part_number).execute()

        # Check if partId is found
        if not part_query.data:
            print(f"Part {part_number} not found in the database, skipping to next.")
            continue

        partId = part_query.data[0]['id']

        if check_part_exists(partId):
            print(f"Part {partId} exist in the database. Skipping...")
            continue
        else:
            url = CONFIG["OPEN_AI"]["EMBED_URL"]
            data = {"input": outstr, "model": "text-embedding-ada-002"}
            token = CONFIG["OPEN_AI"]["KEY"]

            output_file_name = os.path.join("embeddings/tme", os.path.splitext(filename)[0] + ".json")
            print(f"Sending POST request to {url}")  # Debug info for URL being hit

            custom_dispatch_request('POST', url, data, token, output_file_name=output_file_name)

            embedding_vector = extract_embedding_from_json(output_file_name)
            print(f"Extracted embedding: {embedding_vector}")  # Debug info for extracted embedding

            supabase.table('Embeddings').insert(
                {"sourceId": sourceId, "partId": partId, "embedding": embedding_vector}).execute()

            print(f"Inserted embedding for part {partId} from source {sourceId}")  # Debug info for successful insertion

if __name__ == "__main__":
    main()