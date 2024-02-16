import requests
import os
import json
from bs4 import BeautifulSoup


def get_tme_catalogues_from_config(config_path="config.json"):
    with open(config_path, 'r') as f:
        config_data = json.load(f)

    return config_data.get("TME_CATALOGUES", [])


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
CATALOGUE_PATH_FORMAT = 'https://www.tme.eu/en/katalog/{catalogue}/?page={page}'
CATALOGUES = get_tme_catalogues_from_config(config_path="config.json")
category_dir = 'category/tme'


def get_os_name():
    if os.name == 'posix':
        system_info = os.uname()
        if system_info.sysname == 'Linux':
            return 'Linux'
        elif system_info.sysname == 'Darwin':
            return 'macOS'
        else:
            return 'Unknown POSIX System'
    elif os.name == 'nt':
        return 'Windows'
    else:
        return 'Unknown OS'


def get_user_agent():
    os_name = get_os_name()

    if os_name == 'Linux':
        return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    elif os_name == 'macOS':
        return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    elif os_name == 'Windows':
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'


def get_urls(catalogue, page_number):
    urls = []

    for i in range(1, page_number):
        urls.append(CATALOGUE_PATH_FORMAT.format(catalogue=catalogue, page=i))

    return urls


def extract_categories(catalogues, output_dir):
    result_dict = {}

    # Load existing data from JSON file
    try:
        with open(output_dir + '/category_tree.json', 'r') as f:
            result_dict = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    for catalogue in catalogues:
        url_c = CATALOGUE_PATH_FORMAT.format(catalogue=catalogue, page=0)
        response_c = requests.get(url_c, headers=header)

        if response_c.status_code == 200:
            content = BeautifulSoup(response_c.content, 'html.parser')
            total_page_number = int(content.find('span', class_='o-pagination-bar__pages-total-number').text)

            url_list = get_urls(catalogue, total_page_number)

            for url in url_list:
                response_page_c = requests.get(url, headers=header)
                p_content = BeautifulSoup(response_page_c.content, 'html.parser')

                # Find all the main breadcrumb <li> elements
                li_elements = p_content.select(
                    ".c-breadcrumbs__list-item:not(.c-breadcrumbs__list-item--sublist) > a.c-breadcrumbs__link")

                # Extract the text from these <a> tags and filter out "Main page" and "Catalogue"
                a_texts = [a_tag.text.strip() for a_tag in li_elements if
                           a_tag.text.strip() not in ["Main page", "Catalogue"]]

                h4_tags = p_content.find_all('h4', class_='c-product-symbol__symbol')

                for h4_tag in h4_tags:
                    a_tags = h4_tag.find_all('a')

                    for a_tag in a_tags:
                        m_part_number_str = a_tag.text.strip()

                        # Check if the entry already exists
                        if m_part_number_str not in result_dict:
                            # Add to result_dict
                            result_dict[m_part_number_str] = a_texts

                            # Save the result_dict to a JSON file
                            with open(output_dir + '/category_tree.json', 'w') as f:
                                json.dump(result_dict, f, indent=4)
        else:
            print("Failed to fetch the page. Error code:", response_c.status_code)


def main():
    headers = {'User-Agent': get_user_agent()}
    print(headers)

    extract_categories(CATALOGUES, category_dir)


if __name__ == '__main__':
    main()
