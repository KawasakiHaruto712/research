from glob import glob
from tqdm import tqdm
import json
import os

# マージ済みのファイルかの確認
def status_extract(filepath):
    with open(filepath) as f:
        json_load = json.load(f)
    status = json_load['status']
    return status, json_load

file_cate = ['list_1', 'list_1 2', 'list_1 3', 'list_1 4', 'list_1 5', 'list_1 6', 'list_1 7']
for i in tqdm(range(len(file_cate))):
    filepath_read = '/Users/haruto-k/research/project/comments_merge/' + file_cate[i] + '/*.json'
    filepath_list = glob(filepath_read)
    for filepath in filepath_list:
        status, json_load = status_extract(filepath)
        if status == 'MERGED':
            file_name = os.path.splitext(os.path.basename(filepath))[0].replace('_comments_merge', '')
            filepath_write = '/Users/haruto-k/research/project/status_merge/' + file_cate[i] + '/' + file_name + '.json'
            with open(filepath_write, 'w') as f:
                json.dump(json_load, f, indent=4)