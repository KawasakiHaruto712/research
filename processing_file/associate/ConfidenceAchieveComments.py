import pandas as pd
import json
from tqdm import tqdm

# 修正確認コメントの信頼度の計算
def ConfidenceCaluculation():

    # チェックリストの読み込み
    Read_CheckList_path = '/Users/haruto-k/research/select_list/chekList/alradyStart/checkList.csv'
    CheckList_df = pd.read_csv(Read_CheckList_path, header=0)

    # ラベル付けされているPRだけを対象とする
    with open('/work/research/processing_file/select_list/labeled_PRNumber.txt') as LabeledPRNumber_txt:
        textLine = LabeledPRNumber_txt.readlines()
    labeled_PRNumber = float(textLine[0])
    LabeledCheckList_df = CheckList_df[CheckList_df['PRNumber'] <= labeled_PRNumber]

    # 修正確認コメントをまとめたファイルの読み込み
    AcieveCommentsFilePath = '/Users/haruto-k/research/select_list/AcieveCommentsFile.json'
    with open(AcieveCommentsFilePath, 'r') as AchieveCommentsFile_json:
        AchieveCommentsFile = json.load(AchieveCommentsFile_json)

    # 修正確認コメントと出現回数，信頼度を保存するためのリストを初期化
    ConfidenceAchieve_list = []

    # 修正確認コメントの出現回数と信頼度の計算
    for i in range(AchieveCommentsFile):

        # 出現回数と修正確認コメント回数の初期化
        SumAchieveIncluded = 0
        SumTrueAchieve = 0

        # チェックリストを一行ずつ確認
        for CheckListRow in LabeledCheckList_df:

            # 開発者のコメントではないことの確認
            if CheckListRow['owner'] != CheckListRow['author']:

                # 修正確認コメントが含まれているか確認
                if AchieveCommentsFile[i] in CheckListRow['comment']:

                    SumAchieveIncluded += 1

                    # 修正確認コメントが含まれているコメントが本当に修正確認コメントなのか確認
                    if CheckListRow['修正確認'] == 1:

                        SumTrueAchieve += 1

        # 修正確認コメントと出現回数，信頼度を保存
        ConfidenceAchieve_list.append({
            '修正確認コメント': AchieveCommentsFile[i],
            '出現回数': SumAchieveIncluded,
            '信頼度': SumTrueAchieve / SumAchieveIncluded
        })

    # 出現回数，信頼度の順に降順にソート
    ConfidenceAchieve_list.sort_values(['出現回数', '信頼度'], ascending=False)

    # 信頼度などを保存したリストをデータフレーム型に変換
    ConfidenceAchieve_df = pd.DataFrame(ConfidenceAchieve_list)
    
    return ConfidenceAchieve_df

def main():

    # 信頼度などを計算する関数の呼び出し
    ConfidenceAchieve_df = ConfidenceCaluculation()

    # 結果の出力
    FilePath_write = '/Users/haruto-k/research/select_list/adjust_comments/ConfidenceAchieveComments.csv'
    ConfidenceAchieve_df.csv(FilePath_write, index=False)

if __name__ == "__main__":
    main()