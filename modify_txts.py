import os
import re
import json

# Load configurations from config.json
with open('config.json', 'r') as file:
    config = json.load(file)

dir_path = config['DIRECTORY_PATH']

# Iterate through all the files in the specified directory
for filename in os.listdir(dir_path):
    # Check if the file has a .txt extension
    if filename.endswith(".txt"):
        filepath = os.path.join(dir_path, filename)
        with open(filepath, 'r', encoding='utf-8', errors='replace') as file:
            lines = file.readlines()

        # Check if the file contains the specified pattern and make the replacements
        with open(filepath, 'w', encoding='utf-8', errors='replace') as file:
            for line in lines:
                match_d = re.search(r'(.+): ([\d.]+)\.\.\.([\d.]+)(\w+)', line)
                match_awg = re.search(r'(.+): ([\w\d.]+)\.\.\.([\w\d.]+)', line)
                match_temp = re.search(r'(.+): ([+-]?\d+)\.\.\.([+-]?\d+)°C', line)

                if match_d:
                    # Extract the prefix, values before and after the dots, and the unit
                    prefix, min_value, max_value, unit = match_d.groups()

                    # Write the new lines
                    file.write(f"{prefix} minimum: {min_value} {unit}\n")
                    file.write(f"{prefix} maximum: {max_value} {unit}\n")
                elif match_awg:
                    # Extract the prefix and values before and after the dots
                    prefix, min_value, max_value = match_awg.groups()

                    # Write the new lines
                    file.write(f"{prefix} minimum: {min_value}\n")
                    file.write(f"{prefix} maximum: {max_value}\n")
                elif match_temp:
                    # Extract the prefix, values before and after the dots, and the unit
                    prefix, min_value, max_value = match_temp.groups()

                    # Write the new lines
                    file.write(f"{prefix} minimum: {min_value} Celsius\n")
                    file.write(f"{prefix} maximum: {max_value} Celsius\n")
                else:
                    # Write the original line if it doesn't contain the specified pattern
                    file.write(line)

            print(f"Modified file: {filepath}")
