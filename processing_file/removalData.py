from glob import glob
from tqdm import tqdm
import json
import os

def removal_file(filepath):
    removal = 0
    with open(filepath) as f:
        json_load = json.load(f)

    # 除去ファイルの確認
    if json_load['status'] != 'MERGED': # マージ済みであるか
        removal = 1
    elif not json_load['messages']: # コメントがなされているか
        removal = 1
    '''
    elif sandwich_message(json_load['messages']): # リビジョン更新の前後にコメントがなされているか
        removal = 1
    '''

    return removal, json_load

def sandwich_message(message_list):
    revision = []
    for msg in message_list:
        revision.append(msg['_revision_number'])
    return len(set(revision)) == 1 # 同一のリビジョンでのみコメントがなされているか 

file_cate = ['list_1', 'list_1 2', 'list_1 3', 'list_1 4', 'list_1 5', 'list_1 6', 'list_1 7']
for i in tqdm(range(len(file_cate))):
    filepath_read = '/Users/haruto-k/research/project/comments_merge/' + file_cate[i] + '/*.json'
    filepath_list = glob(filepath_read)
    for filepath in filepath_list:
        removal, json_load = removal_file(filepath)
        if removal != 1:
            file_name = os.path.splitext(os.path.basename(filepath))[0].replace('_comments_merge', '')
            filepath_write = '/Users/haruto-k/research/project/formatFile/' + file_cate[i] + '/' + file_name + '.json'
            with open(filepath_write, 'w') as f:
                json.dump(json_load, f, indent=4)