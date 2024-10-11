import pandas as pd
from tqdm import tqdm

# ラベルの出現割合を計算する関数
def CalculationAchievePercentage():

    # レビューコメント分類済みファイルの読み込み
    CheckList_ReadPath = '/Users/haruto-k/research/select_list/checkList/alradyStart/checkList.csv'
    CheckList_df = pd.read_csv(CheckList_ReadPath, header=0)

    # ラベル付けされているPRだけを対象とする
    LabeledPRNumber_ReadPath = '/Users/haruto-k/research/select_list/labeled_PRNumber.txt'
    with open(LabeledPRNumber_ReadPath) as LabeledPRNumber_txt:
        textLine = LabeledPRNumber_txt.readlines()
    LabeledPRNumber = float(textLine[0])
    LabeledCheckList_df = CheckList_df[CheckList_df['PRNumber'] <= LabeledPRNumber]

    # 出現回数と出現しなかった回数を保存する用の変数の初期化
    AchieveNumber = 0
    WeakPositive = 0
    StrongPositive = 0
    OtherAchieve = 0
    NotAppear = 0

    # 分類済みチェックリストの分だけループ処理
    for _, CheckListRow in LabeledCheckList_df.iterrows():

        # 修正確認として分類がされていない場合は対象外
        if CheckListRow['修正確認'] != 1:
            continue

        # 修正確認コメント数のカウント
        AchieveNumber += 1

        # 修正確認ラベルがどちらも付いている
        if (('Code-Review+1' in CheckListRow['comment'] and 'Code-Review+2' in CheckListRow['comment']) or
            ('Looks good to me, but someone else must approve' in CheckListRow['comment'] and 'Looks good to me, approved' in CheckListRow['comment'])):
            WeakPositive += 1
            StrongPositive += 1
            print(str(CheckListRow['commentsNumber']) + '行目のコメントはCode-Review+1とCode-Review+2が同時に付けられています．')
            continue

        # Code-Review+1がコメントに含まれている
        if ('Code-Review+1' in CheckListRow['comment'] or 
            'Looks good to me, but someone else must approve' in CheckListRow['comment'] or 
            'Works for me' in CheckListRow['comment'] or 
            'Sanity review passed' in CheckListRow['comment']):
            WeakPositive += 1
            continue

        # Code-Review+2がコメントに含まれている
        if ('Code-Review+2' in CheckListRow['comment'] or 
            'Looks good to me, approved' in CheckListRow['comment']):
            StrongPositive += 1
            continue

        # 修正確認コメントの信頼度が高いコメントが含まれている
        if ('looks good'in CheckListRow['comment'].lower() or 
            'lgtm'in CheckListRow['comment'].lower() or 
            'looks ok'in CheckListRow['comment'].lower()):
            OtherAchieve += 1
            continue

        # 修正確認ラベルが付けられていないコメントをカウント
        NotAppear += 1

    # それぞれの出現回数をリストに保存
    AchievePercentageResult_list = [{
        '修正確認コメント数': AchieveNumber,
        'Code-Review+1(旧ラベルも含む)出現回数': WeakPositive,
        'Code-Review+2(旧ラベルも含む)出現回数': StrongPositive,
        '信頼度の高かったコメントの出現回数': OtherAchieve,
        'ラベルのついていない出現回数': NotAppear,
        '修正確認コメントのうちラベルの付いたコメントの出現割合': (WeakPositive + StrongPositive) / AchieveNumber,
        '信頼度の高かったコメント修正確認コメントのうちラベルの付いたコメントの出現割合': (WeakPositive + StrongPositive + OtherAchieve) / AchieveNumber
    }]

    # 出現回数などを保存したリストをデータフレーム型に変換
    AchievePercentageResult_df = pd.DataFrame(AchievePercentageResult_list)

    # 出現回数の結果を返す
    return AchievePercentageResult_df

# メイン処理
def main():

    # ラベルの出現割合を計算する関数の呼び出し
    AchievePercentageResult_df = CalculationAchievePercentage()

    # 修正確認として分類したコメントの内，ラベルの出現割合結果の出力
    AchievePercentageResult_WritePath = '/Users/haruto-k/research/select_list/achieve_include_ratio.csv'
    AchievePercentageResult_df.to_csv(AchievePercentageResult_WritePath, index=False, encoding='utf_8_sig')

if __name__ == "__main__":
    main()