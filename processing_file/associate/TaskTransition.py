import itertools
import json
import pandas as pd
from glob import glob
from pathlib import Path
from tqdm import tqdm

# チェックリストのパスと目視を行なったPRの数を記載したファイルのパスを定義
CheckListPath = '/Users/haruto-k/research/select_list/checkList/alradyStart/checkList.csv'
LablesPRNumberPath = '/Users/haruto-k/research/select_list/labeled_PRNumber.txt'

# 修正要求の情報が記述されたファイルのパスの定義
AllRequestPath = '/Users/haruto-k/research/select_list/RequestAssociate/*/*.csv'

# PRの情報が記述されたファイルのパスとディレクトリの定義
AllPRPath = '/Users/haruto-k/research/project/formatFile/*/*.json'
AllPRDirectory = '/Users/haruto-k/research/project/formatFile/'

# タスクの推移の結果を保存するディレクトリの定義
TaskTransPath = '/Users/haruto-k/research/select_list/TaskTransition/'

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

# 抽出した修正要求のの時間情報を抽出する関数
def ExtractTask(ReqPath, AssociData_df):

    ReqTaskData = []

    # 紐づけたファイルを行ごとにループ
    for _, row in AssociData_df.iterrows():

        # 修正要求のPR情報が記述されたファイルのパスの定義
        PRPath = AllPRDirectory + Path(ReqPath).parent.name + '/' + Path(ReqPath).stem + '.json'

        # PRの情報が記載のファイルの読み込み
        with open(PRPath, 'r') as PR_F:
            PRData = json.load(PR_F)

        # 基本的には導入された時間をタスク達成時間に設定
        AchiTime = PRData['updated']

        # 修正確認と紐づいている場合に処理を行う
        if pd.notna(row['検証者は問わずリビジョン更新後にコメント']):

            # 紐づいた修正確認のコメントIDを抽出
            AchiComIDList = row['検証者は問わずリビジョン更新後にコメント'].split(', ')

            # 紐づいたコメント修正確認コメントの提出時間を保存する変数の初期化
            AchiComTime = []

            #　紐づいたコメントの数だけループ
            for AchiComID in AchiComIDList:

                # RPに含まれるコメントの数だけループ
                for message in PRData['messages']:

                    # コメントIDが一致するか確認
                    if message['id'] == AchiComID:

                        # 紐づいた修正確認コメント提出時間を保存
                        AchiComTime.append(message['date'])
            
            # 修正要求が紐づいている場合はタスク達成時間を更新
            AchiTime = min(AchiComTime)
        
        # 修正要求の時間情報関連を変数に保存
        ReqTaskData.append({
            'Projcet': PRData['project'].replace('openstack/','').capitalize(),
            'PRID': Path(ReqPath).stem,
            'CommentID': row['CommentID'],
            'RequestTime': row['Date'],
            'AchieveTime': AchiTime
        })
    
    # 修正要求の時間情報関連を保存した変数を返す
    return ReqTaskData       

# 修正要求のタスク推移を抽出する関数
def ReqTaskTransExt(ModelPRID):

    # 修正要求提出時間と完了時間を保存する変数の初期化
    ReqTrans_twolist = []

    # データセットのPRの数だけループ
    for ReqPath in tqdm(glob(AllRequestPath)):

        # csvファイルが空の場合に処理をスキップ
        with open(ReqPath, 'r', encoding='utf-8_sig') as ReqFile:
            HeaderLine = ReqFile.readline().strip()
        if not HeaderLine:
            continue

        # モデル作成に利用したPRか確認
        if str(Path(ReqPath).stem) == str(ModelPRID):
            continue

        # 紐づけたcsvファイルの読み込み
        AssociData_df = pd.read_csv(ReqPath, header=0)

        # 抽出した修正い要求の時間情報を抽出する関数の呼び出し
        ReqTrans_twolist.append(ExtractTask(ReqPath, AssociData_df))

    # リストの次元を一つ落とす
    ReqTrans_list = list(itertools.chain.from_iterable(ReqTrans_twolist))

    # 修正要求の時間情報を保存した変数を返す
    return pd.DataFrame(ReqTrans_list)

# PRのタスク推移を抽出する関数
def PRTaskTransExt(ModelPRID):

    # PR提出時間と導入時間を保存する変数の初期化
    PRTrans_list = []

    # データセットのPRの数だけループ
    for PRPath in tqdm(glob(AllPRPath)):

        # モデル作成に利用したPRか確認
        if str(Path(PRPath).stem) == str(ModelPRID):
            continue

        # PRの情報が記載のファイルの読み込み
        with open(PRPath, 'r') as PR_F:
            PRData = json.load(PR_F)
        
        # PR提出時間と導入時間の保存(他の情報も最低限追加)
        PRTrans_list.append({
            'Project': PRData['project'].replace('openstack/','').capitalize(),
            'PRID': Path(PRPath).stem,
            'CreateTime': PRData['created'],
            'MergeTime': PRData['updated']
        })

    # PRの時間情報を保存した変数を返す
    return pd.DataFrame(PRTrans_list)

# メイン処理
def main():

    # モデル作成に利用したPRを抽出する関数の呼び出し
    ModelPRID = ModelCreatePR()

    # 修正要求のタスク推移を抽出する関数の呼び出し
    ReqTrans_df = ReqTaskTransExt(ModelPRID)

    # PRのタスク推移を抽出する関数の呼び出し
    PRTrans_df = PRTaskTransExt(ModelPRID)

    # タスクの時間情報を記述した結果をcsvファイルに保存
    ReqTrans_df.to_csv((TaskTransPath + 'RequestTask.csv'), index=False, encoding='utf_8_sig')
    PRTrans_df.to_csv((TaskTransPath + 'PRTask.csv'), index=False, encoding='utf_8_sig')

if __name__ == '__main__':
    main()