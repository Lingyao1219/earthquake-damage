import os
import ast
import argparse
import pandas as pd
import pickle
import requests
import hashlib
from PIL import Image
from io import BytesIO
from word_list import *
from tqdm import tqdm

tqdm.pandas()

HASHES_FILE = 'seen_hashes.pkl'

def load_seen_hashes():
    """Load the set of seen image hashes from a file."""
    try:
        with open(HASHES_FILE, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return set()
    
def save_seen_hashes(seen_hashes):
    """Save the set of seen image hashes to a file."""
    with open(HASHES_FILE, 'wb') as f:
        pickle.dump(seen_hashes, f)

seen_hashes = load_seen_hashes()


def filter_dataset(df, language):
    """Filter dataset based on language and damage words."""
    if language == 'english':
        pattern = '|'.join(r'\b{}\b'.format(word) for word in damage_words_english)
        filtered_df = df[df['text'].str.contains(pattern, case=False, na=False)]
    elif language == 'japanese':
        pattern = '|'.join(damage_words_japanese)
        filtered_df = df[df['text'].str.contains(pattern, case=False, na=False)]
    return filtered_df


def compute_image_hash(url):
    """Compute the MD5 hash of the image at the given URL."""
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        hash_md5 = hashlib.md5(image.tobytes())
        return hash_md5.hexdigest()
    except Exception as e:
        return None


def combine_urls(row, seen_hashes):
    """Combine the entity_image_url and extended_entity_image_urls into a single list."""
    # Combine image_urls into a single list
    image_urls_list = []
    image_url = row['entity_image_url']
    extended_image_urls = row['extended_entity_image_urls']
    if extended_image_urls and isinstance(extended_image_urls, str):
        extended_image_urls = ast.literal_eval(extended_image_urls)
    else:
        extended_image_urls = []
    if image_url:
        image_urls_list.append(image_url)
    if extended_image_urls:
        image_urls_list.extend(extended_image_urls)
    
    # Convert image_urls to hashes
    hash_list = [compute_image_hash(url) for url in image_urls_list]
    
    # Filter out URLs whose hash has already been seen
    unique_urls = []
    for url in image_urls_list:
        hash_value = compute_image_hash(url)
        if hash_value and hash_value not in seen_hashes:
            seen_hashes.add(hash_value)
            unique_urls.append(url)
    return image_urls_list, hash_list, unique_urls


def main(folder, language):
    read_folder = folder
    save_folder = read_folder + '_filtered'
    files = os.listdir(read_folder)
    files = sorted(files)
    files = [file for file in files if file.endswith('.json')]
    if not os.path.exists(save_folder):
        os.makedirs(save_folder, exist_ok=True)
    for file in files:
        read_filepath = os.path.join(read_folder, file)
        df = pd.read_json(read_filepath)
        df['text'] = df['text'].astype(str)
        df = df[~df['text'].str.startswith('RT @')]
        print(len(df))
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        df = df.sort_values('time')
        df1 = filter_dataset(df, language)
        df['image_urls'], df['image_hashes'], df['unique_image_urls'] = zip(*df.progress_apply(lambda row: combine_urls(row, seen_hashes), axis=1))
        df2 = df[df['unique_image_urls'].apply(lambda x: len(x) > 0)]
        save_seen_hashes(seen_hashes)
        save_file1 = file.split('.')[0] + '_text.json'
        save_file2 = file.split('.')[0] + '_image.json'
        save_filepath1 = os.path.join(save_folder, save_file1)
        save_filepath2 = os.path.join(save_folder, save_file2)
        df1.to_json(save_filepath1, orient='records', lines=True)
        df2.to_json(save_filepath2, orient='records', lines=True)
        print(f'{save_file1} and {save_file2} saved')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter dataset based on language and detect image duplicates.")
    parser.add_argument("folder", type=str, help="Path to the folder containing JSON files.")
    parser.add_argument("--language", type=str, default="english", choices=["english", "japanese"], help="Language for filtering dataset (default: english)")
    args = parser.parse_args()
    main(args.folder, args.language)