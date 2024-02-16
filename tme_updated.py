import requests
import common as common
import os
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_tme_catalogues_from_config(config_path="config.json"):
    with open(config_path, 'r') as f:
        config_data = json.load(f)

    return config_data.get("TME_CATALOGUES", [])

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

CATALOGUE_PATH_FORMAT = 'https://www.tme.eu/en/katalog/{catalogue}/?page={page}'

CATALOGUES = get_tme_catalogues_from_config(config_path="config.json")

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

def extract_catalogues(catalogues, output_dir):
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

                h4_tags = p_content.find_all('h4', class_='c-product-symbol__symbol')

                for h4_tag in h4_tags:
                    a_tags = h4_tag.find_all('a')

                    for a_tag in a_tags:
                        m_part_number_str = a_tag.text.strip()
                        sanitized_part_number = m_part_number_str.replace('/', '_')
                        filename = sanitized_part_number + '.txt'
                        file_path = os.path.join(output_dir, filename)
                        file = open(file_path, 'w', encoding='utf-8')

                        file.write(m_part_number_str + '\n')

                        url_d = urljoin('https://www.tme.eu', a_tag['href'])
                        print(url_d)

                        response_d = requests.get(url_d, headers=header)

                        if response_d.status_code == 200:
                            content_s = BeautifulSoup(response_d.content, 'html.parser')
                            rows = content_s.find_all('tr', class_='c-pip__specification-row')

                            for row in rows:
                                param_name = row.find('span', class_='c-pip__specification-param-name').text.strip()
                                param_value = row.find('span', class_='c-pip__specification-parameter-value').text.strip()

                                file.write(f'{param_name}: {param_value}' + '\n')

                            file.close()
                        else:
                            print("Failed to fetch the page. Error code:", response_d.status_code)
        else:
            print("Failed to fetch the page. Error code:", response_c.status_code)

def main():
    headers = {'User-Agent': get_user_agent()}
    print(headers)

    config = common.read_json('config.json')
    mpn_dir = os.path.join(os.path.abspath('.'), config['TXT_DIR'])
    tme_dir = os.path.join(mpn_dir, config['TME_DIR'])

    if not os.path.isdir(mpn_dir):
        os.mkdir(mpn_dir)

    if not os.path.isdir(tme_dir):
        os.mkdir(tme_dir)

    extract_catalogues(CATALOGUES, tme_dir)

if __name__ == '__main__':
    main()
