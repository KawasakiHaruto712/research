from glob import glob
from tqdm import tqdm
import pandas as pd
import json
import os

def extract_comments(filepath):
    with open(filepath, 'r') as file:
        review_file = json.load(file)

    review_extract = []
    for index, message in enumerate(review_file['messages']):
        review_extract.append({
            "comments_number": (index + 1),
            "revision": message['_revision_number'],
            "name": message.get('author', {}).get('name', ''),
            "comment": message['message']
        })
    extract_commentsList = pd.DataFrame(review_extract)
    return extract_commentsList

def main():
    file_categories = ['list_1', 'list_2', 'list_3', 'list_4', 'list_5', 'list_6', 'list_7']
    for category in tqdm(file_categories):
        filepath_read_pattern = os.path.join('/Users/haruto-k/research/project/formatFile', category, '*.json')
        filepath_list = glob(filepath_read_pattern)
        for filepath in filepath_list:
            extract_commentsList = extract_comments(filepath)
            file_name = os.path.splitext(os.path.basename(filepath))[0]
            filepath_write = os.path.join('/Users/haruto-k/research/select_list/extract_comments/', category, file_name + '.csv')
            extract_commentsList.to_csv(filepath_write, index=False)

if __name__ == "__main__":
    main()