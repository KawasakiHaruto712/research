import json
import pandas as pd
from glob import glob
from pathlib import Path
from tqdm import tqdm

# PRの情報を記述したファイルパスの定義
AllPRPath = '/Users/haruto-k/research/project/formatFile/*/*.json'

# 修正要求の情報を記述したディレクトリの定義
RequestDir = '/Users/haruto-k/research/select_list/RequestAssociate/'

# タスクの推移の結果を保存するディレクトリの定義
TaskTransDir = '/Users/haruto-k/research/select_list/TaskTransition/'

# チェックリストのパスと目視を行なったPRの数を記載したファイルのパスを定義
CheckListPath = '/Users/haruto-k/research/select_list/checkList/alradyStart/checkList.csv'
LablesPRNumberPath = '/Users/haruto-k/research/select_list/labeled_PRNumber.txt'

# モデル作成に利用したPRか否か確認する関数
def ModelCreatePR():

    # チェックリストの読み込み
    CheckList_df = pd.read_csv(CheckListPath, header=0)

    # ラベル付けされているPRだけを対象とする
    with open(LablesPRNumberPath) as LabeledPRNumber_txt:
        textLine = LabeledPRNumber_txt.readlines()
    LabeledPRNumber = float(textLine[0])
    CheckList_df = CheckList_df[CheckList_df['PRNumber'] <= LabeledPRNumber]

    # チェックリストの行毎のPRIDを保存
    PRIDDuplicate = []

    # ラベル済みPRの数だけループ
    for _, row in CheckList_df.iterrows():

        # 行のPRIDを保存
        PRIDDuplicate.append(row['PRID'])

    # 重複したPRIDを削除
    PRIDList = list(set(PRIDDuplicate))

    # モデル作成に利用したPRIDを保存した変数を返す
    return PRIDList

# PRの生存時間と修正要求数を抽出する関数
def TimeAndReqExt(ModelPRID_list):

    # プルリクエスト情報と修正要求の情報を保存する変数の初期化
    PRTimeReqNum_list = []

    # PRの数だけループ
    for PRPath in tqdm(glob(AllPRPath)):

        # モデルに利用したPRか確認
        if Path(PRPath).stem in ModelPRID_list:
            continue

        # 修正要求のパスの定義
        RequestPath = RequestDir + Path(PRPath).parent.name + '/' + Path(PRPath).stem + '.csv'

        # 修正要求のcsvファイルのヘッダーを取得
        with open(RequestPath, 'r', encoding='utf-8_sig') as ReqFile:
            HeaderLine = ReqFile.readline().strip()

        # 修正要求の数を保存する変数を初期化
        ReqNum = 0

        # ヘッダーが存在するか確認(空のcsvファイルでないか確認)
        if HeaderLine:
            
            # 修正要求の情報が記述されたファイルの読み込み
            RequestData_df = pd.read_csv(RequestPath, header=0)

            # 修正要求の数(行数)の取得
            ReqNum = RequestData_df.shape[0]
        
        # PRの情報が記述されたjsonファイルの読み込み
        # PRの情報が記載のファイルの読み込み
        with open(PRPath, 'r') as PR_F:
            PRData_df = json.load(PR_F)

        # プルリクエスト情報と修正要求の情報を保存
        PRTimeReqNum_list.append({
            'Project': PRData_df['project'].replace('openstack/','').capitalize(),
            'PRID':  Path(PRPath).stem,
            'CreateTime': PRData_df['created'],
            'MergeTime': PRData_df['updated'],
            'RequestNum': ReqNum
        })
    
    # プルリクエスト情報と修正要求の情報を返す
    return pd.DataFrame(PRTimeReqNum_list)

# メイン処理
def main():

    # モデル作成に利用したPRを抽出する関数の呼び出し
    ModelPRID_list = ModelCreatePR()

    # PRの生存時間と修正要求数を抽出する関数を呼び出し
    PRTimeReqNum_df = TimeAndReqExt(ModelPRID_list)

    # PRの生存時間と修正要求数の結果をcsvファイルに保存
    PRTimeReqNum_df.to_csv((TaskTransDir + 'PRTimeReqNum.csv'), index=False, encoding='utf_8_sig')

if __name__ == '__main__':
    main()