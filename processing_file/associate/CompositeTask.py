import json
import pandas as pd
from tqdm import tqdm

# 修正要求タスクを記述したファイルパスの定義
RequestTaskPath = '/Users/haruto-k/research/select_list/TaskTransition/RequestTask.csv'

# Formatファイルが保存されたディレクトリの定義
FormatDir = '/Users/haruto-k/research/project/formatFile/'

# タスクの推移の結果を保存するディレクトリの定義
TaskTransDir = '/Users/haruto-k/research/select_list/TaskTransition/'

# プロジェクト名とPRIDからPRのデータを参照する関数
def PRDataExtract(Project, PRID):

    # フォルダ番号の初期化(Swiftプロジェクトの7番で初期化)
    FolderNum = 7

    # フォルダ名を抽出する
    if Project == 'Cinder':
        FolderNum = 1
    elif Project == 'Glance':
        FolderNum = 2
    elif Project == 'Horizon':
        FolderNum = 3
    elif Project == 'Keystone':
        FolderNum = 4
    elif Project == 'Neutron':
        FolderNum = 5
    elif Project == 'Nova':
        FolderNum = 6
    
    # PRの情報が記述されたファイルのパスの定義
    FormatFilePath = FormatDir + 'list_' + str(FolderNum) + '/' + str(PRID) + '.json'

    # PRの情報が記述されたのファイルの読み込み
    with open(FormatFilePath, 'r') as PR_F:
        PRData = json.load(PR_F)

    # PRの情報を返す
    return PRData

# 修正要求とPRの時間情報をマージする関数
def ReqAndPRTimeMerge():

    # タスクの複合時間情報を保存する変数の初期化
    CompositeTask_list = []

    # 修正要求の時間情報を記述したcsvファイルの読み込み
    Request_df = pd.read_csv(RequestTaskPath, header=0)

    # 修正要求の数だけループ
    for _, RequestRow in tqdm(Request_df.iterrows()):

        # プロジェクト名とPRIDからPRの情報を参照する関数の呼び出し
        PRData = PRDataExtract(RequestRow['Projcet'], RequestRow['PRID'])

        # タスクの複合時間情報を保存
        CompositeTask_list.append({
            'Project': RequestRow['Projcet'],
            'PRID': RequestRow['PRID'],
            'CommentID': RequestRow['CommentID'],
            'RequestTime': RequestRow['RequestTime'],
            'AchieveTime': RequestRow['AchieveTime'],
            'CreateTime': PRData['created'],
            'MergeTime': PRData['updated']
        })
    
    # タスクの複合時間情報を保存した変数を返す
    return pd.DataFrame(CompositeTask_list)

# メイン処理
def main():

    # 修正要求とPRの時間情報をマージする関数の呼び出し
    CompositeTask_df = ReqAndPRTimeMerge()

    # タスクの複合時間情報を記述した結果をcsvファイルに保存
    CompositeTask_df.to_csv((TaskTransDir + 'CompositeTask.csv'), index=False, encoding='utf_8_sig')

if __name__ == '__main__':
    main()