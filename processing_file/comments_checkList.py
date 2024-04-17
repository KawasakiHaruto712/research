from glob import glob
from tqdm import tqdm
import pandas as pd
import random
import json

def create_checkList(filePath):

    checkList = []
    commentsNumber = 1

    # チェックリストの作成
    for index, file in tqdm(enumerate(filePath)):

        # ファイルの読み込み
        with open(file, 'r') as f:
            reviewFile = json.load(f)
        
        for messages in reviewFile['messages']:
            checkList.append({
                'commentsNumber': commentsNumber,
                'PRNumber': (index + 1),
                'PRID': reviewFile['_number'],
                'subject': reviewFile['subject'],
                'URL': ('https://review.opendev.org/c/' + str(reviewFile['project']) + '/+/' + str(reviewFile['_number'])),
                'revision': messages['_revision_number'],
                'author': messages.get('author', {}).get('name', ''),
                'comment': messages['message']
            })
            commentsNumber += 1
    checkList_df = pd.DataFrame(checkList)
    return checkList_df

def main():

    # ファイルパスの読み取り，チェックリストの作成
    filePath_read = '/Users/haruto-k/research/project/formatFile/*/*.json'
    filePath_list = glob(filePath_read)
    filePath = filePath_list[:1000]
    random.shuffle(filePath)
    checkList_df = create_checkList(filePath)

    # チェックリストの書き込み
    filePath_write = '/Users/haruto-k/research/select_list/checkList.csv'
    checkList_df.to_csv(filePath_write, index = False)

if __name__ == "__main__":
    main()