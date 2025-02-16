import json
import pandas as pd
from datetime import datetime
from glob import glob
from tqdm import tqdm
from pathlib import Path
from statistics import mean, median

def main():

    # 修正要求数とクローズ時間を抽出
    all_data = []
    for request_path in tqdm(glob("../../select_list/RequestAssociate/*/*.csv")):

        # PR（レビュー票）に含まれる修正要求数を抽出
        with open(request_path, 'r', encoding='utf-8_sig') as req_f:
            header = req_f.readline().strip()
        request_sum = 0
        if header:
            request_data = pd.read_csv(request_path)
            request_sum = request_data.shape[0]

        # PRのクローズにかかった時間を抽出
        request_pathlib = Path(request_path)
        with open(f"../../project/formatFile/{request_pathlib.parent.name}/{request_pathlib.stem}.json") as pr_f:
            pr_data = json.load(pr_f)
        pr_create_time = datetime.strptime(pr_data["created"][:-3], "%Y-%m-%d %H:%M:%S.%f")
        pr_merge_time = datetime.strptime(pr_data["updated"][:-3], "%Y-%m-%d %H:%M:%S.%f")
        open_minutes = (pr_merge_time - pr_create_time).total_seconds() / 60 # 開放時間（分）
    
        # 修正要求数とクローズ時間を保存
        all_data.append((request_sum, open_minutes))
    all_data_df = pd.DataFrame(all_data)
    all_data_df.to_csv("../../select_list/closetime_and_requestnum.csv", index=False, encoding="utf_8_sig")

    # 同一修正要求数を持つデータをグループ化
    grouped_data = {}
    for sum, time in all_data:
        if sum not in grouped_data:
            grouped_data[sum] = []
        grouped_data[sum].append(time)
    
    # 結果を保存
    result = []
    for sum in sorted(grouped_data.keys()):
        open_minutes_list = grouped_data[sum]
        result.append({
            "修正要求数": sum,
            "レビュー票数": len(open_minutes_list),
            "レビュー票のクローズ時間の平均値": mean(open_minutes_list),
            "レビュー票のクローズ時間の中央値": median(open_minutes_list)
        })
    result_df = pd.DataFrame(result)
    result_df.to_csv("../../select_list/time_diff_num_requests.csv", index=False, encoding="utf_8_sig")

if __name__ == "__main__":
    main()