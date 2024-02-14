import json

# コメントIDを紐づけることでコメントをマージ
def merge_comments_detail(outline_file, comments_file):
    # コメント部分の読み込み
    with open(outline_file) as f:
        outline_json_load = json.load(f)
    with open(comments_file) as f:
        comments_json_load = json.load(f)
    # コメントIDの抽出
    comments_message_id = comments_id_extract(comments_json_load)
    # 詳細レビューコメントの抽出
    comments_message_detail = comments_detail_extract(comments_json_load)

    # コメントIDが一致する時、詳細コメントのマージ
    for outline_message in outline_json_load['messages']:
        for comments_id in range(len(comments_message_id)):
            if outline_message['id'] == comments_message_id[comments_id]:
                outline_message['message'] += ('\n' + comments_message_detail[comments_id])
    return outline_json_load

# 詳細レビューコメントファイルのコメントIDを抽出
def comments_id_extract(comments_message):
    comments_message_id = []
    for comments_list in comments_message.values():
        for comments_report in comments_list:
            if 'change_message_id' in comments_report:
                comments_message_id.append(comments_report['change_message_id'])
    return comments_message_id

# 詳細レビューコメントファイルのコメント詳細を抽出
def comments_detail_extract(comments_message):
    comments_message_detail = []
    for comments_list in comments_message.values():
        for comments_report in comments_list:
            if 'message' in comments_report:
                comments_message_detail.append(comments_report['message'])
    return comments_message_detail

outline_filepath_read = '/Users/haruto-k/research/project/list_1 6/12148.json'
comments_filepath_read = '/Users/haruto-k/research/project/comments/list_1 6/12148_comments.json'
merge_comments = merge_comments_detail(outline_filepath_read, comments_filepath_read)
merge_comments_write = '/Users/haruto-k/Desktop/12148_comments_merge.json'
with open(merge_comments_write, 'w') as f:
    json.dump(merge_comments, f, indent = 4)