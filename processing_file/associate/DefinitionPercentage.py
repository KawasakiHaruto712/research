import pandas as pd
from glob import glob
from tqdm import tqdm

# 紐づけたファイルのパスを定義
RequestAssociatePath = '/Users/haruto-k/research/select_list/RequestAssociate/*/*.csv'

# 紐づいた合計数と割合の結果を出力するパスを定義
DefiPerResultPath = '/Users/haruto-k/research/select_list/adjust_comments/DefinitionPercentage.csv'

# 修正要求の数と紐づいた湖面の数を抽出する関数
def Extract_ReqAchi(PRPath):

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

    # 紐づけたcsvファイルの読み込み
    AssociateData_df = pd.read_csv(PRPath, header=0)

    # 紐づけたファイルを行とにループ
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


# メイン処理
def main():

    # 紐づけたファイルのパスを格納
    RequestAssociatePathList = glob(RequestAssociatePath)

    # 修正要求と紐づいたコメントの総量を保存する変数の初期化
    ReqSum = 0
    SameRevAchiSum = 0
    RegardRevAchiSum = 0

    # PR毎にループ
    for PRPath in tqdm(RequestAssociatePathList):

        # 修正要求の数と紐づいた紐づいたコメントの数を抽出する関数の呼び出し
        ReqNum, SameRevAchiNum, RegardRevAchiNum = Extract_ReqAchi(PRPath)

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