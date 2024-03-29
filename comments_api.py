from glob import glob
from tqdm import tqdm
import requests
import json
import os
import time


# APIからデータを取得する関数
def get_comments_from_gerrit(url):
    response = requests.get(url)
    # Gerritの応答からセキュリティプレフィックスを取り除く
    content = response.text[4:]
    # JSONデータとして解析
    data = json.loads(content)
    return data

file_cate = ['list_1', 'list_1 2', 'list_1 3', 'list_1 4', 'list_1 5', 'list_1 6', 'list_1 7']
for i in tqdm(range(len(file_cate))):
    filepath_read = '/work/research/project/' + file_cate[i] + '/*.json'
    filepath_list = glob(filepath_read)
    # jsonファイル作成
    for filepath in filepath_list:
        time.sleep(1)
        #ファイル名からプロフジェクトナンバー抽出
        file_name = os.path.splitext(os.path.basename(filepath))[0]
        # コメントデータの取得
        url = 'https://review.openstack.org/changes/' + file_name + '/comments'
        comments = get_comments_from_gerrit(url)
        # コメントファイル作成
        filepath_write = '/work/research/project/comments/' + file_cate[i] + '/' + file_name + '_comments.json'
        with open(filepath_write, 'w') as f:
            json.dump(comments, f, indent = 4)