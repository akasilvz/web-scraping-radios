import pandas as pd
import logging
import re
import requests
import os
import csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_artist_name(artist_name):
    delimiters = [',', 'feat.', 'ft.', '&', ' and ']
    pattern = '|'.join(map(re.escape, delimiters))
    artist_name = re.split(pattern, artist_name, maxsplit=1, flags=re.IGNORECASE)[0]
    return re.sub(r'[^\w\s]', '', artist_name).strip()

def get_artist_nationality_wikidata(artist_name):
    try:
        wiki_api_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            'action': 'query',
            'list': 'search',
            'srsearch': artist_name,
            'format': 'json',
            'srlimit': 1,
            'redirects': 1
        }
        search_data = requests.get(wiki_api_url, params=search_params).json()

        if search_data['query']['search']:
            page_title = search_data['query']['search'][0]['title']
            page_params = {
                'action': 'query',
                'prop': 'pageprops',
                'titles': page_title,
                'format': 'json'
            }
            page_data = requests.get(wiki_api_url, params=page_params).json()
            pages = list(page_data['query']['pages'].values())

            if 'pageprops' in pages[0] and 'wikibase_item' in pages[0]['pageprops']:
                wikidata_id = pages[0]['pageprops']['wikibase_item']
                
                wikidata_api_url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
                wikidata_response = requests.get(wikidata_api_url)
                wikidata_data = wikidata_response.json()

                nationality_claims = wikidata_data['entities'][wikidata_id]['claims'].get('P27', [])
                nationalities = []

                for claim in nationality_claims:
                    country_id = claim['mainsnak']['datavalue']['value']['id']
                    country_api_url = f"https://www.wikidata.org/wiki/Special:EntityData/{country_id}.json"
                    country_data = requests.get(country_api_url).json()
                    country_name = country_data['entities'][country_id]['labels']['en']['value']
                    nationalities.append(country_name)

                if nationalities:
                    return 'Nacional' if 'Portugal' in nationalities else 'Internacional'
        return "Desconhecido"
    except Exception as e:
        logging.error(f"Erro ao consultar '{artist_name}': {e}")
        return "Desconhecido"

input_file = r'input_file_path.csv'
output_file = r'output_file_path.csv'

file_exists = os.path.isfile(output_file)

if not file_exists:
    with open(output_file, mode='w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out, delimiter='|', quoting=csv.QUOTE_NONE, escapechar='\\')
        df = pd.read_csv(input_file, delimiter='|', nrows=0)
        header = list(df.columns) + ['NATIONALITY']
        writer.writerow(header)

artist_info = {}

with open(input_file, mode='r', newline='', encoding='utf-8') as f_in, \
     open(output_file, mode='a', newline='', encoding='utf-8') as f_out:

    reader = csv.DictReader(f_in, delimiter='|')
    writer = csv.writer(f_out, delimiter='|', quoting=csv.QUOTE_NONE, escapechar='\\')

    for row in reader:
        artist_name = process_artist_name(row['SONG ARTIST'])

        if artist_name not in artist_info:
            nationality = get_artist_nationality_wikidata(artist_name)
            artist_info[artist_name] = nationality
        else:
            nationality = artist_info[artist_name]

        row_values = list(row.values()) + [nationality]
        writer.writerow(row_values)

        logging.info(f"Processado: {artist_name} - Nacionalidade: {nationality}")

        f_out.flush()

print(f"Arquivo atualizado salvo em: {output_file}")