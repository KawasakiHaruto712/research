import pandas as pd
from glob import glob
from pathlib import Path
from tqdm import tqdm

# 紐づけたファイルのパスを定義
RequestAssociatePath = '/Users/haruto-k/research/select_list/RequestAssociate/*/*.csv'

# 紐づいた合計数と割合の結果を出力するパスを定義
DefiPerResultPath = '/Users/haruto-k/research/select_list/adjust_comments/DefinitionPercentage.csv'

# チェックリストのパスと目視を行なったPRの数を記載したファイルのパスを定義
CheckListPath = '/Users/haruto-k/research/select_list/checkList/alradyStart/checkList.csv'
LablesPRNumberPath = '/Users/haruto-k/research/select_list/labeled_PRNumber.txt'

# 修正要求の数と紐づいたコメントの数を抽出する関数
def Extract_ReqAchi(PRPath, PRIDList):

    # 抽出した修正要求の数と紐づいたコメントの数を保存する変数の初期化
    ReqNum = 0
    SameRevAchiNum = 0
    RegarRevAchiNum = 0

    # ファイルのヘッダーを確認
    with open(PRPath, 'r', encoding='utf-8_sig') as PRFile:
        HeaderLine = PRFile.readline().strip()

    # ヘッダーが存在しない(csvファイルが空)場合に修正要求及び紐づいた数を0として返す
    if not HeaderLine:
        return ReqNum, SameRevAchiNum, RegarRevAchiNum
    
    # モデル作成に利用したPRの数分ループ
    for PRid in PRIDList:

        # モデル作成に利用したPRか確認
        if str(Path(PRPath).stem) == str(PRid):
            return ReqNum, SameRevAchiNum, RegarRevAchiNum

    # 紐づけたcsvファイルの読み込み
    AssociateData_df = pd.read_csv(PRPath, header=0)

    # 紐づけたファイルを行ごとにループ
    for _, row in AssociateData_df.iterrows():

        # 修正要求が存在する場合にカウント
        if pd.notna(row['Comment']):
            ReqNum += 1
        
        # 同一検証者によるコメントが紐づいている場合にカウント
        if pd.notna(row['同一検証者かつリビジョン更新後にコメント']):
            SameRevAchiNum += 1

        # 検証者問わず紐づいている場合にカウント
        if pd.notna(row['検証者は問わずリビジョン更新後にコメント']):
            RegarRevAchiNum += 1
    
    return ReqNum, SameRevAchiNum, RegarRevAchiNum

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

# メイン処理
def main():

    # 紐づけたファイルのパスを格納
    RequestAssociatePathList = glob(RequestAssociatePath)

    # モデル作成に利用したPRIDを抽出する関数の呼び出し
    PRIDList = ModelCreatePR()

    # 修正要求と紐づいたコメントの総量を保存する変数の初期化
    ReqSum = 0
    SameRevAchiSum = 0
    RegardRevAchiSum = 0

    # PR毎にループ
    for PRPath in tqdm(RequestAssociatePathList):

        # 修正要求の数と紐づいた紐づいたコメントの数を抽出する関数の呼び出し
        ReqNum, SameRevAchiNum, RegardRevAchiNum = Extract_ReqAchi(PRPath, PRIDList)

        # PRに含まれた修正要求の数と紐づいたコメントの数だけ増やす
        ReqSum += ReqNum
        SameRevAchiSum += SameRevAchiNum
        RegardRevAchiSum += RegardRevAchiNum

    # 結果に記載する内容を変数に保存
    ResultNum = [{
        '修正要求合計数': ReqSum,
        '同一検証者がリビジョン更新後に修正確認をした合計数': SameRevAchiSum,
        '同一検証者がリビジョン更新後に修正確認をした割合': SameRevAchiSum / ReqSum,
        '検証者は問わずリビジョン更新後に修正確認をした合計数': RegardRevAchiSum,
        '検証者は問わずリビジョン更新後に修正確認をした割合': RegardRevAchiSum / ReqSum
    }]

    # 紐づいた合計数と割合の結果の出力
    ResultNum_df = pd.DataFrame(ResultNum)
    ResultNum_df.to_csv(DefiPerResultPath, index=False, encoding='utf_8_sig')

if __name__ == '__main__':
    main()