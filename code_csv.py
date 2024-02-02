from glob import glob
from tqdm import tqdm
import csv
import json
import os


file_cate = ['list_1', 'list_1 2', 'list_1 3', 'list_1 4', 'list_1 5', 'list_1 6', 'list_1 7']
for i in tqdm(range(len(file_cate))):
    filepath_read = '/Users/haruto-k/research/select_list/json_file/' + file_cate[i] +'/*.json'
    filepath_list = glob(filepath_read)
    for filepath in tqdm(filepath_list):
        # JSONファイルのロード
        with open(filepath, 'r') as f:
            json_data = json.load(f)
        status_list = json_data['status_list']
        review_list = json_data['review_list']

        file_name = os.path.splitext(os.path.basename(filepath))[0]
        filepath_write = './select_list/csv_file/' + file_cate[i] + '/' + file_name + '.csv'
        # CSVファイルに書き込み
        with open(filepath_write, 'w', newline = '') as f:
            # ヘッダーの合成
            if review_list:
                fieldnames = list(status_list.keys()) + list(review_list[0].keys())
            else:
                review_list_key = ["review_number", "revision", "reviewer",
                                   "Code-Review_label", "Verified_label",
                                   "Review-Priority_label", "Workflow-label",
                                   "comment"]
                fieldnames = list(status_list.keys()) + review_list_key
                # print(file_cate[i], file_name) # レビューがされていないプロジェクトの出力
            writer = csv.DictWriter(f, fieldnames=fieldnames, doublequote=True, quoting=csv.QUOTE_ALL)

            writer.writeheader()

            if review_list:
                row_number = 0
                for review in review_list:
                    # status_listの書き込み
                    status_row = {key: status_list[key] if key in status_list else '' for key in fieldnames}

                    # review_listの書き込み
                    review_row = {key: review[key] if key in review else '' for key in fieldnames}
                    if row_number == 0:
                        combined_row = {key: review_row[key] if review_row[key] else status_row[key] for key in fieldnames}
                    else:
                        combined_row = {**status_row, **review_row}
                    writer.writerow(combined_row)
                    row_number += 1
            else:
                status_row = {key: status_list[key] if key in status_list else '' for key in fieldnames}
                writer.writerow(status_row)

'''
# テスト用の1ファイル実行コマンド
# JSONファイルのロード
with open('./select_list/json_file/list_1 6/20758_list.json', 'r') as f:
    json_data = json.load(f)

status_list = json_data['status_list']
review_list = json_data['review_list']

# CSVファイルに書き込み
with open('./select_list/csv_file/list_1 6/20758_list.csv', 'w', newline='') as f:
    # ヘッダーの合成
    if review_list:
        fieldnames = list(status_list.keys()) + list(review_list[0].keys())
    else:
        review_list_key = ["review_number", "revision", "reviewer",
                            "Code-Review_label", "Verified_label",
                            "Review-Priority_label", "Workflow-label",
                            "comment"]
        fieldnames = list(status_list.keys()) + review_list_key
    writer = csv.DictWriter(f, fieldnames=fieldnames, doublequote=True, quoting=csv.QUOTE_ALL)

    writer.writeheader()

    if review_list:
        row_number = 0
        for review in review_list:
            # status_listの書き込み
            status_row = {key: status_list[key] if key in status_list else '' for key in fieldnames}

            # review_listの書き込み
            review_row = {key: review[key] if key in review else '' for key in fieldnames}
            if row_number == 0:
                combined_row = {key: review_row[key] if review_row[key] else status_row[key] for key in fieldnames}
            else:
                combined_row = {**status_row, **review_row}
            row_number += 1
            writer.writerow(combined_row)
    else:
        status_row = {key: status_list[key] if key in status_list else '' for key in fieldnames}
        writer.writerow(status_row)
'''