from glob import glob
from tqdm import tqdm
import pandas as pd
import os
import json

# JSONファイルを読み込む
def combined_data(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)

    # status_listをDataFrameに変換
    status_details = pd.DataFrame([data['status_list']])

    # link_commentsとnotlink_commentsが含まれるか確認し、DataFrameを作成する
    link_comments = pd.DataFrame(data['review_list'].get('link_comments', []))
    notlink_comments = pd.DataFrame(data['review_list'].get('notlink_comments', []))

    # DataFrameを結合する（存在しない場合は空の列を作成）
    if link_comments.empty:
        link_comments = pd.DataFrame(columns=['request_comment', 'achieve_comment'])
    if notlink_comments.empty:
        notlink_comments = pd.DataFrame(columns=['notlink_comment'])

    # status_detailsをlink_commentsとnotlink_commentsの各行に繰り返して追加
    combined_df = pd.concat([link_comments, notlink_comments], axis=1)
    status_repeated = pd.concat([status_details] * len(combined_df), ignore_index=True)
    final_df = pd.concat([status_repeated, combined_df.reset_index(drop=True)], axis=1)

    return final_df

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