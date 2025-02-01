import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import datetime, timedelta

# PRと日付を軸とした全て空（nan）の二次元データフレームを取得
def make_request_dataframe(pr_and_request_data):

    # 研究対象のPRをリストに格納（重複なし）
    pr_data = pr_and_request_data.drop_duplicates("PRID")
    pr_id = pr_data["PRID"].to_list()

    # 研究対象期間を日毎にリストに格納
    start_date = datetime(2011, 7, 25)
    end_date = datetime(2023, 5, 18)
    target_date = []
    date_i = start_date
    while date_i <= end_date:
        target_date.append(date_i)
        date_i += timedelta(days=1)
    
    # PRと日付を軸とした全て空（nan）の二次元データフレームを作成
    request_data_list = [[np.nan for j in range(len(target_date))] for i in range(len(pr_id))]
    request_data = pd.DataFrame(data=request_data_list, index=pr_id, columns=target_date)
    
    return request_data

# PRの開放期間に修正要求の欄に0を挿入する
def check_pr_open(pr_and_request_data, request_data):

    # PR毎に開放時を確認し，0を挿入
    pr_data = pr_and_request_data.drop_duplicates("PRID")
    for _, pr_data_row in pr_data.iterrows():
        create_time = datetime.strptime(pr_data_row["CreateTime"], "%Y/%m/%d %H:%M:%S")
        merge_time = datetime.strptime(pr_data_row["MergeTime"], "%Y/%m/%d %H:%M:%S")
        request_data.loc[pr_data_row["PRID"], create_time:merge_time] = 0
    
    return request_data

# 修正要求が開放されている数を加算    
def check_request_open(pr_and_request_data, request_data):

    # 修正要求毎に開放時を確認し，カウント
    for _, request_data_row in pr_and_request_data.iterrows():
        request_time = datetime.strptime(request_data_row["RequestTime"], "%Y/%m/%d %H:%M:%S")
        achieve_time = datetime.strptime(request_data_row["AchieveTime"], "%Y/%m/%d %H:%M:%S")
        request_data.loc[request_data_row["PRID"], request_time:achieve_time] += 1
    
    return request_data

def main():
    # PR（レビュー票）と修正要求の開放時間を記したcscファイルを読み込む
    # プロジェクト毎にしたいならここのパスを変更
    pr_and_request_data = pd.read_csv("../../select_list/TaskTransition/CompositeTask.csv")
    
    # PRと日付を軸とした全て空（nan）の二次元データフレームを取得
    request_data = make_request_dataframe(pr_and_request_data)

    # PRの開放時に修正要求数の欄に0を挿入する
    request_data = check_pr_open(pr_and_request_data, request_data)

    # 修正要求が開放されている数を加算
    request_data = check_request_open(pr_and_request_data, request_data)

    # PR毎の要求数の推移のグラフを保存
    request_data.index.name = 'project'  # インデックスに名前をつける
    request_data = request_data.reset_index()  # インデックスを列に変換
    request_data_melted = request_data.melt(id_vars=["project"], var_name="days")
    request_data_melted["days"] = pd.to_datetime(request_data_melted["days"])

    # グラフ作成に用いたデータを保存
    request_data_melted = request_data_melted.dropna(subset=['value'])
    request_data_melted.to_csv("../../select_list/TaskTransition/request_per_pr.csv", index=False, encoding="utf_8_sig")

    # グラフの描画と保存
    line_plot = sns.relplot(x="days", y="value", data=request_data_melted, kind="line", errorbar="sd")
    line_plot.figure.set_size_inches(7.5, 4.5)

    # x軸を1年毎に区切る
    ax = line_plot.axes[0][0]  # グラフのaxesオブジェクトを取得
    ax.xaxis.set_major_locator(mdates.YearLocator())  # 1年毎にメモリを設定
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # 年のみ表示
    # y軸を0.5刻みに設定
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))  # 1刻みにメモリを設定

    line_plot.set_axis_labels("Date", "Number of Review Requests per PR", labelpad=10)
    figure = line_plot.figure
    figure.savefig("../../select_list/TaskTransition/request_per_pr.pdf")

if __name__ == "__main__":
    main()