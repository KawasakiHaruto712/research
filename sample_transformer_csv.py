import csv
import json
import os

filepath_read = '/Users/haruto-k/desktop/629766_summarizelist.json'
with open(filepath_read, 'r') as f:
    json_data = json.load(f)
status_list = json_data['status_list']
review_list = json_data['review_list']

file_name = os.path.splitext(os.path.basename(filepath_read))[0]
filepath_write = '/Users/haruto-k/desktop/629766_summarizelist.csv'
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
        for review in review_list:
            # status_listの書き込み
            status_row = {key: status_list[key] if key in status_list else '' for key in fieldnames}

            # review_listの書き込み
            review_row = {key: review[key] if key in review else '' for key in fieldnames}
            combined_row = {key: review_row[key] if review_row[key] else status_row[key] for key in fieldnames}
            writer.writerow(combined_row)
    else:
        status_row = {key: status_list[key] if key in status_list else '' for key in fieldnames}
        writer.writerow(status_row)