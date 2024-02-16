import os
import json
import requests
import random
from supabase import create_client, Client

# Load configurations from config.json
with open('config.json', 'r') as file:
    config = json.load(file)

dir_path = config['DIRECTORY_PATH']

# Check the value of REMOTE_PUSH and set SUPABASE_URL and SUPABASE_KEY accordingly
if config.get('REMOTE_PUSH', 0) == 0:
    SUPABASE_URL = config['LOCAL']['SUPABASE']['URL']
    SUPABASE_KEY = config['LOCAL']['SUPABASE']['KEY']
else:
    SUPABASE_URL = config['REMOTE']['SUPABASE']['URL']
    SUPABASE_KEY = config['REMOTE']['SUPABASE']['KEY']

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_part_id(mpn):
    response = supabase.table("parts").select("id").filter("part", "eq", mpn).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]["id"]
    else:
        print(f"[ERROR] Unable to retrieve partId for {mpn}.")
        return None


def get_source_id(source_name):
    response = supabase.table('Sources').select('id').eq('name', source_name).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]['id']
    else:
        print(f"[ERROR] Unable to retrieve sourceId for {source_name}.")
        return None


def extract_file_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    embedding_txt = content.replace('\n', ' \n')
    mpn = embedding_txt.split(' ')[0].strip()
    source_name = os.path.basename(os.path.dirname(file_path))

    return embedding_txt, mpn, source_name


def send_request_to_supabase(url, data, token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.post(url, json=data, headers=headers, verify=False)

    if response.status_code == 409:
        print(f"[INFO] Data for {data['mpnTxt'].split(' ')[0]} is already uploaded.")
    elif response.status_code == 200:
        print(f"[SUCCESS] Data for {data['mpnTxt'].split(' ')[0]} uploaded successfully.")
    else:
        print(f"[ERROR] Failed to send request to {url}. Status code: {response.status_code}")

    return response


def main():
    filenames = os.listdir(dir_path)
    random.shuffle(filenames)

    print(f"[INFO] Starting the process for {len(filenames)} files...")

    for filename in filenames:
        file_path = os.path.join(dir_path, filename)

        if os.path.isfile(file_path):
            embedding_txt, mpn, source_name = extract_file_data(file_path)

            part_id = get_part_id(mpn)
            source_id = get_source_id(source_name)

            data = {
                "sourceId": source_id,
                "partId": part_id,
                "mpnTxt": embedding_txt
            }

            # Use the correct URL based on the REMOTE_PUSH value
            if config.get('REMOTE_PUSH', 0) == 0:
                url = config["REMOTE"]["SUPABASE"]["MPN_TXT_URL"]
            else:
                url = config["LOCAL"]["SUPABASE"]["MPN_TXT_URL"]

            token = SUPABASE_KEY

            response = send_request_to_supabase(url, data, token)

            # Log the response details
            print(f"[INFO] Processed file {filename}. Response Status Code: {response.status_code}")

    print(f"[INFO] Process completed for all files.")


if __name__ == "__main__":
    main()
