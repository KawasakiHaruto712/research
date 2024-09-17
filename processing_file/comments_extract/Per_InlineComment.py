import json
import pandas as pd
import re
from glob import glob

# 定数の設定
CheckListPath = "../../select_list/checkList/alradyStart/checkList.csv"
CheckPRNumPath = "../../select_list/labeled_PRNumber.txt"
InlineReqPath = "../../select_list/checkList/InlineReq.csv"

# インラインコメント数と修正要求の割合を算出
def Cal_InlineReq(CheckList):

    # インラインコメント数と修正要求数を格納する変数の初期化
    inline = Req = 0

    # チェックリストの行毎に処理を行う
    for _, row in CheckList.iterrows():

        # コメントにインラインコメントが含まれている場合をカウント
        CommentsForm = r'.*\(([0-9]+)\s*inline\s*comments?\)'
        InlineForm = r'.*\(([0-9]+)\s*comments?\)'
        if re.search(CommentsForm, row["comment"]) or re.search(InlineForm, row["comment"]):
            inline += 1

            # 修正要求が含まれている場合をカウント
            if row["修正要求"] == 1:
                Req += 1

    # インラインコメント数と修正要求の割合を変数に格納
    InlineReq = [{
        "インラインコメント数": inline,
        "修正要求の割合": Req / inline
    }]

    # インラインコメント数と修正要求の割合をデータフレーム型で返す
    return pd.DataFrame(InlineReq)

# メイン処理
def main():

    # チェックリストの読み込み
    CheckList = pd.read_csv(CheckListPath, header=0)
    with open(CheckPRNumPath) as PRNum_txt:
        textline = PRNum_txt.readlines()
    CheckPRNum = float(textline[0])
    CheckList = CheckList[CheckList["PRNumber"] <= CheckPRNum]

    # インラインコメント数と修正要求の割合を出力
    InlineReq_df = Cal_InlineReq(CheckList)
    InlineReq_df.to_csv(InlineReqPath, index=False, encoding='utf_8_sig')

if __name__ == "__main__":
    main()