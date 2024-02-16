import os
import json

# Load configurations from config.json
with open('config.json', 'r') as file:
    config = json.load(file)

dir = config['DIRECTORY_PATH']


def extract_keys_from_txt(file_path, keys_values):
    with open(file_path, 'r') as file:
        for line in file:
            if ':' in line:
                key, value = line.strip().split(':', 1)  # Split only at the first colon
                key = key.strip()
                value = value.strip()
                if key not in keys_values:
                    keys_values[key] = value
    return keys_values


def main():
    all_keys_values = {}

    # Loop through each file in the directory
    for filename in os.listdir(dir):
        if filename.endswith('.txt'):
            input_file_path = os.path.join(dir, filename)
            all_keys_values = extract_keys_from_txt(input_file_path, all_keys_values)

    # Save the output file in the root directory
    output_file_path = 'key_value_pairs.txt'
    with open(output_file_path, 'w') as file:
        for key, value in all_keys_values.items():
            file.write(f"{key}: {value}\n")


if __name__ == '__main__':
    main()
