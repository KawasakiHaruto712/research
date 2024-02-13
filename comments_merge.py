from glob import glob
from tqdm import tqdm
import json
import os

# コメントIDを紐づけることでコメントをマージ
def merge_comments_detail(outline_file, comments_file):
    # コメント部分の読み込み
    with open(outline_file) as f:
        outline_json_load = json.load(f)
        outline_message_list = outline_json_load['message']
    with open(comments_file) as f:
        comments_json_load = json.load(f)
        comments_message_list = comments_json_load[*]
    # コメントIDの抽出
    outline_message_id = outline_id_extract(outline_message_list)
    comments_message_id = comments_id_extract(comments_message_list)
    # 詳細レビューコメントの抽出
    comments_message_detail = comments_detail_extract(comments_message_list)

    for comments_id in range(comments_message_id):
        if outline_message_id == comments_message_id:
            outline_json_load.append(comments_message_detail[comments_id])
    return outline_json_load

# 概要レビューコメントファイルのコメントIDを抽出
def outline_id_extract(outline_message_list):
    outline_message_id = []
    for outline_list in range(outline_message_list):
        outline_message_id.append(outline_list['message']['id'])
    return outline_message_id

# 詳細レビューコメントファイルのコメントIDを抽出
def comments_id_extract(comments_message_list):
    comments_message_id = []
    for comments_list in range(comments_message_list):
        comments_message_id.append(comments_list['change_message_id'])
    return comments_message_id

# 詳細レビューコメントファイルのコメント詳細を抽出
def comments_detail_extract(comments_message_list):
    comments_message_detail = []
    for comments_list in range(comments_message_list):
        comments_message_detail.append(comments_list['message'])
    return comments_message_detail

file_cate = ['list_1', 'list_1 2', 'list_1 3', 'list_1 4', 'list_1 5', 'list_1 6', 'list_1 7']
for i in tqdm(range(len(file_cate))):
    outline_filepath_read = '/Users/haruto-k/research/project/' + file_cate[i] + '/*.json'
    outline_filepath_list = glob(outline_filepath_read)
    # jsonファイル作成
    for outline_file in outline_filepath_list:
        # ファイル名からプロジェクトナンバー抽出
        file_name = os.path.splitext(os.path.basename(outline_file))[0]
        # コメントファイルの確認
        comments_filepath_read = '/Users/haruto-k/research/project/comments/' + file_cate[i] + '/' + file_name + '_comments.json'
        comments_file = glob(comments_filepath_read)
        # コメントをマージする関数の呼び出し
        merge_comments = merge_comments_detail([outline_file], [comments_file])
        # コメントファイル作成
        merge_comments_write = '/Users/haruto-k/research/project/comments_merge/' + file_cate[i] + '/' + file_name + '_comments_merge.json'
        with open(merge_comments_write, 'w') as f:
            json.dump(merge_comments, f, indent = 4)