import pandas as pd
import json
from tqdm import tqdm

def FindOwner(CheckList_df):
    owner = []
    for index, row in tqdm(CheckList_df.iterrows()):

        # ファイル番号の調査
        if 'cinder' in row['URL']:
            FileNumber = 1
        elif 'glance' in row['URL']:
            FileNumber = 2
        elif 'horizon' in row['URL']:
            FileNumber = 3
        elif 'keystone' in row['URL']:
            FileNumber = 4
        elif 'neutron' in row['URL']:
            FileNumber = 5
        elif 'nova' in row['URL']:
            FileNumber = 6
        else:
            FileNumber = 7
        jsonFile_path = '/Users/haruto-k/research/select_list/removal_bot/list_' + str(FileNumber) + '/' + str(row['PRID']) + '.json'
        with open(jsonFile_path, 'r') as f:
            jsonFile = json.load(f)
        
        # 開発者名をリストに追加
        owner.append(jsonFile['owner']['name'])
    return owner

def main():
    #チェックリストの読み込み
    Read_CheckList_path = '/Users/haruto-k/research/select_list/checkList/alradyStart/checkList.csv'
    CheckList_df = pd.read_csv(Read_CheckList_path, header=0)

    # 開発者名の追加
    owner = FindOwner(CheckList_df)
    CheckList_df.insert(loc = 6, column='owner', value=owner)

    # ownerを追加したチェックリストの書き出し
    Write_CheckList_path = '/Users/haruto-k/research/select_list/checkList/alradyStart/checkList.csv'
    CheckList_df.to_csv(Write_CheckList_path, index=False, encoding='utf_8_sig')
if __name__ == '__main__':
    main()