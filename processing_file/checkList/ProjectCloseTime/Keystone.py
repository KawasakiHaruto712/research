import json
import matplotlib.pyplot as plt
import pandas as pd
import statistics
from datetime import datetime
from glob import glob
from matplotlib.font_manager import FontProperties
from pathlib import Path
from tqdm import tqdm

# PR情報とPR/修正要求の開放数を記述したファイルパス
AllPRDataPath = "/Users/haruto-k/research/project/formatFile/list_4/*.json"
NumOpenPath = "/Users/haruto-k/research/select_list/TaskTransition/ChangeNumOpen/Keystone/NumOpen.csv"

# 散布図を記述するパス
PlotFigurePath = "/Users/haruto-k/research/select_list/TaskTransition/ChangeNumOpen/Keystone/PlotFigure"

# 修正要求の開放数によるクローズ時間の変化を散布図で描画
def DrowCloseTimeDiagram():
    print("<Keystone>")
    AllNumOpen = pd.read_csv(NumOpenPath)

    # PRの開放数の第一四分位数から第三四分位数までを算出
    PRNumOpenQ1, PRNumOpenQ2, PRNumOpenQ3 = statistics.quantiles(AllNumOpen["PRNum"])

    # PRの開放数毎に4つの区間に分割し，それぞれの区間内で修正要求数とクローズ時間を格納する配列を初期化
    ReqNumOpenlist = [[] for _ in range(4)]
    OpenMinuteslist = [[] for _ in range(4)]

    # PR毎に修正要求の開放数とクローズ時間の分布を算出
    for PRPath in tqdm(glob(AllPRDataPath)):
        with open(PRPath, "r") as PR_f:
            PRData = json.load(PR_f)

        # PRの作成時間と開放時間を表す変数の初期化
        PRCreateTime = datetime.strptime(PRData["created"][:-3], "%Y-%m-%d %H:%M:%S.%f")
        PRMergeTime = datetime.strptime(PRData["updated"][:-3], "%Y-%m-%d %H:%M:%S.%f")
        OpenMinutes = (PRMergeTime - PRCreateTime).total_seconds() / 60 # 開放時間(分)

        # PRと修正要求の開放数を表す変数の初期化
        PRNumOpen = ReqNumOpen = 0

        # PRの作成時のPRと修正要求の開放数を算出
        for Date_i, NumOpen in AllNumOpen.iterrows():
            NumOpenTime = datetime.strptime(NumOpen["Date"], "%Y/%m/%d")
            if PRCreateTime.date() == NumOpenTime.date():
                PRNumOpen = NumOpen["PRNum"]
                ReqNumOpen = NumOpen["ReqNum"]
                break
            elif Date_i == len(AllNumOpen) - 1:
                print(f"PRID:{Path(PRPath).stem}はPRの開放日と一致する日付が開放数を記載したファイルに存在しないです")

        # PRの開放数の区間毎に修正要求数とクローズ時間の格納
        if PRNumOpen < PRNumOpenQ1:
            ReqNumOpenlist[0].append(ReqNumOpen)
            OpenMinuteslist[0].append(OpenMinutes)
        elif PRNumOpen < PRNumOpenQ2:
            ReqNumOpenlist[1].append(ReqNumOpen)
            OpenMinuteslist[1].append(OpenMinutes)
        elif PRNumOpen < PRNumOpenQ3:
            ReqNumOpenlist[2].append(ReqNumOpen)
            OpenMinuteslist[2].append(OpenMinutes)
        else:
            ReqNumOpenlist[3].append(ReqNumOpen)
            OpenMinuteslist[3].append(OpenMinutes)

    # 散布図の描画
    Section = ["First", "Second", "Third", "Fource"]
    for PRNumSection_i in range(4):

        # 散布図の作成
        plt.figure(figsize=(8, 6))
        plt.scatter(ReqNumOpenlist[PRNumSection_i], OpenMinuteslist[PRNumSection_i], color='blue', alpha=0.5)

        # #散布図の設定
        plt.title("Number of requests opened and time to close code review tickets")
        plt.xlabel("Number of requests opened (items)")
        plt.ylabel("Code review tickets closing time (min)")

        # PDFとして保存
        plt.savefig(PlotFigurePath + "/" + Section[PRNumSection_i] + ".pdf")
        plt.close()
    
        # 散布図に描画する修正要求の数とクローズ時間をcsvに保存
        PlotData = []
        for ReqNumOpen_i in range(len(ReqNumOpenlist[PRNumSection_i])):
            PlotData.append({
                "修正要求開放数": ReqNumOpenlist[PRNumSection_i][ReqNumOpen_i],
                "レビュー票クローズ時間": OpenMinuteslist[PRNumSection_i][ReqNumOpen_i]
            })
        PlotData_df = pd.DataFrame(PlotData)
        PlotData_df.to_csv((PlotFigurePath + "/PlotData/" + Section[PRNumSection_i] + ".csv"), index=False, encoding="utf_8_sig")

def main():
    DrowCloseTimeDiagram()

if __name__ == "__main__":
    main()