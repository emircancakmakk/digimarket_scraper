import requests
import hashlib
import os
import json
from supabase import create_client, Client
import base64
import random

# Load configurations from config.json
with open('config.json', 'r') as file:
    config = json.load(file)

# Determine whether to use local or remote configurations based on REMOTE_PUSH
if config.get('REMOTE_PUSH', 0) == 0:
    SUPABASE_CONFIG = config['LOCAL']['SUPABASE']
else:
    SUPABASE_CONFIG = config['REMOTE']['SUPABASE']

# Use the configurations in the script
dir_path = config['DIRECTORY_PATH']
SUPABASE_URL = SUPABASE_CONFIG['URL']
SUPABASE_KEY = SUPABASE_CONFIG['KEY']
CHECK_FILE_UPLOADED_ENDPOINT = SUPABASE_CONFIG['CHECK_FILE_UPLOADED_URL']
UPLOAD_DOCUMENT_ENDPOINT = SUPABASE_CONFIG['UPLOAD_DOCUMENT_URL']
SET_EMBEDDING_UPLOADED_ENDPOINT = SUPABASE_CONFIG['SET_EMBEDDING_UPLOADED']

url: str = SUPABASE_URL
key: str = SUPABASE_KEY
supabase: Client = create_client(url, key)

def send_post_request_to_supabase(url, data, token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to send request to {url}. Reason: {e}")
        return None

def check_file_uploaded(embedding_id):
    data = {
        "embeddingId": embedding_id
    }

    url = CHECK_FILE_UPLOADED_ENDPOINT
    token = config["REMOTE"]["SUPABASE"]["KEY"]

    response = send_post_request_to_supabase(url, data, token)

    if response and response.status_code == 200:
        return response.json().get("uploaded", False)
    return False

def get_part_id(filename):
    response = supabase.table("parts").select("id").filter("part", "eq", filename).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]["id"]
    else:
        print(f"[WARNING] Unable to retrieve partId for {filename}.")
        return None

def get_embedding_id(part_id):
    response = supabase.table("Embeddings").select("id").filter("partId", "eq", part_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]["id"]
    else:
        print(f"[WARNING] Unable to retrieve embeddingId for partId {part_id}.")
        return None

def main():
    filenames = os.listdir(dir_path)
    random.shuffle(filenames)

    total_files = len(filenames)
    uploaded_files = 0

    print(f"[INFO] Starting the upload process for {total_files} files...")

    for filename in filenames:
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    content = file.read()
                    encoded_content = base64.b64encode(content).decode('utf-8')
                    first_line = content.split(b'\n')[0].decode('utf-8').strip()
                    md5_hash = hashlib.md5(content).hexdigest()
        except FileNotFoundError:
            print(f"[WARNING] File {file_path} not found. Skipping...")
            continue
        except Exception as e:
            print(f"[ERROR] Failed to read file {file_path}. Reason: {e}")
            continue

        part_id = get_part_id(first_line)
        if part_id is None:
            print(f"[WARNING] Skipping file {filename} as partId could not be retrieved.")
            continue

        embedding_id = get_embedding_id(part_id)
        if embedding_id is None:
            print(f"[WARNING] Skipping file {filename} as embeddingId could not be retrieved for partId {part_id}.")
            continue

        if check_file_uploaded(embedding_id):
            print(f"[INFO] File {filename} is already uploaded. Skipping...")
            continue

        data = {
            "md5sum": md5_hash,
            "name": first_line,
            "embeddingId": embedding_id,
            "docType": "text/plain",
            "fileContent": encoded_content
        }

        try:
            upload_response = send_post_request_to_supabase(UPLOAD_DOCUMENT_ENDPOINT, data, SUPABASE_KEY)
            upload_response_json = upload_response.json()
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to decode JSON response for file {filename}.")
            continue
        except Exception as e:
            print(f"[ERROR] Failed to process file {filename}. Reason: {e}")
            continue

        if upload_response.status_code == 200:
            data = {
                "embeddingId": embedding_id,
                "uploaded": 1
            }
            response = send_post_request_to_supabase(SET_EMBEDDING_UPLOADED_ENDPOINT, data, SUPABASE_KEY)
            print(f"[SUCCESS] Uploaded file {filename}.")
            uploaded_files += 1
        else:
            print(f"[ERROR] Failed to upload {filename}. Status code: {upload_response.status_code}")

    print(f"[INFO] Upload process completed. {uploaded_files}/{total_files} files uploaded successfully.")

if __name__ == "__main__":
    main()
