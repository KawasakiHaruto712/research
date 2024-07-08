import pandas as pd
import json
from tqdm import tqdm

# 修正確認コメントの信頼度の計算
def ConfidenceCaluculation():

    # チェックリストの読み込み
    Read_CheckList_path = '/Users/haruto-k/research/select_list/checkList/alradyStart/checkList.csv'
    CheckList_df = pd.read_csv(Read_CheckList_path, header=0)

    # ラベル付けされているPRだけを対象とする
    labeled_PRNumber_path = '/Users/haruto-k/research/select_list/labeled_PRNumber.txt'
    with open(labeled_PRNumber_path) as LabeledPRNumber_txt:
        textLine = LabeledPRNumber_txt.readlines()
    labeled_PRNumber = float(textLine[0])
    LabeledCheckList_df = CheckList_df[CheckList_df['PRNumber'] <= labeled_PRNumber]

    # 修正確認コメントをまとめたファイルの読み込み
    AcieveCommentsFile_path = '/Users/haruto-k/research/select_list/AchieveCommentsFile.json'
    with open(AcieveCommentsFile_path, 'r') as AchieveCommentsFile_json:
        AchieveCommentsFile = json.load(AchieveCommentsFile_json)

    # 修正確認コメントと出現回数，信頼度を保存するためのリストを初期化
    ConfidenceAchieve_list = []

    # 修正確認コメントの出現回数と信頼度の計算
    for AchieveComment in tqdm(AchieveCommentsFile):

        # 出現回数と修正確認コメント回数の初期化
        SumAchieveIncluded = 0
        SumTrueAchieve = 0

        # チェックリストを一行ずつ確認
        for _, CheckListRow in LabeledCheckList_df.iterrows():

            # 開発者のコメントではないことの確認
            if CheckListRow['owner'] != CheckListRow['author']:

                # 修正確認コメントが含まれているか確認
                if str(AchieveComment['AchieveComments']).lower() in CheckListRow['comment'].lower():

                    # 出現回数のカウント
                    SumAchieveIncluded += 1

                    # 修正確認コメントが含まれているコメントが本当に修正確認コメントなのか確認
                    if CheckListRow['修正確認'] == 1:

                        # 修正確認コメント回数のカウント
                        SumTrueAchieve += 1

        # 修正確認コメントと出現回数，信頼度を保存
        ConfidenceAchieve_list.append({
            '修正確認コメント': AchieveComment['AchieveComments'],
            '出現回数': SumAchieveIncluded,
            '信頼度': SumTrueAchieve / SumAchieveIncluded
        })

    # 出現回数，信頼度の順に降順にソート
    SortedConfidenceAchieve_list = sorted(ConfidenceAchieve_list, key=lambda x:(x['出現回数'], x['信頼度']), reverse=True)

    # ソートしたリストをデータフレーム型に変換
    SortedConfidenceAchieve_df = pd.DataFrame(SortedConfidenceAchieve_list)
    
    return SortedConfidenceAchieve_df

def main():

    # 信頼度などを計算する関数の呼び出し
    ConfidenceAchieve_df = ConfidenceCaluculation()

    # 結果の出力
    WriteResult_path = '/Users/haruto-k/research/select_list/adjust_comments/ConfidenceAchieveComments.csv'
    ConfidenceAchieve_df.to_csv(WriteResult_path, index=False, encoding='utf_8_sig')

if __name__ == "__main__":
    main()