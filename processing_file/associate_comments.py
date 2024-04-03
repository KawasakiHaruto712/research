from glob import glob
from tqdm import tqdm
import json
import os

# タスクリストの作成
def make_tasklist(filepath):
    with open(filepath) as f:
        review_file = json.load(f)
    link_ratio, reviewlist = make_reviewlist(review_file)
    statuslist = make_statuslist(review_file, link_ratio)
    return {'statuslist': statuslist, 'reviewlist': reviewlist}

# ステータスリストの作成
def make_statuslist(review_file, link_ratio):
    number = str(review_file['_number'])
    subject = str(review_file['subject'])
    statuslist = {
        'number': number,
        'subject': subject,
        'link_ratio': link_ratio
    }
    return statuslist

# レビューリストの作成
def make_reviewlist(review_file):
    link_ratio, request_commentlist, donelist, not_associate = associate_comments(review_file)
    reviewlist = []
    # 修正要求が紐づかなかった確認コメントより数が多かった場合
    if len(request_commentlist) >= len(not_associate):
        for i in range(len(request_commentlist)):
            if i < len(not_associate):
                reviewlist.append({
                    'request_comment': request_commentlist[i]['message'],
                    'acheive_comment': donelist[i],
                    'notlink_comment': not_associate[i]
                })
            else:
                reviewlist.append({
                    'request_comment': request_commentlist[i]['message'],
                    'acheive_comment': donelist[i],
                    'notlink_comment': '' 
                })
    # 修正要求が紐づかなった確認コメントより数が少なかった場合
    else:
        for i in range(len(not_associate)):
            if i < len(request_commentlist):
                reviewlist.append({
                    'request_comment': request_commentlist[i]['message'],
                    'acheive_comment': donelist[i],
                    'notlink_comment': not_associate[i]
                })
            else:
                reviewlist.append({
                    'request_comment': '',
                    'acheive_comment': '',
                    'notlink_comment': not_associate[i]
                })
    return link_ratio, reviewlist

# コメントの紐付け
def associate_comments(review_file):
    donelist = []
    donecount = 0
    not_associate = []
    message_list = review_file['messages']
    adjust_commentlist, request_commentlist = comment_classify(message_list)
    associate_check = [''] * len(adjust_commentlist)
    for request_comment in request_commentlist:
        append = 0
        for i in range(len(adjust_commentlist)):
            # 修正要求と修正確認コメントの紐付け
            if adjust_commentlist[i]['_revision_number'] >= request_comment['_revision_number']: # 修正確認コメントのリビジョン数が要求より大きい
                if 'author' in request_comment and 'name' in request_comment['author']:
                    if 'author' in adjust_commentlist[i] and 'name' in adjust_commentlist[i]['author']:
                        if adjust_commentlist[i]['author']['name'] == request_comment['author']['name']: # 同一レビューアで紐付け
                            donelist.append(adjust_commentlist[i]['message'])
                            append = 1
                            donecount += 1
                            associate_check[i] = 'Already associate'
                            break
                else:
                    break
                
        if append == 0:
            donelist.append('')
    # 紐づいていた修正確認コメントの割合計算
    link_ratio = (donecount / len(request_commentlist)) * 100
    # 紐づけられなかった修正確認コメントのリスト作成
    for i in range(len(adjust_commentlist)):
        if associate_check[i] != 'Already associate':
            not_associate.append(adjust_commentlist[i]['message'])
    return link_ratio, request_commentlist, donelist, not_associate

# 修正要求と修正確認コメントの分類
def comment_classify(message_list):
    adjust_commentlist = []
    request_commentlist = []
    search_filepath = '/Users/haruto-k/research/project/adjust_comments.json'
    with open(search_filepath) as f:
        adjust_comments = json.load(f)
    for message in message_list:
        append = 0
        for adjust in adjust_comments:
            if adjust['comment_text'] in message['message'].lower():
                adjust_commentlist.append(message)
                append = 1
                break
        if append == 0:
            request_commentlist.append(message)
    return adjust_commentlist, request_commentlist

file_cate = ['list_1', 'list_1 2', 'list_1 3', 'list_1 4', 'list_1 5', 'list_1 6', 'list_1 7']
for i in tqdm(range(len(file_cate))):
    filepath_read = '/Users/haruto-k/research/project/formatFile/' + file_cate[i] + '/*.json'
    filepath_list = glob(filepath_read)
    for filepath in filepath_list:
        tasklist = make_tasklist(filepath)
        file_name = os.path.splitext(os.path.basename(filepath))[0]
        filepath_write = '/Users/haruto-k/research/select_list/adjust_comments/' + file_cate[i] + '/' + file_name + '.json'
        with open(filepath_write, 'w') as f:
            json.dump(tasklist, f, indent = 4)