from glob import glob
from tqdm import tqdm
import pandas as pd
import os
import json

def combined_data(filepath):
    # JSONファイルを読み込む
    with open(filepath, 'r') as file:
        data = json.load(file)

    # 'status_list'データをDataFrameに変換
    status_data = data['status_list']
    status_df = pd.DataFrame([status_data])

    # 'review_list'データをDataFrameに変換
    review_data = data['review_list']
    review_df = pd.DataFrame(review_data)

    # status_dfに'review_list'データを追加するための準備：全ての行で同じstatusデータを使用
    status_expanded_df = pd.concat([status_df]*len(review_df), ignore_index=True)

    # statusデータとreviewデータを結合
    combined_df = pd.concat([status_expanded_df, review_df], axis=1)

    return combined_df

def main():
    file_categories = ['list_1', 'list_2', 'list_3', 'list_4', 'list_5', 'list_6', 'list_7']
    for category in tqdm(file_categories):
        filepath_read_pattern = os.path.join('/Users/haruto-k/research/select_list/adjust_comments/json', category, '*.json')
        filepath_list = glob(filepath_read_pattern)
        for filepath in filepath_list:
            combined_df = combined_data(filepath)
            file_name = os.path.splitext(os.path.basename(filepath))[0]
            filepath_write = os.path.join('/Users/haruto-k/research/select_list/adjust_comments/csv', category, file_name + '.csv')
            # CSVファイルとして出力
            combined_df.to_csv(filepath_write, index=False)

if __name__ == "__main__":
    main()
