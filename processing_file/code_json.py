from glob import glob
from tqdm import tqdm
import json
import os

def get_status_list(filepath_list):
    status_list = dict()
    review_list = []
    for filepath in filepath_list:
        with open(filepath) as f:
            json_load = json.load(f)
        number = str(json_load['_number'])
        subject = str(json_load['subject'])
        status = str(json_load['status'])
        message_list = json_load['messages']
        revs = max_revision_number(message_list)
        review_count = review_comment_count(message_list)
        review_revs = review_revision_number(message_list)
        reviewer_name = review_author_name(message_list)
        review_label = label_with_message(message_list)
        review_message = review_comment_message(message_list, review_revs)
        review_delete = unnecessary_review_delete(message_list, review_revs)
        status_list = {
            "number": number,
            "subject": subject,
            "status": status,
            "final revision": revs,
            "number of review comment": review_count
        }
        reviw_num_accurate = 0
        for i in range(len(review_revs)):
            if review_delete[i] != 1:
                review_list.append({
                    "review_number": reviw_num_accurate + 1,
                    "revision": review_revs[i],
                    "reviewer": reviewer_name[i],
                    "Code-Review_label": review_label[0][i],
                    "Verified_label": review_label[1][i],
                    "Review-Priority_label": review_label[2][i],
                    "Workflow-label": review_label[3][i],
                    "comment": review_message[i]
                })
                reviw_num_accurate += 1
    return {"status_list": status_list, "review_list": review_list}
        
### 最大のリビジョン数
def max_revision_number(message_list):
    revision = 1
    for msg in message_list:
        if revision < msg['_revision_number']:
            revision = msg['_revision_number']
    return revision

### レビューコメント数
def review_comment_count(message_list):
    count = 0
    for msg in message_list:
        if any(['Code-Review+2' in msg['message'], 'Code-Review+1' in msg['message'],
                'Code-Review-1' in msg['message'], 'Code-Review-2' in msg['message'],
                'Verified+2' in msg['message'], 'Verified+1' in msg['message'],
                'Verified-1' in msg['message'], 'Verified-2' in msg['message'],
                'Review-Priority+2' in msg['message'], 'Review-Priority+1' in msg['message'],
                'Review-Priority-1' in msg['message'], 'Review-Priority-2' in msg['message'],
                'Workflow+2' in msg['message'], 'Workflow+1' in msg['message'],
                'Workflow-1' in msg['message'], 'Workflow-2' in msg['message']]):
            count += 1
        elif any(['-Code-Review' in msg['message'], '-Verified' in msg['message'],
                 '-Review-Priority' in msg['message'], '-Workflow' in msg['message']]):
            count -= 1
    return count

### リビジョン番号
def review_revision_number(message_list):
    review_revs = []
    for msg in message_list:
        review_revs.append(msg['_revision_number'])
    return review_revs

### レビューア名
def review_author_name(message_list):
    name = []
    for msg in message_list:
        if (('author' not in msg) or ('name' not in msg['author'])):
            name.append('Unknown')
        else:
            name.append(msg['author']['name'])
    return name

### レビューコメント内容
def review_comment_message(message_list, review_revs):
    review_message = []
    label_cate = ['Code-Review', 'Verified', 'Review-Priority', 'Workflow']
    label_point = ['+2', '+1', '-1', '-2']
    count = 0
    for msg in message_list:
        # リビジョン番号を削除
        before_message = msg['message']
        patch_set_delete = 'Patch Set ' + str(review_revs[count]) + ':'
        before_message = before_message.replace(patch_set_delete, '')
        
        # レビューラベルを削除
        for cate in range(4):
            for point in range(4):
                label_delete = str(label_cate[cate]) + str(label_point[point])
                before_message = before_message.replace(label_delete, '')

        # 最初の文字が改行や空白であった際に削除
        while True:
            if len(before_message) >= 2 and before_message[0] == '\n':
                before_message = before_message[2:]
            elif len(before_message) >= 1 and before_message[0] == ' ':
                before_message = before_message[1:]
            else:
                break

        review_message.append(before_message)
        count += 1
    return review_message

### レビューラベル
def label_with_message(message_list):
    code_review = []
    verified = []
    review_priority = []
    workflow = []
    for msg in message_list:
        # Code-Reviewラベルの検出
        if 'Code-Review+2' in msg['message']:
            code_review.append(2)
        elif ('Code-Review+1' in msg['message']):
            code_review.append(1)
        elif ('Code-Review-1' in msg['message']):
            code_review.append(-1)
        elif ('Code-Review-2' in msg['message']):
            code_review.append(-2)
        else:
            code_review.append("")

        # Verifiedラベルの検出
        if ('Verified+2' in msg['message']):
            verified.append(2)
        elif ('Verified+1' in msg['message']):
            verified.append(1)
        elif ('Verified-1' in msg['message']):
            verified.append(-1)
        elif ('Verified-2' in msg['message']):
            verified.append(-2)
        else:
            verified.append("")
        
        # Review-Priorityラベルの検出
        if ('Review-Priority+2' in msg['message']):
            review_priority.append(2)
        elif ('Review-Priority+1' in msg['message']):
            review_priority.append(1)
        elif ('Review-Priority-1' in msg['message']):
            review_priority.append(-1)
        elif ('Review-Priority-2' in msg['message']):
            review_priority.append(-2)
        else:
            review_priority.append("")

        # Workflowラベルの検出
        if ('Workflow+2' in msg['message']):
            workflow.append(2)
        elif ('Workflow+1' in msg['message']):
            workflow.append(1)
        elif ('Workflow-1' in msg['message']):
            workflow.append(-1)
        elif ('Workflow-2' in msg['message']):
            workflow.append(-2)
        else:
            workflow.append("")
    return [code_review, verified, review_priority, workflow]

### 削除するレビューの行番号を検索
def unnecessary_review_delete(message_list, review_revs):
    delete_message = [0] * len(message_list)
    count = 0
    for msg in message_list:

        default_message = msg['message']
        # アップロードしたというメッセージが入っていないか確認
        patch_upload_message = 'Uploaded patch set ' + str(review_revs[count])
        if (patch_upload_message in default_message):
            delete_message[count] = 1
        '''
        # マージ成功したというメッセージが入っていないか確認
        merge_success_message = 'Change has been successfully merged'
        if (merge_success_message in default_message):
            delete_message[count] = 1
        # Change has been successfully merged into the git repository. のやつもあるのでこっちのほうがいい(例：6806)？

        #マージ失敗したというメッセージが入っていないか確認
        merge_fail_message = 'Merge Failed.'
        if (merge_fail_message in default_message):
            delete_message[count] = 1
        # マージの失敗は Merge Failed. でいいのか？
        '''
        count += 1 
    return delete_message

project = 'Swift'


file_cate = ['list_1', 'list_1 2', 'list_1 3', 'list_1 4', 'list_1 5', 'list_1 6', 'list_1 7']
for i in tqdm(range(len(file_cate))):
    # ここは任意のパス
    filepath_read = '/Users/haruto-k/research/project/comments_merge/' + file_cate[i] +'/*.json'
    filepath_list = glob(filepath_read)
    # print(revs_list) #ターミナルに表示したい場合はこの行のコメントアウトを外す
    # jsonファイル作成
    for filepath in tqdm(filepath_list):
        revs_list = get_status_list([filepath])
        file_name = os.path.splitext(os.path.basename(filepath))[0]
        filepath_write = './select_list/json_file/' + file_cate[i] + '/' + file_name + '_list.json'
        with open(filepath_write, 'w') as f:
            json.dump(revs_list, f, indent = 4)

            
'''
# テスト用の1ファイル実行コマンド
# ここは任意のパス
filepath_list = glob(f'/Users/haruto-k/research/project/list_1/6806.json')
revs_list = get_status_list(filepath_list)
# print(revs_list) #ターミナルに表示したい場合はこの行のコメントアウトを外す
# jsonファイル作成
with open('./select_list/json_file/list_1/6806_list.json', 'w') as f:
    json.dump(revs_list, f, indent = 4)
'''