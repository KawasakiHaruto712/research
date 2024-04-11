from glob import glob
from tqdm import tqdm
from collections import defaultdict
import json
import os

# タスクリストの作成
def create_task_list(filepath):
    with open(filepath) as f:
        review_file = json.load(f)
    request_comments, review_list = create_review_list(review_file)
    status_list = create_status_list(request_comments, review_file, review_list)
    return {'status_list': status_list, 'review_list': review_list}

# ステータスリストの作成
def create_status_list(request_comments, review_file, review_list):
    link_ratio = calculate_linkRatio(request_comments, review_file, review_list)
    return {
        'number': str(review_file['_number']),
        'subject': str(review_file['subject']),
        'link_ratio': link_ratio,
        'number_request': len(request_comments)
    }

# レビューリストの作成
def create_review_list(review_file):
    associate_comments, request_comments, achieved_comments = associate_review_comments(review_file)
    unassociated_comments = unassociated_achived_comments(associate_comments, achieved_comments)
    review_list = defaultdict(list)
    for i in range(max(len(request_comments), len(unassociated_comments))):
        review_list['link_comments'].append({
            'request_comment': request_comments[i]['message'] if i < len(request_comments) else '',
            'achieve_comment': achieved_comments[i]['message'] if i < len(achieved_comments) and isinstance(achieved_comments[i], dict) else ''
        })
        review_list['notlink_comments'].append({
            'notlink_comment': unassociated_comments[i]['message'] if i < len(unassociated_comments) else ''
        })
    return request_comments, review_list

# コメントの紐付け
def associate_review_comments(review_file):
    associate_comments, request_comments = classify_comments(review_file['messages'])
    achieved_comments = [''] * len(request_comments)
    for index, request in enumerate(request_comments):
        for associate in associate_comments:
            # 修正要求と修正確認コメントの紐付け
            if associate['_revision_number'] >= request['_revision_number']: # 修正確認コメントのリビジョン数が要求より大きい
                if ('author' in request and 'name' in request['author']) \
                and ('author' in associate and 'name' in associate['author']) \
                and (associate['author']['name'] == request['author']['name']): # 同一レビューアで紐付け
                    achieved_comments[index] = associate
    return associate_comments, request_comments, achieved_comments

# 紐づかなかった修正確認コメントの確認
def unassociated_achived_comments(associate_comments, achieved_comments):
    unassociated_comments = []
    for associate in associate_comments:
        if not any(associate['id'] == achieved['id'] for achieved in achieved_comments if achieved != ''):
            unassociated_comments.append(associate)
    return unassociated_comments

# 修正要求と修正確認コメントの分類
def classify_comments(message_list):
    adjust_comments, request_comments = [], []
    search_filepath = '/Users/haruto-k/research/project/adjust_comments.json'
    with open(search_filepath) as f:
        adjust_comments_json = json.load(f)
    for message in message_list:
        if any(adjust['comment_text'] in message['message'].lower() for adjust in adjust_comments_json):
            adjust_comments.append(message)
        else:
            request_comments.append(message)
    return adjust_comments, request_comments

# 紐づいている割合の算出
def calculate_linkRatio(request_comments, review_file, review_list):
    total_link = 0
    link_ratio = 0
    if any(review['achieve_comment'] != '' for review in review_list['link_comments']):
        total_link += 1
    if len(request_comments) != 0:
        link_ratio = total_link / len(request_comments)
    else:
        print(str(review_file['_number']) + 'は修正要求コメントがないです')
    return link_ratio

def main():
    file_categories = ['list_1', 'list_2', 'list_3', 'list_4', 'list_5', 'list_6', 'list_7']
    for category in tqdm(file_categories):
        filepath_read_pattern = os.path.join('/Users/haruto-k/research/project/formatFile', category, '*.json')
        filepath_list = glob(filepath_read_pattern)
        for filepath in filepath_list:
            task_list = create_task_list(filepath)
            file_name = os.path.splitext(os.path.basename(filepath))[0]
            filepath_write = os.path.join('/Users/haruto-k/research/select_list/adjust_comments/json/', category, file_name + '.json')
            with open(filepath_write, 'w') as f:
                json.dump(task_list, f, indent=4)

if __name__ == "__main__":
    main()