import json
import requests
from supabase import create_client, Client

# Load configurations from config.json
with open('config.json', 'r') as file:
    config = json.load(file)

# Check the value of REMOTE_PUSH and set SUPABASE_URL, SUPABASE_KEY, and TS_VECTOR_URL accordingly
if config.get('REMOTE_PUSH', 0) == 0:
    SUPABASE_URL = config['LOCAL']['SUPABASE']['URL']
    SUPABASE_KEY = config['LOCAL']['SUPABASE']['KEY']
    TS_VECTOR_URL = config['LOCAL']['SUPABASE']['SET_TS_VECTOR']
else:
    SUPABASE_URL = config['REMOTE']['SUPABASE']['URL']
    SUPABASE_KEY = config['REMOTE']['SUPABASE']['KEY']
    TS_VECTOR_URL = config['REMOTE']['SUPABASE']['SET_TS_VECTOR']

url_supabase: str = SUPABASE_URL
key_supabase: str = SUPABASE_KEY
supabase: Client = create_client(url_supabase, key_supabase)

def send_request_to_supabase(url, data, token):
    """Send a POST request to the specified Supabase URL."""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.post(url, json=data, headers=headers, verify=False)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Print success message
        print(
            f"Success: Request for embeddingId {data['embeddingId']} completed with status code {response.status_code}.")

        return response
    except requests.RequestException as e:
        # Print warning message
        print(f"Warning: Error sending request for embeddingId {data['embeddingId']}: {e}")
        return None

def get_embedding_ids():
    """Retrieve embedding IDs from the Supabase table."""
    try:
        response = supabase.table("Embeddings").select("id").execute()
        ids = [item['id'] for item in response.data]
        return ids
    except Exception as e:
        # Print error message
        print(f"Error fetching embedding IDs: {e}")
        return []

def main():
    """Main function to retrieve embedding IDs and send requests."""
    embedding_ids = get_embedding_ids()
    print(f"Info: Found {len(embedding_ids)} embedding IDs to process.")

    for embedding_id in embedding_ids:
        data = {
            "embeddingId": embedding_id
        }

        response = send_request_to_supabase(TS_VECTOR_URL, data, SUPABASE_KEY)

        # If the response is not None, print the response content
        if response:
            print("Response Content:")
            print(response.text)
            print("-" * 50)  # Add a separator for clarity

        # If the response is None, continue to the next iteration
        else:
            continue


if __name__ == '__main__':
    main()
