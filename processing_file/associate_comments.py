from glob import glob
from tqdm import tqdm
import json
import os

# タスクリストの作成
def create_task_list(filepath):
    with open(filepath) as f:
        review_file = json.load(f)
    link_ratio, request_comments, review_list = create_review_list(review_file)
    status_list = create_status_list(review_file, link_ratio, request_comments)
    return {'status_list': status_list, 'review_list': review_list}

# ステータスリストの作成
def create_status_list(review_file, link_ratio, request_comments):
    return {
        'number': str(review_file['_number']),
        'subject': str(review_file['subject']),
        'link_ratio': link_ratio,
        'number_request': len(request_comments)
    }

# レビューリストの作成
def create_review_list(review_file):
    link_ratio, request_comments, achieved_comments, unassociated_comments = associate_review_comments(review_file)
    review_list = []
    for i in range(max(len(request_comments), len(unassociated_comments))):
        review_list.append({
            'request_comment': request_comments[i]['message'] if i < len(request_comments) else '',
            'achieve_comment': achieved_comments[i] if i < len(achieved_comments) else '',
            'notlink_comment': unassociated_comments[i] if i < len(unassociated_comments) else '' 
        })
    return link_ratio, request_comments, review_list

# コメントの紐付け
def associate_review_comments(review_file):
    adjust_commentlist, request_commentlist = classify_comments(review_file['messages'])
    donelist, not_associate = [], []
    donecount = 0
    associate_check = [''] * len(adjust_commentlist)
    for request_comment in request_commentlist:
        append = False
        for i in range(len(adjust_commentlist)):
            # 修正要求と修正確認コメントの紐付け
            if adjust_commentlist[i]['_revision_number'] >= request_comment['_revision_number']: # 修正確認コメントのリビジョン数が要求より大きい
                if ('author' in request_comment and 'name' in request_comment['author']) \
                    and ('author' in adjust_commentlist[i] and 'name' in adjust_commentlist[i]['author']):
                    if adjust_commentlist[i]['author']['name'] == request_comment['author']['name']: # 同一レビューアで紐付け
                        donelist.append(adjust_commentlist[i]['message'])
                        append = True
                        donecount += 1
                        associate_check[i] = 'Already associate'
                        break
        if append == False:
            donelist.append('')
    # 紐づいていた修正確認コメントの割合計算
    link_ratio = donecount / len(request_commentlist)
    # 紐づけられなかった修正確認コメントのリスト作成
    for i in range(len(adjust_commentlist)):
        if associate_check[i] != 'Already associate':
            not_associate.append(adjust_commentlist[i]['message'])
    return link_ratio, request_commentlist, donelist, not_associate

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

def main():
    file_categories = ['list_1', 'list_2', 'list_3', 'list_4', 'list_5', 'list_6', 'list_7']
    for category in tqdm(file_categories):
        filepath_read_pattern = os.path.join('/Users/haruto-k/research/project/formatFile', category, '*.json')
        filepath_list = glob(filepath_read_pattern)
        for filepath in filepath_list:
            task_list = create_task_list(filepath)
            file_name = os.path.splitext(os.path.basename(filepath))[0]
            filepath_write = os.path.join('/Users/haruto-k/research/select_list/adjust_comments', category, file_name + '.json')
            with open(filepath_write, 'w') as f:
                json.dump(task_list, f, indent=4)

if __name__ == "__main__":
    main()